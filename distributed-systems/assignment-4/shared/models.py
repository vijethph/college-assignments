from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, field_validator


class BookingStatus(str, Enum):
    """
    Booking status enumeration.

    Defines the possible states of a hotel booking throughout its lifecycle.
    """

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class HotelBase(BaseModel):
    """
    Base hotel model with common attributes.

    Contains the core hotel information shared across creation and response models.
    """

    name: str = Field(..., description="Name of the hotel", example="Grand Hotel")
    location: str = Field(
        ...,
        description="City or area where hotel is located",
        example="Dublin, Ireland",
    )
    description: str = Field(
        ...,
        description="Detailed description of the hotel",
        example="Luxury hotel in city center",
    )
    amenities: List[str] = Field(
        ...,
        description="List of hotel amenities",
        example=["WiFi", "Pool", "Gym", "Restaurant"],
    )
    rating: float = Field(
        ..., description="Hotel rating out of 5", example=4.5, ge=0, le=5
    )


class HotelCreate(HotelBase):
    """
    Hotel creation request model.

    Used for creating new hotels with all required attributes.
    """

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Grand Hotel",
                "location": "Dublin, Ireland",
                "description": "Luxury hotel in city center",
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
                "rating": 4.5,
            }
        }
    }


class HotelResponse(HotelBase):
    """
    Hotel response model.

    Represents a hotel entity with its unique identifier and all attributes.
    """

    id: int = Field(..., description="Unique hotel identifier", example=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Grand Hotel",
                "location": "Dublin, Ireland",
                "description": "Luxury hotel in city center",
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
                "rating": 4.5,
            }
        }
    }


class RoomBase(BaseModel):
    """
    Base room model with common attributes.

    Contains core room information including type, pricing, and availability.
    """

    hotel_id: int = Field(
        ..., description="ID of the hotel this room belongs to", example=1
    )
    room_type: str = Field(..., description="Type of room", example="Deluxe")
    price_per_night: float = Field(
        ..., description="Price per night in EUR", example=150.0, gt=0
    )
    capacity: int = Field(..., description="Maximum number of guests", example=2, gt=0)
    available_count: int = Field(
        ..., description="Number of available rooms of this type", example=10, ge=0
    )


class RoomCreate(RoomBase):
    """
    Room creation request model.

    Used for adding new room types to a hotel.
    """

    model_config = {
        "json_schema_extra": {
            "example": {
                "hotel_id": 1,
                "room_type": "Deluxe",
                "price_per_night": 150.0,
                "capacity": 2,
                "available_count": 10,
            }
        }
    }


class RoomResponse(RoomBase):
    """
    Room response model.

    Represents a room entity with its unique identifier and all attributes.
    """

    id: int = Field(..., description="Unique room identifier", example=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "hotel_id": 1,
                "room_type": "Deluxe",
                "price_per_night": 150.0,
                "capacity": 2,
                "available_count": 10,
            }
        }
    }


class RoomAvailabilityCheck(BaseModel):
    """
    Room availability check request model.

    Used to verify room availability for specific dates and room type.
    """

    check_in: date = Field(..., description="Check-in date", example="2024-12-01")
    check_out: date = Field(..., description="Check-out date", example="2024-12-05")
    room_type: Optional[str] = Field(
        None, description="Type of room to check", example="Deluxe"
    )

    @field_validator("check_out")
    @classmethod
    def check_out_after_check_in(cls, v, info):
        """
        Validate that check-out date is after check-in date.

        :param v: Check-out date value
        :type v: date
        :param info: Validation context information
        :return: Validated check-out date
        :rtype: date
        :raises ValueError: If check-out is not after check-in
        """
        if "check_in" in info.data and v <= info.data["check_in"]:
            raise ValueError("check_out must be after check_in")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "check_in": "2024-12-01",
                "check_out": "2024-12-05",
                "room_type": "Deluxe",
            }
        }
    }


class RoomAvailabilityUpdate(BaseModel):
    """
    Room availability update model.

    Used to increase or decrease the available count for a specific room.
    """

    room_id: int = Field(..., description="ID of the room to update", example=1)
    change: int = Field(
        ...,
        description="Change in availability (positive to add, negative to subtract)",
        example=-1,
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "room_id": 1,
                "change": -1,
            }
        }
    }


class UserBase(BaseModel):
    """
    Base user model with common attributes.

    Contains core user information shared across different user models.
    """

    email: EmailStr = Field(
        ..., description="User email address", example="user@example.com"
    )
    name: str = Field(..., description="Full name of the user", example="John Doe")
    phone: str = Field(..., description="Contact phone number", example="+353123456789")


class UserCreate(UserBase):
    """
    User registration request model.

    Used for creating new user accounts with password.
    """

    password: str = Field(
        ..., description="User password", min_length=6, example="securepass123"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "phone": "+353123456789",
                "password": "securepass123",
            }
        }
    }


class UserResponse(UserBase):
    """
    User response model.

    Represents a user entity with identifier and creation timestamp.
    """

    id: int = Field(..., description="Unique user identifier", example=1)
    created_at: datetime = Field(
        ..., description="Account creation timestamp", example="2024-01-15T10:30:00"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "John Doe",
                "phone": "+353123456789",
                "created_at": "2024-01-15T10:30:00",
            }
        }
    }


class UserUpdate(BaseModel):
    """
    User profile update model.

    Allows partial updates to user profile information.
    """

    name: Optional[str] = Field(
        None, description="Updated full name", example="Jane Doe"
    )
    phone: Optional[str] = Field(
        None, description="Updated phone number", example="+353987654321"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Jane Doe",
                "phone": "+353987654321",
            }
        }
    }


class UserLogin(BaseModel):
    """
    User login request model.

    Contains credentials for user authentication.
    """

    email: EmailStr = Field(
        ..., description="User email address", example="user@example.com"
    )
    password: str = Field(..., description="User password", example="securepass123")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepass123",
            }
        }
    }


class TokenResponse(BaseModel):
    """
    JWT token response model.

    Returned after successful authentication with access token.
    """

    access_token: str = Field(
        ...,
        description="JWT access token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    token_type: str = Field(..., description="Token type", example="bearer")
    user_id: int = Field(..., description="Authenticated user ID", example=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjQwOTk1MjAwfQ.signature",
                "token_type": "bearer",
                "user_id": 1,
            }
        }
    }


class BookingCreate(BaseModel):
    """
    Booking creation request model.

    Used for creating new hotel room bookings with dates and room selection.
    """

    user_id: int = Field(
        ..., description="ID of the user making the booking", example=1
    )
    hotel_id: int = Field(..., description="ID of the hotel", example=1)
    room_id: int = Field(..., description="ID of the room being booked", example=1)
    check_in: date = Field(..., description="Check-in date", example="2024-12-01")
    check_out: date = Field(..., description="Check-out date", example="2024-12-05")

    @field_validator("check_out")
    @classmethod
    def check_out_after_check_in(cls, v, info):
        """
        Validate that check-out date is after check-in date.

        :param v: Check-out date value
        :type v: date
        :param info: Validation context information
        :return: Validated check-out date
        :rtype: date
        :raises ValueError: If check-out is not after check-in
        """
        if "check_in" in info.data and v <= info.data["check_in"]:
            raise ValueError("check_out must be after check_in")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "hotel_id": 1,
                "room_id": 1,
                "check_in": "2024-12-01",
                "check_out": "2024-12-05",
            }
        }
    }


class BookingResponse(BaseModel):
    """
    Booking response model.

    Represents a complete booking entity with all details and status.
    """

    id: int = Field(..., description="Unique booking identifier", example=1)
    user_id: int = Field(
        ..., description="ID of the user who made the booking", example=1
    )
    hotel_id: int = Field(..., description="ID of the booked hotel", example=1)
    room_id: int = Field(..., description="ID of the booked room", example=1)
    check_in: date = Field(..., description="Check-in date", example="2024-12-01")
    check_out: date = Field(..., description="Check-out date", example="2024-12-05")
    total_price: float = Field(
        ..., description="Total booking price in EUR", example=600.0
    )
    status: BookingStatus = Field(
        ..., description="Current booking status", example="confirmed"
    )
    created_at: datetime = Field(
        ..., description="Booking creation timestamp", example="2024-11-15T14:30:00"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 1,
                "hotel_id": 1,
                "room_id": 1,
                "check_in": "2024-12-01",
                "check_out": "2024-12-05",
                "total_price": 600.0,
                "status": "confirmed",
                "created_at": "2024-11-15T14:30:00",
            }
        }
    }


class BookingCancellation(BaseModel):
    """
    Booking cancellation request model.

    Contains optional cancellation reason for booking cancellations.
    """

    reason: Optional[str] = Field(
        None, description="Reason for cancellation", example="Change of plans"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "reason": "Change of plans",
            }
        }
    }


class HealthResponse(BaseModel):
    """
    Health check response model.

    Indicates the operational status of a service.
    """

    status: str = Field(..., description="Service health status", example="healthy")
    service: str = Field(..., description="Service name", example="api-gateway")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "service": "api-gateway",
            }
        }
    }
