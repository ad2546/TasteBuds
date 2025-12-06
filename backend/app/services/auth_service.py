"""Authentication service."""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserWithToken
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import InvalidCredentialsException, UserAlreadyExistsException


class AuthService:
    """Service for user authentication."""

    async def register(
        self,
        db: AsyncSession,
        user_data: UserCreate,
    ) -> UserWithToken:
        """Register a new user."""
        # Check if user exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise UserAlreadyExistsException(user_data.email)

        # Create user
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=get_password_hash(user_data.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Generate token
        token = create_access_token({"sub": str(user.id)})

        return UserWithToken(
            user=UserResponse.model_validate(user),
            access_token=token,
        )

    async def login(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> UserWithToken:
        """Login user with email and password."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsException()

        token = create_access_token({"sub": str(user.id)})

        return UserWithToken(
            user=UserResponse.model_validate(user),
            access_token=token,
        )

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


# Global service instance
auth_service = AuthService()


def get_auth_service() -> AuthService:
    """Dependency to get auth service."""
    return auth_service
