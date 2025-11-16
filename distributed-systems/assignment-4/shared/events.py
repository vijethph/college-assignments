"""Event schemas for async messaging.

Defines Pydantic models for events published to the message broker.
These schemas ensure type safety and validation for inter-service
communication in the hotel booking system.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class BookingCreatedEvent(BaseModel):
    """Event published when booking is created.

    This event is published by the booking service after successfully
    creating a new booking. Consumed by user service for notifications.

    :param event_type: Event type identifier
    :type event_type: Literal["booking.created"]
    :param booking_id: Unique booking identifier
    :type booking_id: int
    :param user_id: User who made the booking
    :type user_id: int
    :param hotel_id: Hotel identifier
    :type hotel_id: int
    :param room_id: Room identifier
    :type room_id: int
    :param check_in: Check-in date in ISO format
    :type check_in: str
    :param check_out: Check-out date in ISO format
    :type check_out: str
    :param total_price: Total booking price
    :type total_price: float
    :param timestamp: Event timestamp in ISO format
    :type timestamp: str
    """

    event_type: Literal["booking.created"] = "booking.created"
    booking_id: int
    user_id: int
    hotel_id: int
    room_id: int
    check_in: str
    check_out: str
    total_price: float
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class BookingCancelledEvent(BaseModel):
    """Event published when booking is cancelled.

    This event is published by the booking service after cancelling a
    booking. Consumed by hotel service to restore room availability.

    :param event_type: Event type identifier
    :type event_type: Literal["booking.cancelled"]
    :param booking_id: Cancelled booking identifier
    :type booking_id: int
    :param hotel_id: Hotel identifier
    :type hotel_id: int
    :param room_id: Room identifier for availability restoration
    :type room_id: int
    :param reason: Cancellation reason
    :type reason: str
    :param timestamp: Event timestamp in ISO format
    :type timestamp: str
    """

    event_type: Literal["booking.cancelled"] = "booking.cancelled"
    booking_id: int
    hotel_id: int
    room_id: int
    reason: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
