"""User Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for user update."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    avatar_url: Optional[str] = None
    quiz_completed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithToken(BaseModel):
    """Schema for user with auth token."""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: str
    exp: datetime
