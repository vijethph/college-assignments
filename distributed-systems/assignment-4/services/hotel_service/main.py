"""
Hotel Service.

This module provides API endpoints for managing hotels and rooms in the hotel
booking system. It handles CRUD operations for hotels, room management, and
availability checking.
"""

import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
import uvicorn

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import Config
from database import Hotel, Room, get_db, init_db
from shared.logging_config import configure_logging, get_logger
from shared.models import (
    HealthResponse,
    HotelCreate,
    HotelResponse,
    RoomAvailabilityCheck,
    RoomAvailabilityUpdate,
    RoomCreate,
    RoomResponse,
)
from shared.messaging import broker


configure_logging(Config.SERVICE_NAME)
logger = get_logger()

HOTEL_NOT_FOUND = "Hotel not found"
ROOM_NOT_FOUND = "Room not found"


def hotel_to_response(hotel: Hotel) -> dict:
    """
    Convert hotel database model to response dict.

    :param hotel: Hotel database object
    :type hotel: Hotel
    :return: Hotel data as dictionary with amenities parsed
    :rtype: dict
    """
    return {
        "id": hotel.id,
        "name": hotel.name,
        "location": hotel.location,
        "description": hotel.description,
        "amenities": (
            json.loads(hotel.amenities)
            if isinstance(hotel.amenities, str)
            else hotel.amenities
        ),
        "rating": hotel.rating,
    }


async def handle_booking_cancelled(event: dict):
    """
    Handle booking cancelled event and restore room availability.

    :param event: Event payload containing booking cancellation details
    :type event: dict
    """
    db = next(get_db())
    try:
        room = (
            db.query(Room)
            .filter(Room.id == event["room_id"], Room.hotel_id == event["hotel_id"])
            .first()
        )

        if room:
            room.available_count += 1
            db.commit()
            logger.info(
                "room_availability_restored",
                hotel_id=event["hotel_id"],
                room_id=event["room_id"],
                booking_id=event["booking_id"],
                new_count=room.available_count,
            )
    except Exception as e:
        db.rollback()
        logger.error("availability_restore_failed", error=str(e))
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("service_starting", port=Config.SERVICE_PORT)
    init_db()
    await broker.connect()
    await broker.subscribe(
        queue_name="hotel_service_cancellations",
        routing_key="booking.cancelled",
        callback=handle_booking_cancelled,
    )
    yield
    await broker.close()
    logger.info("service_stopping")


app = FastAPI(
    title="Hotel Service",
    description="Hotel and room management service for hotel booking system",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the hotel service is running and healthy",
    tags=["Health"],
)
async def health_check():
    return HealthResponse(status="healthy", service=Config.SERVICE_NAME)


@app.post(
    "/hotels",
    response_model=HotelResponse,
    status_code=201,
    summary="Create Hotel",
    description="Register a new hotel in the system",
    tags=["Hotels"],
    responses={
        201: {"description": "Hotel created successfully"},
        500: {"description": "Internal server error"},
    },
)
async def create_hotel(hotel: HotelCreate, db: Session = Depends(get_db)):
    """
    Create a new hotel.

    :param hotel: Hotel data to create
    :type hotel: HotelCreate
    :param db: Database session
    :type db: Session
    :return: Created hotel details
    :rtype: Hotel
    :raises HTTPException: If hotel creation fails
    """
    try:
        hotel_data = hotel.model_dump()
        hotel_data["amenities"] = json.dumps(hotel_data["amenities"])
        db_hotel = Hotel(**hotel_data)
        db.add(db_hotel)
        db.commit()
        db.refresh(db_hotel)
        logger.info("hotel_created", hotel_id=db_hotel.id, hotel_name=db_hotel.name)
        return hotel_to_response(db_hotel)
    except Exception as e:
        db.rollback()
        logger.error("hotel_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create hotel") from e


@app.get(
    "/hotels",
    response_model=List[HotelResponse],
    summary="List Hotels",
    description="Retrieve list of all hotels with optional filters for location and minimum rating",
    tags=["Hotels"],
)
async def get_hotels(
    location: Optional[str] = Query(None, description="Filter by location"),
    min_rating: Optional[float] = Query(
        None, ge=0.0, le=5.0, description="Minimum hotel rating"
    ),
    db: Session = Depends(get_db),
):
    """
    Get all hotels with optional filters.

    :param location: Filter hotels by location
    :type location: Optional[str]
    :param min_rating: Filter hotels by minimum rating
    :type min_rating: Optional[float]
    :param db: Database session
    :type db: Session
    :return: List of hotels matching criteria
    :rtype: List[Hotel]
    """
    try:
        query = db.query(Hotel)
        if location:
            query = query.filter(Hotel.location.contains(location))
        if min_rating is not None:
            query = query.filter(Hotel.rating >= min_rating)
        hotels = query.all()
        logger.info("hotels_retrieved", count=len(hotels))
        return [hotel_to_response(hotel) for hotel in hotels]
    except Exception as e:
        logger.error("hotels_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch hotels") from e


@app.get(
    "/hotels/{hotel_id}",
    response_model=HotelResponse,
    summary="Get Hotel",
    description="Retrieve details of a specific hotel by ID",
    tags=["Hotels"],
    responses={
        200: {"description": "Hotel details retrieved successfully"},
        404: {"description": "Hotel not found"},
    },
)
async def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    """
    Get hotel by ID.

    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :param db: Database session
    :type db: Session
    :return: Hotel details
    :rtype: Hotel
    :raises HTTPException: If hotel not found
    """
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail=HOTEL_NOT_FOUND)
    return hotel_to_response(hotel)


@app.post(
    "/hotels/{hotel_id}/rooms",
    response_model=RoomResponse,
    status_code=201,
    summary="Create Room",
    description="Add a new room type to a hotel",
    tags=["Rooms"],
    responses={
        201: {"description": "Room created successfully"},
        404: {"description": "Hotel not found"},
        500: {"description": "Internal server error"},
    },
)
async def create_room(hotel_id: int, room: RoomCreate, db: Session = Depends(get_db)):
    try:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail=HOTEL_NOT_FOUND)

        room_data = room.model_dump()
        room_data["hotel_id"] = hotel_id
        db_room = Room(**room_data)
        db.add(db_room)
        db.commit()
        db.refresh(db_room)
        logger.info(
            "room_created",
            hotel_id=hotel_id,
            room_id=db_room.id,
            room_type=db_room.room_type,
        )
        return db_room
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("room_creation_failed", hotel_id=hotel_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create room") from e


@app.get(
    "/hotels/{hotel_id}/rooms",
    response_model=List[RoomResponse],
    summary="List Hotel Rooms",
    description="Retrieve all rooms for a specific hotel with optional filters",
    tags=["Rooms"],
)
async def get_hotel_rooms(
    hotel_id: int,
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    min_capacity: Optional[int] = Query(
        None, ge=1, description="Minimum guest capacity"
    ),
    max_price: Optional[float] = Query(
        None, gt=0, description="Maximum price per night"
    ),
    db: Session = Depends(get_db),
):
    try:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail=HOTEL_NOT_FOUND)

        query = db.query(Room).filter(Room.hotel_id == hotel_id)
        if room_type:
            query = query.filter(Room.room_type == room_type)
        if min_capacity:
            query = query.filter(Room.capacity >= min_capacity)
        if max_price:
            query = query.filter(Room.price_per_night <= max_price)

        rooms = query.all()
        return rooms
    except HTTPException:
        raise
    except Exception as e:
        logger.error("rooms_fetch_failed", hotel_id=hotel_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch rooms") from e


@app.post(
    "/hotels/{hotel_id}/rooms/check-availability",
    summary="Check Room Availability",
    description="Check which rooms are available for given dates at a specific hotel",
    tags=["Rooms"],
    responses={
        200: {"description": "Availability information retrieved successfully"},
        404: {"description": "Hotel not found"},
    },
)
async def check_room_availability(
    hotel_id: int,
    availability_check: RoomAvailabilityCheck,
    db: Session = Depends(get_db),
):
    try:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail=HOTEL_NOT_FOUND)

        query = db.query(Room).filter(
            Room.hotel_id == hotel_id, Room.available_count > 0
        )

        if availability_check.room_type:
            query = query.filter(Room.room_type == availability_check.room_type)

        available_rooms = query.all()

        return {
            "hotel_id": hotel_id,
            "check_in": availability_check.check_in,
            "check_out": availability_check.check_out,
            "available_rooms": [
                {
                    "room_id": room.id,
                    "room_type": room.room_type,
                    "price_per_night": room.price_per_night,
                    "capacity": room.capacity,
                    "available_count": room.available_count,
                }
                for room in available_rooms
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("availability_check_failed", hotel_id=hotel_id, error=str(e))
        raise HTTPException(
            status_code=500, detail="Failed to check availability"
        ) from e


@app.put(
    "/hotels/{hotel_id}/rooms/{room_id}/availability",
    summary="Update Room Availability",
    description="Update the available count for a room (increase or decrease)",
    tags=["Rooms"],
    responses={
        200: {"description": "Availability updated successfully"},
        400: {"description": "Invalid availability update"},
        404: {"description": "Room not found"},
    },
)
async def update_room_availability(
    hotel_id: int,
    room_id: int,
    update: RoomAvailabilityUpdate,
    db: Session = Depends(get_db),
):
    try:
        room = (
            db.query(Room).filter(Room.id == room_id, Room.hotel_id == hotel_id).first()
        )

        if not room:
            raise HTTPException(status_code=404, detail=ROOM_NOT_FOUND)

        new_count = room.available_count + update.change

        if new_count < 0:  # type: ignore
            logger.error(
                "invalid_availability_update",
                room_id=room_id,
                current_count=room.available_count,
                change=update.change,
            )
            raise HTTPException(
                status_code=400, detail="Cannot reduce availability below zero"
            )

        room.available_count = new_count  # type: ignore
        db.commit()
        db.refresh(room)

        logger.info(
            "availability_updated",
            room_id=room_id,
            hotel_id=hotel_id,
            new_count=new_count,
            change=update.change,
        )

        return {
            "room_id": room.id,
            "hotel_id": room.hotel_id,
            "available_count": room.available_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("availability_update_failed", room_id=room_id, error=str(e))
        raise HTTPException(
            status_code=500, detail="Failed to update availability"
        ) from e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=Config.SERVICE_PORT)
