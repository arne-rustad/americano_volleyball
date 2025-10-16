"""Application configuration and settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase configuration
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # API configuration
    api_title: str = "Americano Volleyball API"
    api_version: str = "0.1.0"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

