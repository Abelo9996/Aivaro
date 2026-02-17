from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Database configuration
    # Local development: sqlite:///./aivaro.db
    # Production PostgreSQL: postgresql://user:password@host:5432/dbname
    # Neon: postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
    # Supabase: postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
    # Railway: postgresql://postgres:password@xxx.railway.app:5432/railway
    database_url: str = "sqlite:///./aivaro.db"
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    access_token_expire_minutes: int = 1440
    
    # OpenAI
    openai_api_key: str | None = None
    
    # Google OAuth
    google_client_id: str | None = None
    google_client_secret: str | None = None
    
    # Slack OAuth
    slack_client_id: str | None = None
    slack_client_secret: str | None = None
    
    # Notion OAuth
    notion_client_id: str | None = None
    notion_client_secret: str | None = None
    
    # Stripe OAuth
    stripe_client_id: str | None = None
    stripe_client_secret: str | None = None
    
    # Calendly OAuth
    calendly_client_id: str | None = None
    calendly_client_secret: str | None = None
    
    # Airtable OAuth
    airtable_client_id: str | None = None
    airtable_client_secret: str | None = None
    
    # Mailchimp OAuth
    mailchimp_client_id: str | None = None
    mailchimp_client_secret: str | None = None
    
    # Twilio (uses Account SID and Auth Token, not OAuth)
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None
    
    # HubSpot OAuth
    hubspot_client_id: str | None = None
    hubspot_client_secret: str | None = None
    
    # Salesforce OAuth
    salesforce_client_id: str | None = None
    salesforce_client_secret: str | None = None
    
    # Shopify OAuth
    shopify_client_id: str | None = None
    shopify_client_secret: str | None = None
    
    # QuickBooks OAuth
    quickbooks_client_id: str | None = None
    quickbooks_client_secret: str | None = None
    
    # GitHub OAuth
    github_client_id: str | None = None
    github_client_secret: str | None = None
    
    # Discord OAuth
    discord_client_id: str | None = None
    discord_client_secret: str | None = None
    
    # Asana OAuth
    asana_client_id: str | None = None
    asana_client_secret: str | None = None
    
    # Trello (uses API key)
    trello_api_key: str | None = None
    trello_api_token: str | None = None
    
    # Zendesk OAuth
    zendesk_client_id: str | None = None
    zendesk_client_secret: str | None = None
    zendesk_subdomain: str | None = None
    
    # Intercom OAuth
    intercom_client_id: str | None = None
    intercom_client_secret: str | None = None
    
    # Linear OAuth
    linear_client_id: str | None = None
    linear_client_secret: str | None = None
    
    # Jira OAuth
    jira_client_id: str | None = None
    jira_client_secret: str | None = None
    
    # App URLs (for OAuth redirects)
    api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Environment
    environment: str = "development"  # development, staging, production
    
    # Timezone - default to Pacific Time if not specified
    default_timezone: str = "America/Los_Angeles"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Module-level settings instance for convenience
settings = get_settings()
