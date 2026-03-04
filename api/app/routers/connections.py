from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
import secrets

from app.database import get_db
from app.models import Connection, User
from app.schemas import ConnectionCreate, ConnectionResponse
from app.routers.auth import get_current_user
from app.services.oauth_service import (
    get_authorization_url,
    exchange_code_for_tokens,
    get_user_info,
    is_provider_configured,
)

router = APIRouter()

# In-memory state storage (use Redis in production)
oauth_states = {}

# Frontend URL for redirects - use settings for flexibility
from app.config import get_settings
settings = get_settings()
FRONTEND_URL = settings.frontend_url
API_URL = settings.api_url


@router.get("/", response_model=List[ConnectionResponse])
async def list_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    connections = db.query(Connection).filter(Connection.user_id == current_user.id).all()
    return [ConnectionResponse.model_validate(c) for c in connections]


@router.get("/providers")
async def list_providers():
    """List available OAuth providers and their configuration status."""
    providers = [
        # Core integrations
        "google", "slack", "notion", "stripe", 
        # Scheduling & CRM
        "calendly", "airtable", "mailchimp", "twilio",
        # CRM & Sales
        "hubspot", "salesforce", "shopify", "quickbooks",
        # Developer Tools
        "github", "discord", "asana", "trello",
        "zendesk", "intercom", "linear", "jira",
        # SMS Marketing
        "textedly",
        # Website & Domain Providers
        "godaddy", "wix", "squarespace", "webflow",
        # No-Code Platforms
        "base44", "bubble", "zapier",
        # Analytics & Traffic
        "google_analytics", "cloudflare", "plausible", "hotjar",
        # Social Media
        "facebook", "instagram", "twitter", "linkedin", "tiktok",
    ]
    return [
        {
            "type": p,
            "configured": is_provider_configured(p),
            "name": p.title(),
        }
        for p in providers
    ]


@router.get("/{provider}/authorize")
async def authorize_provider(
    provider: str,
    current_user: User = Depends(get_current_user),
):
    """Start OAuth flow for a provider."""
    if not is_provider_configured(provider):
        # For demo/unconfigured providers, return a demo mode response
        return {
            "demo_mode": True,
            "message": f"{provider.title()} OAuth is not configured. Set {provider.upper()}_CLIENT_ID and {provider.upper()}_CLIENT_SECRET environment variables.",
            "provider": provider,
        }
    
    # Generate state token
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "user_id": current_user.id,
        "provider": provider,
    }
    
    redirect_uri = f"{API_URL}/api/connections/{provider}/callback"
    auth_url = get_authorization_url(provider, redirect_uri, state)
    
    if not auth_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate authorization URL for {provider}"
        )
    
    return {"authorization_url": auth_url}


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """Handle OAuth callback from provider."""
    # Verify state
    state_data = oauth_states.pop(state, None)
    if not state_data or state_data["provider"] != provider:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/oauth-callback?error=invalid_state"
        )
    
    user_id = state_data["user_id"]
    redirect_uri = f"{API_URL}/api/connections/{provider}/callback"
    
    # Exchange code for tokens
    tokens = await exchange_code_for_tokens(provider, code, redirect_uri)
    if not tokens:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/oauth-callback?error=token_exchange_failed"
        )
    
    # Get user info from provider
    access_token = tokens.get("access_token")
    user_info = await get_user_info(provider, access_token) if access_token else None
    
    # Check if connection already exists
    existing = db.query(Connection).filter(
        Connection.user_id == user_id,
        Connection.type == provider,
    ).first()
    
    if existing:
        # Update existing connection
        existing.credentials = {
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in"),
            "token_type": tokens.get("token_type"),
            "user_info": user_info,
        }
        existing.is_connected = True
        if user_info:
            existing.name = user_info.get("name") or user_info.get("email") or provider.title()
    else:
        # Create new connection
        connection = Connection(
            user_id=user_id,
            name=user_info.get("name") or user_info.get("email") or provider.title() if user_info else provider.title(),
            type=provider,
            credentials={
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "expires_in": tokens.get("expires_in"),
                "token_type": tokens.get("token_type"),
                "user_info": user_info,
            },
            is_connected=True,
        )
        db.add(connection)
    
    db.commit()
    
    return RedirectResponse(
        url=f"{FRONTEND_URL}/oauth-callback?success={provider}"
    )


@router.post("/", response_model=ConnectionResponse)
async def create_connection(
    connection_data: ConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a connection (for demo mode or API key-based integrations)."""
    # Strip whitespace from all credential values on save
    creds = connection_data.credentials
    if creds and isinstance(creds, dict):
        creds = {k: v.strip() if isinstance(v, str) else v for k, v in creds.items()}
        connection_data.credentials = creds
    
    # Check if connection already exists
    existing = db.query(Connection).filter(
        Connection.user_id == current_user.id,
        Connection.type == connection_data.type,
    ).first()
    
    if existing:
        # Update existing
        existing.name = connection_data.name
        existing.credentials = connection_data.credentials
        existing.is_connected = True
        db.commit()
        db.refresh(existing)
        return ConnectionResponse.model_validate(existing)
    
    connection = Connection(
        user_id=current_user.id,
        name=connection_data.name,
        type=connection_data.type,
        credentials=connection_data.credentials,
        is_connected=True
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    
    return ConnectionResponse.model_validate(connection)


@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    connection = db.query(Connection).filter(
        Connection.id == connection_id,
        Connection.user_id == current_user.id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    db.delete(connection)
    db.commit()
    
    return {"message": "Connection deleted"}


@router.post("/{connection_id}/test")
async def test_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test if a connection is still valid by making a lightweight API call."""
    connection = db.query(Connection).filter(
        Connection.id == connection_id,
        Connection.user_id == current_user.id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    # For demo connections, always return success
    if connection.credentials and connection.credentials.get("demo"):
        return {"success": True, "message": "Demo connection is active"}
    
    creds = connection.credentials or {}
    ctype = connection.type
    
    import httpx
    
    # ---- Provider-specific verification ----
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            
            # === OAuth providers (access_token based) ===
            if ctype == "google" and creds.get("access_token"):
                async def _test_google_token(token: str):
                    return await client.get(
                        "https://www.googleapis.com/oauth2/v1/userinfo",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                
                resp = await _test_google_token(creds["access_token"])
                
                # If 401, try refreshing the token first
                if resp.status_code == 401 and creds.get("refresh_token"):
                    import os
                    refresh_resp = await client.post("https://oauth2.googleapis.com/token", data={
                        "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
                        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
                        "refresh_token": creds["refresh_token"],
                        "grant_type": "refresh_token",
                    })
                    if refresh_resp.status_code == 200:
                        new_token = refresh_resp.json().get("access_token")
                        if new_token:
                            # Persist the refreshed token
                            creds["access_token"] = new_token
                            connection.credentials = creds
                            db.commit()
                            resp = await _test_google_token(new_token)
                
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "Google connected", "user": {"email": data.get("email", ""), "name": data.get("name", "")}}
                elif resp.status_code == 401:
                    return {"success": False, "message": "Google token expired and refresh failed. Try reconnecting."}
                return {"success": False, "message": f"Google verification failed (HTTP {resp.status_code})"}
            
            if ctype == "slack" and creds.get("access_token"):
                resp = await client.get(
                    "https://slack.com/api/auth.test",
                    headers={"Authorization": f"Bearer {creds['access_token']}"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("ok"):
                        return {"success": True, "message": "Slack connected", "user": {"team": data.get("team", ""), "user": data.get("user", "")}}
                    return {"success": False, "message": f"Slack token invalid: {data.get('error', 'unknown')}"}
                return {"success": False, "message": f"Slack verification failed (HTTP {resp.status_code})"}
            
            if ctype == "notion" and creds.get("access_token"):
                resp = await client.get(
                    "https://api.notion.com/v1/users/me",
                    headers={"Authorization": f"Bearer {creds['access_token']}", "Notion-Version": "2022-06-28"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "Notion connected", "user": {"name": data.get("name", "")}}
                return {"success": False, "message": f"Notion token invalid (HTTP {resp.status_code})"}
            
            if ctype == "calendly" and creds.get("access_token"):
                resp = await client.get(
                    "https://api.calendly.com/users/me",
                    headers={"Authorization": f"Bearer {creds['access_token']}"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    resource = data.get("resource", {})
                    return {"success": True, "message": "Calendly connected", "user": {"name": resource.get("name", ""), "email": resource.get("email", "")}}
                return {"success": False, "message": f"Calendly token invalid (HTTP {resp.status_code}). Try reconnecting."}

            # === API key providers ===
            if ctype == "brevo" and creds.get("api_key"):
                key = creds["api_key"]
                import logging
                logging.getLogger("connections").info(
                    f"[Brevo test] key length={len(key)}, prefix={key[:20]}..., suffix=...{key[-10:]}, "
                    f"has_whitespace={key != key.strip()}, has_newline={chr(10) in key or chr(13) in key}, "
                    f"repr_start={repr(key[:25])}"
                )
                resp = await client.get(
                    "https://api.brevo.com/v3/account",
                    headers={"api-key": key.strip(), "Accept": "application/json"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "Brevo API key is valid", "user": {"email": data.get("email", ""), "company": data.get("companyName", "")}}
                logging.getLogger("connections").warning(
                    f"[Brevo test] FAILED: status={resp.status_code}, response={resp.text[:300]}, "
                    f"request_headers={dict(resp.request.headers)}"
                )
                return {"success": False, "message": f"Brevo API key invalid (HTTP {resp.status_code}). Response: {resp.text[:200]}"}

            if ctype == "stripe" and creds.get("api_key"):
                resp = await client.get(
                    "https://api.stripe.com/v1/balance",
                    headers={"Authorization": f"Bearer {creds['api_key']}"}
                )
                if resp.status_code == 200:
                    return {"success": True, "message": "Stripe API key is valid"}
                return {"success": False, "message": f"Stripe API key invalid (HTTP {resp.status_code})"}

            if ctype == "sendgrid" and creds.get("api_key"):
                resp = await client.get(
                    "https://api.sendgrid.com/v3/user/profile",
                    headers={"Authorization": f"Bearer {creds['api_key']}"}
                )
                if resp.status_code == 200:
                    return {"success": True, "message": "SendGrid API key is valid"}
                return {"success": False, "message": f"SendGrid API key invalid (HTTP {resp.status_code})"}

            if ctype == "airtable" and creds.get("api_key"):
                resp = await client.get(
                    "https://api.airtable.com/v0/meta/whoami",
                    headers={"Authorization": f"Bearer {creds['api_key']}"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "Airtable token is valid", "user": {"id": data.get("id", "")}}
                return {"success": False, "message": f"Airtable token invalid (HTTP {resp.status_code})"}

            if ctype == "mailchimp" and creds.get("api_key"):
                key = creds["api_key"]
                dc = key.split("-")[-1] if "-" in key else "us1"
                resp = await client.get(
                    f"https://{dc}.api.mailchimp.com/3.0/",
                    headers={"Authorization": f"Bearer {key}"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "Mailchimp API key is valid", "user": {"name": data.get("account_name", "")}}
                return {"success": False, "message": f"Mailchimp API key invalid (HTTP {resp.status_code})"}

            if ctype == "hubspot" and creds.get("access_token"):
                resp = await client.get(
                    "https://api.hubapi.com/crm/v3/objects/contacts?limit=1",
                    headers={"Authorization": f"Bearer {creds['access_token']}"}
                )
                if resp.status_code == 200:
                    return {"success": True, "message": "HubSpot token is valid"}
                return {"success": False, "message": f"HubSpot token invalid (HTTP {resp.status_code})"}

            if ctype == "github" and creds.get("access_token"):
                resp = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {creds['access_token']}", "Accept": "application/vnd.github+json"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "GitHub token is valid", "user": {"login": data.get("login", ""), "name": data.get("name", "")}}
                return {"success": False, "message": f"GitHub token invalid (HTTP {resp.status_code})"}

            if ctype == "discord" and creds.get("bot_token"):
                resp = await client.get(
                    "https://discord.com/api/v10/users/@me",
                    headers={"Authorization": f"Bot {creds['bot_token']}"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "Discord bot token is valid", "user": {"username": data.get("username", "")}}
                return {"success": False, "message": f"Discord bot token invalid (HTTP {resp.status_code})"}

            if ctype == "linear" and creds.get("api_key"):
                resp = await client.post(
                    "https://api.linear.app/graphql",
                    headers={"Authorization": creds["api_key"], "Content-Type": "application/json"},
                    json={"query": "{ viewer { id name } }"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    viewer = data.get("data", {}).get("viewer", {})
                    return {"success": True, "message": "Linear API key is valid", "user": {"name": viewer.get("name", "")}}
                return {"success": False, "message": f"Linear API key invalid (HTTP {resp.status_code})"}

            if ctype == "monday" and creds.get("api_key"):
                resp = await client.post(
                    "https://api.monday.com/v2",
                    headers={"Authorization": creds["api_key"], "Content-Type": "application/json"},
                    json={"query": "{ me { name email } }"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    me = data.get("data", {}).get("me", {})
                    return {"success": True, "message": "Monday.com API key is valid", "user": {"name": me.get("name", ""), "email": me.get("email", "")}}
                return {"success": False, "message": f"Monday.com API key invalid (HTTP {resp.status_code})"}

            if ctype == "jira" and creds.get("domain") and creds.get("email") and creds.get("api_token"):
                import base64
                auth = base64.b64encode(f"{creds['email']}:{creds['api_token']}".encode()).decode()
                domain = creds["domain"].rstrip("/")
                if not domain.startswith("http"):
                    domain = f"https://{domain}"
                resp = await client.get(
                    f"{domain}/rest/api/3/myself",
                    headers={"Authorization": f"Basic {auth}", "Accept": "application/json"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "Jira credentials are valid", "user": {"name": data.get("displayName", ""), "email": data.get("emailAddress", "")}}
                return {"success": False, "message": f"Jira credentials invalid (HTTP {resp.status_code})"}

            if ctype == "shopify" and creds.get("shop_domain") and creds.get("access_token"):
                domain = creds["shop_domain"].rstrip("/")
                if not domain.startswith("http"):
                    domain = f"https://{domain}"
                resp = await client.get(
                    f"{domain}/admin/api/2024-01/shop.json",
                    headers={"X-Shopify-Access-Token": creds["access_token"]}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    shop = data.get("shop", {})
                    return {"success": True, "message": "Shopify token is valid", "user": {"name": shop.get("name", ""), "domain": shop.get("domain", "")}}
                return {"success": False, "message": f"Shopify token invalid (HTTP {resp.status_code})"}

            if ctype == "whatsapp" and creds.get("access_token") and creds.get("phone_number_id"):
                resp = await client.get(
                    f"https://graph.facebook.com/v18.0/{creds['phone_number_id']}",
                    headers={"Authorization": f"Bearer {creds['access_token']}"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "WhatsApp credentials are valid", "user": {"phone": data.get("display_phone_number", "")}}
                return {"success": False, "message": f"WhatsApp credentials invalid (HTTP {resp.status_code})"}

            if ctype == "twilio" and creds.get("account_sid") and creds.get("auth_token"):
                resp = await client.get(
                    f"https://api.twilio.com/2010-04-01/Accounts/{creds['account_sid']}.json",
                    auth=(creds["account_sid"], creds["auth_token"])
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"success": True, "message": "Twilio credentials are valid", "user": {"name": data.get("friendly_name", "")}}
                return {"success": False, "message": f"Twilio credentials invalid (HTTP {resp.status_code})"}

    except httpx.TimeoutException:
        return {"success": False, "message": f"Verification timed out — {ctype} API may be slow. Try again."}
    except Exception as e:
        return {"success": False, "message": f"Verification error: {str(e)}"}
    
    return {"success": True, "message": "Connection stored (no verification available for this provider)"}
