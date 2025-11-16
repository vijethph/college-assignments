"""
API Gateway Service.

This module provides a unified entry point for all microservices in the hotel
booking system. It proxies requests to the appropriate backend services and
handles cross-cutting concerns like request routing and error handling.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import aiohttp
import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from shared.models import (
    BookingCancellation,
    BookingCreate,
    BookingResponse,
    HealthResponse,
    HotelCreate,
    HotelResponse,
    RoomAvailabilityCheck,
    RoomAvailabilityUpdate,
    RoomCreate,
    RoomResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Hotel Booking API Gateway",
    description="Unified entry point for all microservices",
    version="1.0.0",
)

HOTEL_SERVICE_URL = os.getenv("HOTEL_SERVICE_URL", "http://localhost:8001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://localhost:8003")

TIMEOUT = aiohttp.ClientTimeout(total=30.0)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.

    Logs the service startup information including configured backend service URLs.
    """
    logger.info(
        "api_gateway_started",
        port=os.getenv("SERVICE_PORT", "8000"),
        hotel_service=HOTEL_SERVICE_URL,
        user_service=USER_SERVICE_URL,
        booking_service=BOOKING_SERVICE_URL,
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="Check the health status of the API Gateway service",
    responses={
        200: {"description": "Service is healthy and operational"},
    },
)
async def health():
    """
    Health check endpoint.

    :return: Health status of the API gateway
    :rtype: dict
    """
    return {"status": "healthy", "service": "api-gateway"}


# Hotel Service Routes
@app.get(
    "/api/hotels",
    response_model=list[HotelResponse],
    tags=["Hotels"],
    summary="List Hotels",
    description="Retrieve all hotels with optional filtering by location and rating. Proxies to the hotel service.",
    responses={
        200: {"description": "List of hotels retrieved successfully"},
        503: {"description": "Hotel service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def get_hotels(request: Request):
    """
    Get all hotels.

    :param request: The incoming HTTP request
    :type request: Request
    :return: List of hotels from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, "/hotels")


@app.post(
    "/api/hotels",
    response_model=HotelResponse,
    status_code=201,
    tags=["Hotels"],
    summary="Create Hotel",
    description="Create a new hotel in the system via the gateway. Proxies to the hotel service.",
    responses={
        201: {"description": "Hotel successfully created"},
        400: {"description": "Invalid hotel data provided"},
        503: {"description": "Hotel service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def create_hotel(hotel: HotelCreate, request: Request):
    """
    Create a new hotel.

    :param hotel: Hotel data to create
    :type hotel: HotelCreate
    :param request: The incoming HTTP request
    :type request: Request
    :return: Created hotel details from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, "/hotels")


@app.get(
    "/api/hotels/{hotel_id}",
    response_model=HotelResponse,
    tags=["Hotels"],
    summary="Get Hotel",
    description="Retrieve detailed information about a specific hotel by its ID via the gateway.",
    responses={
        200: {"description": "Hotel details retrieved successfully"},
        404: {"description": "Hotel not found"},
        503: {"description": "Hotel service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def get_hotel(request: Request, hotel_id: int):
    """
    Get details of a specific hotel.

    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :return: Hotel details from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}")


@app.put("/api/hotels/{hotel_id}", tags=["Hotels"], summary="Update hotel")
async def update_hotel(request: Request, hotel_id: int):
    """
    Update hotel information.

    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :return: Updated hotel details from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}")


@app.delete("/api/hotels/{hotel_id}", tags=["Hotels"], summary="Delete hotel")
async def delete_hotel(request: Request, hotel_id: int):
    """
    Delete a hotel.

    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :return: Deletion confirmation from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}")


# Hotel Room Routes
@app.post(
    "/api/hotels/{hotel_id}/rooms",
    response_model=RoomResponse,
    status_code=201,
    tags=["Rooms"],
    summary="Create Room",
    description="Add a new room to a specific hotel via the gateway. Proxies to the hotel service.",
    responses={
        201: {"description": "Room successfully created"},
        400: {"description": "Invalid room data provided"},
        404: {"description": "Hotel not found"},
        503: {"description": "Hotel service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def create_room(room: RoomCreate, request: Request, hotel_id: int):
    """
    Create a new room for a hotel.

    :param room: Room data to create
    :type room: RoomCreate
    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :return: Created room details from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}/rooms")


@app.get(
    "/api/hotels/{hotel_id}/rooms",
    response_model=list[RoomResponse],
    tags=["Rooms"],
    summary="List Hotel Rooms",
    description="Retrieve all rooms for a specific hotel with optional filtering by room type and availability.",
    responses={
        200: {"description": "List of rooms retrieved successfully"},
        404: {"description": "Hotel not found"},
        503: {"description": "Hotel service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def get_hotel_rooms(request: Request, hotel_id: int):
    """
    Get all rooms for a specific hotel.

    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :return: List of rooms from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}/rooms")


@app.post(
    "/api/hotels/{hotel_id}/rooms/check-availability",
    tags=["Rooms"],
    summary="Check Room Availability",
    description="Check if rooms of a specific type are available for given dates at a hotel.",
    responses={
        200: {"description": "Availability information retrieved successfully"},
        400: {"description": "Invalid date range or room type"},
        404: {"description": "Hotel not found"},
        503: {"description": "Hotel service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def check_availability(
    availability: RoomAvailabilityCheck, request: Request, hotel_id: int
):
    """
    Check room availability.

    :param availability: Availability check parameters
    :type availability: RoomAvailabilityCheck
    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :return: Availability details from the hotel service
    """
    return await proxy_request(
        request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}/rooms/check-availability"
    )


@app.put(
    "/api/hotels/{hotel_id}/rooms/{room_id}/availability",
    tags=["Rooms"],
    summary="Update Room Availability",
    description="Update the available count for a specific room (increase or decrease inventory).",
    responses={
        200: {"description": "Room availability updated successfully"},
        400: {"description": "Invalid availability change"},
        404: {"description": "Hotel or room not found"},
        503: {"description": "Hotel service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def update_availability(
    availability_update: RoomAvailabilityUpdate,
    request: Request,
    hotel_id: int,
    room_id: int,
):
    """
    Update room availability.

    :param availability_update: Availability update data
    :type availability_update: RoomAvailabilityUpdate
    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :param room_id: The room identifier
    :type room_id: int
    :return: Updated availability details from the hotel service
    """
    return await proxy_request(
        request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}/rooms/{room_id}/availability"
    )


# User Service Routes
@app.post(
    "/api/users/register",
    response_model=UserResponse,
    status_code=201,
    tags=["Users"],
    summary="Register User",
    description="Register a new user account in the system via the gateway. Proxies to the user service.",
    responses={
        201: {"description": "User successfully registered"},
        400: {"description": "Invalid user data or email already exists"},
        503: {"description": "User service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def register_user(user: UserCreate, request: Request):
    """
    Register a new user.

    :param user: User registration data
    :type user: UserCreate
    :param request: The incoming HTTP request
    :type request: Request
    :return: Created user details from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, "/users/register")


@app.post(
    "/api/users/login",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="User Login",
    description="Authenticate a user with email and password, returning a JWT access token.",
    responses={
        200: {"description": "Login successful, JWT token returned"},
        401: {"description": "Invalid credentials"},
        503: {"description": "User service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def login_user(credentials: UserLogin, request: Request):
    """
    Login user.

    :param credentials: Login credentials
    :type credentials: UserLogin
    :param request: The incoming HTTP request
    :type request: Request
    :return: JWT token and user details from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, "/users/login")


@app.get(
    "/api/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get User",
    description="Retrieve detailed information about a specific user by their ID.",
    responses={
        200: {"description": "User details retrieved successfully"},
        404: {"description": "User not found"},
        503: {"description": "User service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def get_user(request: Request, user_id: int):
    """
    Get details of a specific user.

    :param request: The incoming HTTP request
    :type request: Request
    :param user_id: The user identifier
    :type user_id: int
    :return: User details from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, f"/users/{user_id}")


@app.put(
    "/api/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Update User",
    description="Update user profile information such as name and phone number.",
    responses={
        200: {"description": "User updated successfully"},
        404: {"description": "User not found"},
        400: {"description": "Invalid update data"},
        503: {"description": "User service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def update_user(user_update: UserUpdate, request: Request, user_id: int):
    """
    Update user details.

    :param user_update: User update data
    :type user_update: UserUpdate
    :param request: The incoming HTTP request
    :type request: Request
    :param user_id: The user identifier
    :type user_id: int
    :return: Updated user details from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, f"/users/{user_id}")


@app.post(
    "/api/users/verify-token",
    tags=["Authentication"],
    summary="Verify JWT Token",
    description="Validate a JWT access token and retrieve the associated user information.",
    responses={
        200: {"description": "Token is valid, user information returned"},
        401: {"description": "Invalid or expired token"},
        503: {"description": "User service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def verify_token(request: Request):
    """
    Verify JWT token.

    :param request: The incoming HTTP request
    :type request: Request
    :return: Token verification result from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, "/users/verify-token")


# Booking Service Routes
@app.post(
    "/api/bookings",
    response_model=BookingResponse,
    status_code=201,
    tags=["Bookings"],
    summary="Create Booking",
    description="Create a new hotel room booking for a user with specified check-in and check-out dates.",
    responses={
        201: {"description": "Booking successfully created"},
        400: {"description": "Invalid booking data or dates"},
        404: {"description": "User, hotel, or room not found"},
        503: {"description": "Booking service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def create_booking(booking: BookingCreate, request: Request):
    """
    Create a new booking.

    :param booking: Booking data to create
    :type booking: BookingCreate
    :param request: The incoming HTTP request
    :type request: Request
    :return: Created booking details from the booking service
    """
    return await proxy_request(request, BOOKING_SERVICE_URL, "/bookings")


@app.get(
    "/api/bookings/{booking_id}",
    response_model=BookingResponse,
    tags=["Bookings"],
    summary="Get Booking",
    description="Retrieve detailed information about a specific booking by its ID.",
    responses={
        200: {"description": "Booking details retrieved successfully"},
        404: {"description": "Booking not found"},
        503: {"description": "Booking service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def get_booking(request: Request, booking_id: int):
    """
    Get details of a specific booking.

    :param request: The incoming HTTP request
    :type request: Request
    :param booking_id: The booking identifier
    :type booking_id: int
    :return: Booking details from the booking service
    """
    return await proxy_request(request, BOOKING_SERVICE_URL, f"/bookings/{booking_id}")


@app.get(
    "/api/bookings/user/{user_id}",
    response_model=list[BookingResponse],
    tags=["Bookings"],
    summary="Get User Bookings",
    description="Retrieve all bookings made by a specific user, including active and cancelled bookings.",
    responses={
        200: {"description": "List of user bookings retrieved successfully"},
        404: {"description": "User not found"},
        503: {"description": "Booking service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def get_user_bookings(request: Request, user_id: int):
    """
    Get all bookings for a specific user.

    :param request: The incoming HTTP request
    :type request: Request
    :param user_id: The user identifier
    :type user_id: int
    :return: List of bookings from the booking service
    """
    return await proxy_request(
        request, BOOKING_SERVICE_URL, f"/bookings/user/{user_id}"
    )


@app.put(
    "/api/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
    tags=["Bookings"],
    summary="Cancel Booking",
    description="Cancel an existing booking and optionally provide a cancellation reason.",
    responses={
        200: {"description": "Booking cancelled successfully"},
        400: {
            "description": "Booking cannot be cancelled (already cancelled or checked in)"
        },
        404: {"description": "Booking not found"},
        503: {"description": "Booking service unavailable"},
        504: {"description": "Gateway timeout"},
    },
)
async def cancel_booking(
    cancellation: BookingCancellation, request: Request, booking_id: int
):
    """
    Cancel a booking.

    :param cancellation: Cancellation data
    :type cancellation: BookingCancellation
    :param request: The incoming HTTP request
    :type request: Request
    :param booking_id: The booking identifier
    :type booking_id: int
    :return: Cancelled booking details from the booking service
    """
    return await proxy_request(
        request, BOOKING_SERVICE_URL, f"/bookings/{booking_id}/cancel"
    )


async def proxy_request(request: Request, service_url: str, path: str):
    """
    Proxy request to backend service with improved error handling.

    :param request: The incoming HTTP request
    :type request: Request
    :param service_url: The backend service URL
    :type service_url: str
    :param path: The path to append to the service URL
    :type path: str
    :return: JSON response from the backend service
    :rtype: JSONResponse
    :raises HTTPException: If the backend service is unavailable or returns an error
    """
    url = f"{service_url}{path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    # Filter out headers that should not be proxied
    headers_to_skip = {
        "host",
        "content-length",
        "transfer-encoding",
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "upgrade",
    }

    headers = {
        k: v for k, v in request.headers.items() if k.lower() not in headers_to_skip
    }

    body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None

    logger.info("proxy_request", method=request.method, url=url, has_body=bool(body))

    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.request(
                method=request.method, url=url, headers=headers, data=body
            ) as response:
                try:
                    content = await response.json()
                except (ValueError, aiohttp.ContentTypeError):
                    text_content = await response.text()
                    content = {"message": text_content} if text_content else {}

                logger.info(
                    "proxy_response",
                    url=url,
                    status=response.status,
                    content_type=response.headers.get("content-type"),
                )

                return JSONResponse(
                    content=content,
                    status_code=response.status,
                )
        except aiohttp.ServerTimeoutError as e:
            logger.error("proxy_timeout", url=url, timeout=TIMEOUT.total, error=str(e))
            raise HTTPException(
                status_code=504,
                detail=f"Gateway timeout: Backend service at {service_url} did not respond within {TIMEOUT.total}s",
            ) from e
        except aiohttp.ClientConnectorError as e:
            logger.error(
                "proxy_connection_error", url=url, service_url=service_url, error=str(e)
            )
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: Cannot connect to backend service at {service_url}",
            ) from e
        except aiohttp.ClientError as e:
            logger.error(
                "proxy_client_error", url=url, error=str(e), error_type=type(e).__name__
            )
            raise HTTPException(
                status_code=502,
                detail=f"Bad gateway: Error communicating with backend service - {type(e).__name__}",
            ) from e
        except Exception as e:
            logger.error(
                "proxy_unexpected_error",
                url=url,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {type(e).__name__}"
            ) from e


if __name__ == "__main__":
    port = int(os.getenv("SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
