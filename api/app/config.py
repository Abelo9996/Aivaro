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
