"""API Gateway Configuration."""

import os

SERVICE_NAME = "api-gateway"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

HOTEL_SERVICE_URL = os.getenv("HOTEL_SERVICE_URL", "http://localhost:8001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://localhost:8003")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
