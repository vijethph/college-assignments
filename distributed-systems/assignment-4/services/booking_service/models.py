"""Booking Service Pydantic Models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BookingCreate(BaseModel):
    """Model for creating a new booking."""

    user_id: int
    hotel_id: int
    room_id: int
    check_in: str
    check_out: str


class BookingResponse(BaseModel):
    """Model for booking API responses."""

    id: int
    user_id: int
    hotel_id: int
    room_id: int
    check_in: str
    check_out: str
    total_price: float
    status: str
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class BookingCancellation(BaseModel):
    """Model for booking cancellation requests."""

    reason: Optional[str] = None


class HealthResponse(BaseModel):
    """Model for health check responses."""

    status: str
    service: str
