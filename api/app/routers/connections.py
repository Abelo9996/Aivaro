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
        # New integrations
        "hubspot", "salesforce", "shopify", "quickbooks",
        "github", "discord", "asana", "trello",
        "zendesk", "intercom", "linear", "jira",
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
            url=f"{FRONTEND_URL}/app/connections?error=invalid_state"
        )
    
    user_id = state_data["user_id"]
    redirect_uri = f"{API_URL}/api/connections/{provider}/callback"
    
    # Exchange code for tokens
    tokens = await exchange_code_for_tokens(provider, code, redirect_uri)
    if not tokens:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/app/connections?error=token_exchange_failed"
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
        url=f"{FRONTEND_URL}/app/connections?success={provider}"
    )


@router.post("/", response_model=ConnectionResponse)
async def create_connection(
    connection_data: ConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a connection (for demo mode or API key-based integrations)."""
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
    """Test if a connection is still valid."""
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
    
    # For real connections, try to get user info
    if connection.credentials and connection.credentials.get("access_token"):
        user_info = await get_user_info(
            connection.type, 
            connection.credentials["access_token"]
        )
        if user_info:
            return {"success": True, "message": "Connection is valid", "user": user_info}
        else:
            return {"success": False, "message": "Connection token may be expired"}
    
    return {"success": True, "message": "Connection test successful"}
