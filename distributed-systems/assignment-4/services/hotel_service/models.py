"""Hotel Service Pydantic Models."""

from typing import Optional

from pydantic import BaseModel, Field


class HotelBase(BaseModel):
    """Base hotel model with common fields."""

    name: str
    location: str
    description: Optional[str] = None
    amenities: Optional[str] = None
    rating: float = Field(default=0.0, ge=0.0, le=5.0)


class HotelCreate(HotelBase):
    """Model for creating a new hotel."""

    pass


class HotelResponse(HotelBase):
    """Model for hotel API responses."""

    id: int

    class Config:
        """Pydantic config."""

        from_attributes = True


class RoomBase(BaseModel):
    """Base room model with common fields."""

    hotel_id: int
    room_type: str
    price_per_night: float = Field(gt=0)
    capacity: int = Field(gt=0)
    available_count: int = Field(ge=0)


class RoomCreate(RoomBase):
    """Model for creating a new room."""

    pass


class RoomResponse(RoomBase):
    """Model for room API responses."""

    id: int

    class Config:
        """Pydantic config."""

        from_attributes = True


class RoomAvailabilityCheck(BaseModel):
    """Model for checking room availability."""

    check_in: str
    check_out: str
    room_type: Optional[str] = None


class RoomAvailabilityUpdate(BaseModel):
    """Model for updating room availability."""

    room_id: int
    change: int


class HealthResponse(BaseModel):
    """Model for health check responses."""

    status: str
    service: str
