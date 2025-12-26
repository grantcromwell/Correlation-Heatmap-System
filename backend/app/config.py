"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    alpha_vantage_api_key: str
    finnhub_api_key: str

    # Database
    database_url: str
    sync_database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Temporal
    temporal_address: str = "localhost:7233"
    temporal_namespace: str = "default"

    # Frontend URL (for CORS)
    frontend_url: str = "http://localhost:5173"

    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    # Rate Limiting
    alpha_vantage_rate_limit: int = 5  # calls per minute
    finnhub_rate_limit: int = 60  # calls per minute

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()

