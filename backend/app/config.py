"""
Application Configuration
Environment variables loaded from .env file
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://brinesim:brinesim@localhost:5432/brinesim"
    DATABASE_URL_SYNC: str = "postgresql://brinesim:brinesim@localhost:5432/brinesim"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Kakao OAuth
    KAKAO_CLIENT_ID: str = ""
    KAKAO_REDIRECT_URI: str = "http://localhost:8000/api/auth/kakao/callback"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # App
    APP_NAME: str = "Brine Spray Simulation Engine"
    APP_VERSION: str = "0.2.0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
