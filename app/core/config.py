from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sustainability Tracking Platform"

    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "sustainability_db"

    # Security
    SECRET_KEY: str  # Mandatory: No default ensures production safety
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GEMINI_API_KEY: str | None = None

    # Email Configuration
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"
    RESEND_API_KEY: str | None = None

    # CORS — Fix #16: moved from main.py hardcode to settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    # Pydantic v2 Configuration Management
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # Safely skips extra fields in .env without crashing
        case_sensitive=True      # Enforces clean, uppercase standards
    )


# Singleton instance to import throughout the app
settings = Settings()