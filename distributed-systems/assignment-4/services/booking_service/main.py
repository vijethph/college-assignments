"""
Booking Service.

This module provides API endpoints for managing hotel room bookings. It handles
booking creation, retrieval, cancellation, and coordinates with hotel and user
services for validation and room availability management.
"""

import sys
from contextlib import asynccontextmanager
from datetime import datetime as dt
from pathlib import Path
from typing import List

import requests
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import Config
from database import Booking, get_db, init_db
from models import BookingCancellation, BookingCreate, BookingResponse, HealthResponse
from shared.logging_config import configure_logging, get_logger
from shared.utils import log_request, retry_on_failure


configure_logging(Config.SERVICE_NAME)
logger = get_logger()

BOOKING_NOT_FOUND = "Booking not found"
REQUEST_TIMEOUT = 5


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("service_starting", port=Config.SERVICE_PORT)
    init_db()
    yield
    logger.info("service_stopping")


app = FastAPI(title="Booking Service", lifespan=lifespan)


@retry_on_failure(max_retries=3, delay=0.5)
@log_request("user-service", "/users/{user_id}", "GET")
def verify_user_exists(user_id: int) -> bool:
    """
    Verify if a user exists in the user service.

    :param user_id: The user identifier
    :type user_id: int
    :return: True if user exists, False otherwise
    :rtype: bool
    """
    response = requests.get(
        f"{Config.USER_SERVICE_URL}/users/{user_id}", timeout=REQUEST_TIMEOUT
    )
    if response.status_code == 404:
        return False
    response.raise_for_status()
    return True


@retry_on_failure(max_retries=3, delay=0.5)
@log_request("hotel-service", "/hotels/{hotel_id}/rooms/check-availability", "POST")
def check_room_availability(hotel_id: int, room_id: int, check_in: str, check_out: str):
    """
    Check if a specific room is available for given dates.

    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :param room_id: The room identifier
    :type room_id: int
    :param check_in: Check-in date in ISO format
    :type check_in: str
    :param check_out: Check-out date in ISO format
    :type check_out: str
    :return: Room data if available, None otherwise
    :rtype: dict or None
    """
    response = requests.post(
        f"{Config.HOTEL_SERVICE_URL}/hotels/{hotel_id}/rooms/check-availability",
        json={"check_in": check_in, "check_out": check_out},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    availability_data = response.json()

    for room in availability_data.get("available_rooms", []):
        if room["room_id"] == room_id and room["available_count"] > 0:
            return room

    return None


@retry_on_failure(max_retries=3, delay=0.5)
@log_request("hotel-service", "/hotels/{hotel_id}/rooms/{room_id}/availability", "PUT")
def update_room_availability(hotel_id: int, room_id: int, change: int) -> bool:
    """
    Update room availability count in the hotel service.

    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :param room_id: The room identifier
    :type room_id: int
    :param change: Change in availability (positive or negative)
    :type change: int
    :return: True if successful
    :rtype: bool
    """
    response = requests.put(
        f"{Config.HOTEL_SERVICE_URL}/hotels/{hotel_id}/rooms/{room_id}/availability",
        json={"room_id": room_id, "change": change},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return True


def calculate_total_price(room_data: dict, check_in: str, check_out: str) -> float:
    """
    Calculate total price for a booking based on room rate and number of nights.

    :param room_data: Room data containing price_per_night
    :type room_data: dict
    :param check_in: Check-in date in ISO format
    :type check_in: str
    :param check_out: Check-out date in ISO format
    :type check_out: str
    :return: Total price for the stay
    :rtype: float
    """
    check_in_date = dt.fromisoformat(check_in)
    check_out_date = dt.fromisoformat(check_out)
    nights = (check_out_date - check_in_date).days
    return room_data["price_per_night"] * nights


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", service=Config.SERVICE_NAME)


@app.post(
    "/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED
)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    try:
        if not verify_user_exists(booking.user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        room_data = check_room_availability(
            booking.hotel_id, booking.room_id, booking.check_in, booking.check_out
        )

        if not room_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room not available for the selected dates",
            )

        total_price = calculate_total_price(
            room_data, booking.check_in, booking.check_out
        )

        db_booking = Booking(
            user_id=booking.user_id,
            hotel_id=booking.hotel_id,
            room_id=booking.room_id,
            check_in=booking.check_in,
            check_out=booking.check_out,
            total_price=total_price,
            status="confirmed",
        )

        try:
            update_room_availability(booking.hotel_id, booking.room_id, -1)
        except requests.exceptions.RequestException as e:
            logger.error(
                "availability_update_failed_during_booking",
                hotel_id=booking.hotel_id,
                room_id=booking.room_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to reserve room. Please try again.",
            ) from e

        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)

        logger.info(
            "booking_created",
            booking_id=db_booking.id,
            user_id=booking.user_id,
            hotel_id=booking.hotel_id,
            room_id=booking.room_id,
        )

        return db_booking

    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        logger.error("booking_creation_failed_service_unavailable", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable",
        ) from e
    except Exception as e:
        db.rollback()
        logger.error("booking_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking",
        ) from e


@app.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BOOKING_NOT_FOUND
        )
    return booking


@app.get("/bookings/user/{user_id}", response_model=List[BookingResponse])
async def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    try:
        if not verify_user_exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
        return bookings
    except HTTPException:
        raise
    except Exception as e:
        logger.error("fetch_user_bookings_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bookings",
        ) from e


@app.put("/bookings/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int, cancellation: BookingCancellation, db: Session = Depends(get_db)
):
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=BOOKING_NOT_FOUND
            )

        if booking.status == "cancelled":  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled",
            )

        try:
            update_room_availability(booking.hotel_id, booking.room_id, 1)
        except requests.exceptions.RequestException as e:
            logger.error(
                "availability_update_failed_during_cancellation",
                booking_id=booking_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to cancel booking. Please try again.",
            ) from e

        booking.status = "cancelled"  # type: ignore
        db.commit()
        db.refresh(booking)

        logger.info(
            "booking_cancelled", booking_id=booking_id, reason=cancellation.reason
        )
        return booking

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("booking_cancellation_failed", booking_id=booking_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking",
        ) from e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=Config.SERVICE_PORT)
