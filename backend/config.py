"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Telegram
    telegram_bot_token: str

    # LLM (Gemini)
    google_ai_api_key: str

    # TikTok Scraping
    supadata_api_key: str

    # Infrastructure
    redis_url: str = "redis://localhost:6379"
    database_url: str = "sqlite:///./tikodea.db"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
