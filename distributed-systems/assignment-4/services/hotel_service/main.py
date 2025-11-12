"""
Hotel Service.

This module provides API endpoints for managing hotels and rooms in the hotel
booking system. It handles CRUD operations for hotels, room management, and
availability checking.
"""

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
from models import (
    HealthResponse,
    HotelCreate,
    HotelResponse,
    RoomAvailabilityCheck,
    RoomAvailabilityUpdate,
    RoomCreate,
    RoomResponse,
)
from shared.logging_config import configure_logging, get_logger


configure_logging(Config.SERVICE_NAME)
logger = get_logger()

HOTEL_NOT_FOUND = "Hotel not found"
ROOM_NOT_FOUND = "Room not found"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("service_starting", port=Config.SERVICE_PORT)
    init_db()
    yield
    logger.info("service_stopping")


app = FastAPI(title="Hotel Service", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", service=Config.SERVICE_NAME)


@app.post("/hotels", response_model=HotelResponse, status_code=201)
async def create_hotel(hotel: HotelCreate, db: Session = Depends(get_db)):
    try:
        db_hotel = Hotel(**hotel.model_dump())
        db.add(db_hotel)
        db.commit()
        db.refresh(db_hotel)
        logger.info("hotel_created", hotel_id=db_hotel.id, hotel_name=db_hotel.name)
        return db_hotel
    except Exception as e:
        db.rollback()
        logger.error("hotel_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create hotel") from e


@app.get("/hotels", response_model=List[HotelResponse])
async def get_hotels(
    location: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Hotel)
        if location:
            query = query.filter(Hotel.location.contains(location))
        if min_rating is not None:
            query = query.filter(Hotel.rating >= min_rating)
        hotels = query.all()
        return hotels
    except Exception as e:
        logger.error("hotels_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch hotels") from e


@app.get("/hotels/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail=HOTEL_NOT_FOUND)
    return hotel


@app.post("/hotels/{hotel_id}/rooms", response_model=RoomResponse, status_code=201)
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


@app.get("/hotels/{hotel_id}/rooms", response_model=List[RoomResponse])
async def get_hotel_rooms(
    hotel_id: int,
    room_type: Optional[str] = Query(None),
    min_capacity: Optional[int] = Query(None, ge=1),
    max_price: Optional[float] = Query(None, gt=0),
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


@app.post("/hotels/{hotel_id}/rooms/check-availability")
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


@app.put("/hotels/{hotel_id}/rooms/{room_id}/availability")
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
