"""Taste Twins API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.services.twin_matching_service import twin_matching_service
from app.services.taste_dna_service import taste_dna_service
from app.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import TasteDNANotFoundException

router = APIRouter()


class TwinResponse(BaseModel):
    """Response for a single twin."""
    twin_id: str
    name: str
    email: str
    avatar_url: str | None
    similarity_score: float
    shared_cuisines: List[str]
    adventure_score: float
    spice_tolerance: float


class TwinsListResponse(BaseModel):
    """Response for twins list."""
    twins: List[TwinResponse]
    total_count: int


class TwinCountResponse(BaseModel):
    """Response for twin count."""
    count: int


@router.get("", response_model=TwinsListResponse)
async def get_taste_twins(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's Taste Twins."""
    twins = await twin_matching_service.get_user_twins(db, current_user.id)
    return TwinsListResponse(
        twins=[TwinResponse(**t) for t in twins],
        total_count=len(twins),
    )


@router.get("/count", response_model=TwinCountResponse)
async def get_twin_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of user's Taste Twins."""
    count = await twin_matching_service.get_twin_count(db, current_user.id)
    return TwinCountResponse(count=count)


@router.get("/{twin_id}", response_model=TwinResponse)
async def get_twin_profile(
    twin_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get specific twin's profile."""
    twins = await twin_matching_service.get_user_twins(db, current_user.id)

    for twin in twins:
        if twin["twin_id"] == str(twin_id):
            return TwinResponse(**twin)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Twin not found",
    )


@router.post("/refresh", response_model=TwinsListResponse)
async def refresh_twins(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Refresh twin matching."""
    taste_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    if not taste_dna:
        raise TasteDNANotFoundException()

    twins = await twin_matching_service.refresh_twins(db, current_user.id)
    return TwinsListResponse(
        twins=[TwinResponse(**t) for t in twins],
        total_count=len(twins),
    )
