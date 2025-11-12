"""User Service Pydantic Models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common fields."""

    email: EmailStr
    name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    """Model for user login credentials."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Model for user API responses."""

    id: int
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserUpdate(BaseModel):
    """Model for updating user information."""

    name: Optional[str] = None
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    """Model for JWT token responses."""

    access_token: str
    token_type: str
    user_id: int


class HealthResponse(BaseModel):
    """Model for health check responses."""

    status: str
    service: str
