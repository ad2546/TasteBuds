"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserWithToken, UserResponse
from app.services.auth_service import auth_service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    # Temporary debug log to inspect incoming payloads causing 422
    logging.getLogger("tastesync.auth").info("Register payload: %s", user_data.model_dump())
    return await auth_service.register(db, user_data)


@router.post("/login", response_model=UserWithToken)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    return await auth_service.login(db, credentials.email, credentials.password)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user info."""
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=UserWithToken)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Refresh authentication token."""
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(current_user.id)})
    return UserWithToken(
        user=UserResponse.model_validate(current_user),
        access_token=token,
    )
