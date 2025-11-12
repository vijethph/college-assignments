"""Booking Service Configuration."""

import os


class Config:
    """Configuration class for booking service settings."""

    SERVICE_NAME = "booking-service"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8003"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./booking_service.db")
    HOTEL_SERVICE_URL = os.getenv("HOTEL_SERVICE_URL", "http://localhost:8001")
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
