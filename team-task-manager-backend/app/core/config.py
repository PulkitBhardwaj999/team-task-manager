"""
Application configuration and settings
"""
import os
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Team Task Manager"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/team_task_manager"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-super-secret-key-change-in-production-12345678901234567890"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Environment
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Rate limiting (simple in-memory limiter)
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        """Accept common environment labels as boolean debug values."""
        if isinstance(value, bool):
            return value
        if value is None:
            return True

        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes", "on", "debug", "development", "dev"}:
            return True
        if normalized in {"false", "0", "no", "off", "release", "production", "prod"}:
            return False

        return value
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
