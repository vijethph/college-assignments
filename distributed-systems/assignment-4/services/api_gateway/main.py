"""
API Gateway Service.

This module provides a unified entry point for all microservices in the hotel
booking system. It proxies requests to the appropriate backend services and
handles cross-cutting concerns like request routing and error handling.
"""

import os

import aiohttp
import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

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
    logger.info(
        "api_gateway_started",
        port=os.getenv("SERVICE_PORT", "8000"),
        hotel_service=HOTEL_SERVICE_URL,
        user_service=USER_SERVICE_URL,
        booking_service=BOOKING_SERVICE_URL,
    )


@app.get("/health")
async def health():
    """
    Check API Gateway health status.

    :return: Health status response
    :rtype: dict
    """
    return {"status": "healthy", "service": "api-gateway"}


# Hotel Service Routes
@app.get("/api/hotels", tags=["Hotels"], summary="Get all hotels")
async def get_hotels(request: Request):
    """
    Get a list of all hotels.

    :param request: The incoming HTTP request
    :type request: Request
    :return: List of hotels from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, "/hotels")


@app.post("/api/hotels", tags=["Hotels"], summary="Create a new hotel")
async def create_hotel(request: Request):
    """
    Create a new hotel.

    :param request: The incoming HTTP request
    :type request: Request
    :return: Created hotel details from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, "/hotels")


@app.get("/api/hotels/{hotel_id}", tags=["Hotels"], summary="Get hotel by ID")
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
    tags=["Hotels"],
    summary="Create a room in hotel",
)
async def create_room(request: Request, hotel_id: int):
    """
    Create a new room in a hotel.

    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :return: Created room details from the hotel service
    """
    return await proxy_request(request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}/rooms")


@app.get(
    "/api/hotels/{hotel_id}/rooms",
    tags=["Hotels"],
    summary="Get hotel rooms",
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
    tags=["Hotels"],
    summary="Check room availability",
)
async def check_room_availability(request: Request, hotel_id: int):
    """
    Check available rooms for specified dates.

    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :return: Available rooms for the specified dates from the hotel service
    """
    return await proxy_request(
        request, HOTEL_SERVICE_URL, f"/hotels/{hotel_id}/rooms/check-availability"
    )


@app.put(
    "/api/hotels/{hotel_id}/rooms/{room_id}/availability",
    tags=["Hotels"],
    summary="Update room availability",
)
async def update_room_availability(request: Request, hotel_id: int, room_id: int):
    """
    Update room availability count.

    :param request: The incoming HTTP request
    :type request: Request
    :param hotel_id: The hotel identifier
    :type hotel_id: int
    :param room_id: The room identifier
    :type room_id: int
    :return: Updated room availability from the hotel service
    """
    return await proxy_request(
        request,
        HOTEL_SERVICE_URL,
        f"/hotels/{hotel_id}/rooms/{room_id}/availability",
    )


# User Service Routes
@app.post("/api/users/register", tags=["Users"], summary="Register a new user")
async def register_user(request: Request):
    """
    Register a new user account.

    :param request: The incoming HTTP request
    :type request: Request
    :return: Created user details from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, "/users/register")


@app.post("/api/users/login", tags=["Users"], summary="Login user")
async def login_user(request: Request):
    """
    Login and get access token.

    :param request: The incoming HTTP request
    :type request: Request
    :return: Access token and user information from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, "/users/login")


@app.get("/api/users/{user_id}", tags=["Users"], summary="Get user by ID")
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


@app.put("/api/users/{user_id}", tags=["Users"], summary="Update user")
async def update_user(request: Request, user_id: int):
    """
    Update user information.

    :param request: The incoming HTTP request
    :type request: Request
    :param user_id: The user identifier
    :type user_id: int
    :return: Updated user details from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, f"/users/{user_id}")


@app.post("/api/users/verify-token", tags=["Users"], summary="Verify token")
async def verify_token(request: Request):
    """
    Verify JWT token.

    :param request: The incoming HTTP request
    :type request: Request
    :return: Token verification result from the user service
    """
    return await proxy_request(request, USER_SERVICE_URL, "/users/verify-token")


# Booking Service Routes
@app.post("/api/bookings", tags=["Bookings"], summary="Create a new booking")
async def create_booking(request: Request):
    """
    Create a new booking.

    :param request: The incoming HTTP request
    :type request: Request
    :return: Created booking details from the booking service
    """
    return await proxy_request(request, BOOKING_SERVICE_URL, "/bookings")


@app.get("/api/bookings/{booking_id}", tags=["Bookings"], summary="Get booking by ID")
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
    tags=["Bookings"],
    summary="Get user bookings",
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
    tags=["Bookings"],
    summary="Cancel booking",
)
async def cancel_booking(request: Request, booking_id: int):
    """
    Cancel a booking.

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
