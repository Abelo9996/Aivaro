from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Default to SQLite for easy local development (no Docker needed)
    database_url: str = "sqlite:///./aivaro.db"
    secret_key: str = "your-super-secret-key-change-in-production"
    access_token_expire_minutes: int = 1440
    openai_api_key: str | None = None
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
