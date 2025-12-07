"""Restaurant API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.session import get_db
from app.schemas.restaurant import (
    RestaurantSearchParams,
    RestaurantSearchResponse,
    RestaurantDetail,
)
from app.services.yelp_service import yelp_service
from app.dependencies import get_current_user
from app.models.user import User
from app.models.interaction_log import InteractionLog
from app.models.saved_restaurant import SavedRestaurant

router = APIRouter()


class SaveRestaurantRequest(BaseModel):
    """Request to save a restaurant."""
    notes: Optional[str] = None


class LogInteractionRequest(BaseModel):
    """Request to log an interaction."""
    action_type: str  # view, save, book, dismiss, like
    context: Optional[str] = None  # lucky, compare, search, twins


@router.get("/search")
async def search_restaurants(
    term: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius: Optional[int] = Query(None, le=40000),
    categories: Optional[str] = Query(None),
    price: Optional[str] = Query(None),
    open_now: bool = Query(False),
    sort_by: str = Query("best_match"),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """Search for restaurants using Yelp API."""
    results = await yelp_service.search_businesses(
        term=term or "restaurants",
        location=location,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        categories=categories,
        price=price,
        open_now=open_now,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )
    return results


@router.get("/{restaurant_id}")
async def get_restaurant(
    restaurant_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get detailed restaurant information."""
    return await yelp_service.get_business(restaurant_id)


@router.get("/{restaurant_id}/reviews")
async def get_restaurant_reviews(
    restaurant_id: str,
    limit: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user),
):
    """Get restaurant reviews."""
    return await yelp_service.get_business_reviews(restaurant_id, limit=limit)


@router.post("/{restaurant_id}/save")
async def save_restaurant(
    restaurant_id: str,
    request: SaveRestaurantRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a restaurant to user's list."""
    # Get restaurant data
    restaurant = await yelp_service.get_business(restaurant_id)

    # Check if already saved
    result = await db.execute(
        select(SavedRestaurant)
        .where(SavedRestaurant.user_id == current_user.id)
        .where(SavedRestaurant.restaurant_id == restaurant_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.notes = request.notes
        existing.restaurant_data = restaurant
    else:
        saved = SavedRestaurant(
            user_id=current_user.id,
            restaurant_id=restaurant_id,
            restaurant_name=restaurant.get("name"),
            restaurant_data=restaurant,
            notes=request.notes,
        )
        db.add(saved)

    await db.commit()
    return {"message": "Restaurant saved successfully"}


@router.delete("/{restaurant_id}/save")
async def unsave_restaurant(
    restaurant_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove restaurant from saved list."""
    from sqlalchemy import delete
    await db.execute(
        delete(SavedRestaurant)
        .where(SavedRestaurant.user_id == current_user.id)
        .where(SavedRestaurant.restaurant_id == restaurant_id)
    )
    await db.commit()
    return {"message": "Restaurant removed from saved list"}


@router.get("/saved/list")
async def get_saved_restaurants(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's saved restaurants - always fetch fresh data from Yelp."""
    result = await db.execute(
        select(SavedRestaurant)
        .where(SavedRestaurant.user_id == current_user.id)
        .order_by(SavedRestaurant.created_at.desc())
    )
    saved = result.scalars().all()

    # Always fetch fresh restaurant data from Yelp instead of using stored snapshots
    saved_list = []
    for s in saved:
        try:
            # Fetch current data from Yelp API
            fresh_data = await yelp_service.get_business(s.restaurant_id)
            saved_list.append({
                "restaurant_id": s.restaurant_id,
                "restaurant_name": fresh_data.get("name", s.restaurant_name),
                "restaurant_data": fresh_data,  # Always use fresh Yelp data
                "notes": s.notes,
                "saved_at": s.created_at,
            })
        except Exception:
            # If restaurant no longer exists on Yelp, skip it
            continue

    return saved_list


@router.post("/{restaurant_id}/log")
async def log_interaction(
    restaurant_id: str,
    request: LogInteractionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log a user interaction with a restaurant."""
    log = InteractionLog(
        user_id=current_user.id,
        restaurant_id=restaurant_id,
        action_type=request.action_type,
        context=request.context,
    )
    db.add(log)
    await db.commit()

    # Update TasteDNA based on interaction (real-time learning)
    if request.action_type in ["save", "book", "like"]:
        from app.services.taste_dna_service import taste_dna_service
        restaurant = await yelp_service.get_business(restaurant_id)
        await taste_dna_service.update_taste_dna_from_interaction(
            db, current_user.id, request.action_type, restaurant
        )

    # Check for visit-based achievements
    if request.action_type == "visited":
        from app.models.challenge import UserAchievement
        from datetime import datetime

        # Count total visits
        result = await db.execute(
            select(InteractionLog)
            .where(InteractionLog.user_id == current_user.id)
            .where(InteractionLog.action_type == "visited")
        )
        visit_count = len(result.scalars().all())

        # Define achievement thresholds
        achievements_to_check = {
            1: "first_visit",
            5: "explorer_5",
            10: "explorer_10",
            25: "explorer_25",
            50: "explorer_50",
        }

        # Award achievement if milestone reached
        if visit_count in achievements_to_check:
            achievement_type = achievements_to_check[visit_count]

            # Check if already earned
            existing = await db.execute(
                select(UserAchievement)
                .where(UserAchievement.user_id == current_user.id)
                .where(UserAchievement.achievement_type == achievement_type)
            )

            if not existing.scalar_one_or_none():
                achievement = UserAchievement(
                    user_id=current_user.id,
                    achievement_type=achievement_type,
                    earned_at=datetime.utcnow()
                )
                db.add(achievement)
                await db.commit()

    return {"message": "Interaction logged"}
