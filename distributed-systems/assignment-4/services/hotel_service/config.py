"""Hotel Service Configuration."""

import os


class Config:
    """Configuration class for hotel service settings."""

    SERVICE_NAME = "hotel-service"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hotel_service.db")
