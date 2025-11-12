"""
User Service.

This module provides API endpoints for user management in the hotel booking
system. It handles user registration, authentication, JWT token management,
and user profile operations.
"""

import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import uvicorn

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import Config
from database import User, get_db, init_db
from models import (
    HealthResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from shared.logging_config import configure_logging, get_logger


configure_logging(Config.SERVICE_NAME)
logger = get_logger()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USER_NOT_FOUND = "User not found"
INVALID_CREDENTIALS = "Invalid credentials"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("service_starting", port=Config.SERVICE_PORT)
    init_db()
    yield
    logger.info("service_stopping")


app = FastAPI(title="User Service", lifespan=lifespan)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    :param password: Plain text password
    :type password: str
    :return: Hashed password
    :rtype: str
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    :param plain_password: Plain text password
    :type plain_password: str
    :param hashed_password: Hashed password
    :type hashed_password: str
    :return: True if password matches, False otherwise
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for a user.

    :param user_id: The user identifier
    :type user_id: int
    :return: Encoded JWT token
    :rtype: str
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=Config.JWT_EXPIRATION_MINUTES
    )
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> int:
    """
    Verify and decode a JWT token.

    :param token: JWT token string
    :type token: str
    :return: User ID extracted from token
    :rtype: int
    :raises HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
        )
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return int(user_id_str)
    except JWTError as e:
        logger.error("token_verification_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", service=Config.SERVICE_NAME)


@app.post(
    "/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = hash_password(user.password)
        db_user = User(
            email=user.email,
            name=user.name,
            phone=user.phone,
            password_hash=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info("user_registered", user_id=db_user.id, email=user.email)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("user_registration_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        ) from e


@app.post("/users/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.password_hash):  # type: ignore
            logger.warning("login_failed", email=credentials.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS
            )

        access_token = create_access_token(user.id)  # type: ignore
        logger.info("user_logged_in", user_id=user.id)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,  # type: ignore
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("login_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        ) from e


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )

        if user_update.name is not None:
            user.name = user_update.name  # type: ignore
        if user_update.phone is not None:
            user.phone = user_update.phone  # type: ignore

        db.commit()
        db.refresh(user)

        logger.info("user_updated", user_id=user_id)
        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("user_update_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        ) from e


@app.post("/users/verify-token")
async def verify_user_token(token: str):
    user_id = verify_token(token)
    return {"user_id": user_id, "valid": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=Config.SERVICE_PORT)
