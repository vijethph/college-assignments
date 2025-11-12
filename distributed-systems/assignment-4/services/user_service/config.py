"""User Service Configuration."""

import os


class Config:
    """Configuration class for user service settings."""

    SERVICE_NAME = "user-service"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8002"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./user_service.db")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_MINUTES = 60
