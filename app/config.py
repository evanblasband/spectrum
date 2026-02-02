"""Application settings loaded from environment."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # App
    app_name: str = "Spectrum"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # API
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # AI Providers
    default_ai_provider: str = "groq"

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = "llama-3.3-70b-versatile"

    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    claude_model: str = "claude-3-5-sonnet-20241022"

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4-turbo-preview"

    # News APIs
    newsapi_key: Optional[str] = Field(default=None, alias="NEWSAPI_KEY")
    gnews_api_key: Optional[str] = Field(default=None, alias="GNEWS_API_KEY")

    # Cache
    cache_backend: str = "memory"  # "memory" or "redis"
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    cache_max_size: int = 500

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Scraping
    scraper_timeout_seconds: int = 30
    scraper_user_agent: str = "Spectrum/1.0 (News Analysis Bot)"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
