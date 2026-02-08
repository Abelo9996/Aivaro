"""
OAuth Service for handling third-party integrations.
Supports Google, Slack, and other OAuth2 providers.
"""
import os
import httpx
from typing import Optional
from urllib.parse import urlencode

# OAuth Configuration - Set these environment variables
OAUTH_CONFIGS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    },
    "slack": {
        "client_id": os.getenv("SLACK_CLIENT_ID", ""),
        "client_secret": os.getenv("SLACK_CLIENT_SECRET", ""),
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scopes": ["channels:read", "chat:write", "users:read"],
    },
    "notion": {
        "client_id": os.getenv("NOTION_CLIENT_ID", ""),
        "client_secret": os.getenv("NOTION_CLIENT_SECRET", ""),
        "auth_url": "https://api.notion.com/v1/oauth/authorize",
        "token_url": "https://api.notion.com/v1/oauth/token",
        "scopes": [],
    },
    "stripe": {
        "client_id": os.getenv("STRIPE_CLIENT_ID", ""),
        "client_secret": os.getenv("STRIPE_CLIENT_SECRET", ""),
        "auth_url": "https://connect.stripe.com/oauth/authorize",
        "token_url": "https://connect.stripe.com/oauth/token",
        "scopes": ["read_write"],
    },
}


def get_oauth_config(provider: str) -> Optional[dict]:
    """Get OAuth configuration for a provider."""
    return OAUTH_CONFIGS.get(provider)


def get_authorization_url(provider: str, redirect_uri: str, state: str) -> Optional[str]:
    """Generate OAuth authorization URL for a provider."""
    config = get_oauth_config(provider)
    if not config or not config["client_id"]:
        return None
    
    params = {
        "client_id": config["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    
    if config["scopes"]:
        params["scope"] = " ".join(config["scopes"])
    
    return f"{config['auth_url']}?{urlencode(params)}"


async def exchange_code_for_tokens(provider: str, code: str, redirect_uri: str) -> Optional[dict]:
    """Exchange authorization code for access and refresh tokens."""
    config = get_oauth_config(provider)
    if not config:
        return None
    
    async with httpx.AsyncClient() as client:
        if provider == "notion":
            # Notion uses Basic Auth
            import base64
            credentials = base64.b64encode(
                f"{config['client_id']}:{config['client_secret']}".encode()
            ).decode()
            headers = {"Authorization": f"Basic {credentials}"}
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            }
        else:
            headers = {}
            data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
        
        response = await client.post(
            config["token_url"],
            data=data,
            headers=headers,
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"OAuth token exchange failed: {response.text}")
            return None


async def refresh_access_token(provider: str, refresh_token: str) -> Optional[dict]:
    """Refresh an expired access token."""
    config = get_oauth_config(provider)
    if not config:
        return None
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            config["token_url"],
            data={
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        
        if response.status_code == 200:
            return response.json()
        return None


async def get_user_info(provider: str, access_token: str) -> Optional[dict]:
    """Get user info from the OAuth provider."""
    config = get_oauth_config(provider)
    if not config:
        return None
    
    async with httpx.AsyncClient() as client:
        if provider == "google":
            response = await client.get(
                config["userinfo_url"],
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 200:
                return response.json()
        elif provider == "slack":
            response = await client.get(
                "https://slack.com/api/users.identity",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return data.get("user")
    
    return None


def is_provider_configured(provider: str) -> bool:
    """Check if a provider has OAuth credentials configured."""
    config = get_oauth_config(provider)
    return bool(config and config.get("client_id") and config.get("client_secret"))
