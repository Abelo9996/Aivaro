"""
OAuth Service for handling third-party integrations.
Supports Google, Slack, and other OAuth2 providers.
"""
import httpx
from typing import Optional
from urllib.parse import urlencode
from app.config import get_settings

settings = get_settings()

# OAuth Configuration - Using settings from .env
OAUTH_CONFIGS = {
    "google": {
        "client_id": settings.google_client_id or "",
        "client_secret": settings.google_client_secret or "",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar",  # Full calendar access (read + write)
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly",  # For searching/listing spreadsheets
        ],
    },
    "slack": {
        "client_id": settings.slack_client_id or "",
        "client_secret": settings.slack_client_secret or "",
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scopes": ["channels:read", "groups:read", "chat:write", "chat:write.public", "users:read"],
    },
    "notion": {
        "client_id": settings.notion_client_id or "",
        "client_secret": settings.notion_client_secret or "",
        "auth_url": "https://api.notion.com/v1/oauth/authorize",
        "token_url": "https://api.notion.com/v1/oauth/token",
        "scopes": [],
    },
    "stripe": {
        "client_id": settings.stripe_client_id or "",
        "client_secret": settings.stripe_client_secret or "",
        "auth_url": "https://connect.stripe.com/oauth/authorize",
        "token_url": "https://connect.stripe.com/oauth/token",
        "scopes": ["read_write"],
    },
    "calendly": {
        "client_id": settings.calendly_client_id or "",
        "client_secret": settings.calendly_client_secret or "",
        "auth_url": "https://auth.calendly.com/oauth/authorize",
        "token_url": "https://auth.calendly.com/oauth/token",
        "scopes": [],
    },
    "airtable": {
        "client_id": settings.airtable_client_id or "",
        "client_secret": settings.airtable_client_secret or "",
        "auth_url": "https://airtable.com/oauth2/v1/authorize",
        "token_url": "https://airtable.com/oauth2/v1/token",
        "scopes": [
            "data.records:read",
            "data.records:write",
            "schema.bases:read",
        ],
    },
    "mailchimp": {
        "client_id": settings.mailchimp_client_id or "",
        "client_secret": settings.mailchimp_client_secret or "",
        "auth_url": "https://login.mailchimp.com/oauth2/authorize",
        "token_url": "https://login.mailchimp.com/oauth2/token",
        "scopes": [],
    },
    "hubspot": {
        "client_id": settings.hubspot_client_id or "",
        "client_secret": settings.hubspot_client_secret or "",
        "auth_url": "https://app.hubspot.com/oauth/authorize",
        "token_url": "https://api.hubapi.com/oauth/v1/token",
        "scopes": ["crm.objects.contacts.read", "crm.objects.contacts.write", "crm.objects.deals.read", "crm.objects.deals.write"],
    },
    "salesforce": {
        "client_id": settings.salesforce_client_id or "",
        "client_secret": settings.salesforce_client_secret or "",
        "auth_url": "https://login.salesforce.com/services/oauth2/authorize",
        "token_url": "https://login.salesforce.com/services/oauth2/token",
        "scopes": ["api", "refresh_token"],
    },
    "shopify": {
        "client_id": settings.shopify_client_id or "",
        "client_secret": settings.shopify_client_secret or "",
        "auth_url": "https://{shop}.myshopify.com/admin/oauth/authorize",
        "token_url": "https://{shop}.myshopify.com/admin/oauth/access_token",
        "scopes": ["read_products", "write_products", "read_orders", "write_orders"],
    },
    "quickbooks": {
        "client_id": settings.quickbooks_client_id or "",
        "client_secret": settings.quickbooks_client_secret or "",
        "auth_url": "https://appcenter.intuit.com/connect/oauth2",
        "token_url": "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
        "scopes": ["com.intuit.quickbooks.accounting"],
    },
    "github": {
        "client_id": settings.github_client_id or "",
        "client_secret": settings.github_client_secret or "",
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scopes": ["repo", "user:email"],
    },
    "discord": {
        "client_id": settings.discord_client_id or "",
        "client_secret": settings.discord_client_secret or "",
        "auth_url": "https://discord.com/api/oauth2/authorize",
        "token_url": "https://discord.com/api/oauth2/token",
        "scopes": ["identify", "guilds", "bot"],
    },
    "asana": {
        "client_id": settings.asana_client_id or "",
        "client_secret": settings.asana_client_secret or "",
        "auth_url": "https://app.asana.com/-/oauth_authorize",
        "token_url": "https://app.asana.com/-/oauth_token",
        "scopes": ["default"],
    },
    "zendesk": {
        "client_id": settings.zendesk_client_id or "",
        "client_secret": settings.zendesk_client_secret or "",
        "auth_url": "https://{subdomain}.zendesk.com/oauth/authorizations/new",
        "token_url": "https://{subdomain}.zendesk.com/oauth/tokens",
        "scopes": ["read", "write"],
    },
    "intercom": {
        "client_id": settings.intercom_client_id or "",
        "client_secret": settings.intercom_client_secret or "",
        "auth_url": "https://app.intercom.com/oauth",
        "token_url": "https://api.intercom.io/auth/eagle/token",
        "scopes": [],
    },
    "linear": {
        "client_id": settings.linear_client_id or "",
        "client_secret": settings.linear_client_secret or "",
        "auth_url": "https://linear.app/oauth/authorize",
        "token_url": "https://api.linear.app/oauth/token",
        "scopes": ["read", "write", "issues:create"],
    },
    "jira": {
        "client_id": settings.jira_client_id or "",
        "client_secret": settings.jira_client_secret or "",
        "auth_url": "https://auth.atlassian.com/authorize",
        "token_url": "https://auth.atlassian.com/oauth/token",
        "scopes": ["read:jira-work", "write:jira-work", "read:jira-user"],
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
            # For Slack bot tokens, use auth.test instead of users.identity
            response = await client.get(
                "https://slack.com/api/auth.test",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return {"name": data.get("user", "Slack User"), "id": data.get("user_id"), "team": data.get("team")}
    
    return None


def is_provider_configured(provider: str) -> bool:
    """Check if a provider has OAuth credentials configured."""
    config = get_oauth_config(provider)
    return bool(config and config.get("client_id") and config.get("client_secret"))
