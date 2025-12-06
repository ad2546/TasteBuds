"""Discovery API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.schemas.discovery import (
    FeelingLuckyResponse,
    CompareResponse,
    CompareOption,
    TrendingResponse,
    TrendingItem,
    ExplainRequest,
    ExplainResponse,
)
from app.schemas.restaurant import RestaurantWithExplanation, RestaurantBase
from app.services.discovery_service import discovery_service
from app.services.taste_dna_service import taste_dna_service
from app.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import TasteDNANotFoundException, QuizNotCompletedException

router = APIRouter()


@router.get("/lucky")
async def feeling_lucky(
    location: str = Query(..., description="Location for restaurant search"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single highly-matched restaurant recommendation."""
    if not current_user.quiz_completed:
        raise QuizNotCompletedException()

    result = await discovery_service.get_feeling_lucky(
        db, current_user.id, location
    )

    if not result:
        return {"message": "No restaurants found in your area"}

    restaurant = result["restaurant"]
    return {
        "restaurant": {
            **restaurant,
            "explanation": result["explanation"],
            "match_score": result["match_score"],
        },
        "twin_count": result["twin_count"],
        "confidence": result["match_score"],
    }


@router.get("/compare")
async def compare_restaurants(
    location: str = Query(..., description="Location for restaurant search"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get 3 restaurant options for comparison."""
    if not current_user.quiz_completed:
        raise QuizNotCompletedException()

    options = await discovery_service.get_compare_options(
        db, current_user.id, location
    )

    return {
        "options": options,
        "recommendation": "Based on your TasteDNA, we recommend comparing these diverse options!",
    }


@router.get("/trending")
async def trending_among_twins(
    location: str = Query(..., description="Location for restaurant search"),
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get restaurants trending among user's Taste Twins."""
    if not current_user.quiz_completed:
        raise QuizNotCompletedException()

    trending = await discovery_service.get_trending_among_twins(
        db, current_user.id, location, limit
    )

    return {
        "items": trending,
        "time_period": "this_week",
    }


@router.post("/explain")
async def explain_recommendation(
    request: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed explanation for why a restaurant matches."""
    taste_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    if not taste_dna:
        raise TasteDNANotFoundException()

    from app.services.yelp_service import yelp_service
    restaurant = await yelp_service.get_business(request.restaurant_id)

    # Calculate match factors
    match_factors = []

    # Price factor
    price = restaurant.get("price", "$$")
    price_match = 1 - abs(taste_dna.price_sensitivity - (len(price) / 4))
    match_factors.append({
        "factor": "Price",
        "score": round(price_match, 2),
        "description": f"Price point ({price}) {'matches' if price_match > 0.7 else 'partially matches'} your preference",
    })

    # Rating factor
    rating = restaurant.get("rating", 3.5)
    match_factors.append({
        "factor": "Rating",
        "score": round(rating / 5, 2),
        "description": f"Rated {rating}★ by Yelp users",
    })

    # Cuisine factor
    categories = [c.get("title", "") for c in restaurant.get("categories", [])]
    preferred = taste_dna.preferred_cuisines or []
    cuisine_match = any(
        any(p.lower() in cat.lower() for p in preferred)
        for cat in categories
    )
    match_factors.append({
        "factor": "Cuisine",
        "score": 1.0 if cuisine_match else 0.5,
        "description": f"Serves {', '.join(categories[:2])}",
    })

    return ExplainResponse(
        restaurant_id=request.restaurant_id,
        restaurant_name=restaurant.get("name", ""),
        explanation=f"This restaurant is a great match based on your TasteDNA profile!",
        match_factors=match_factors,
        twin_insights="Your Taste Twins also love restaurants with similar vibes.",
    )


@router.get("/predict")
async def predict_taste_trend(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Predict what cuisine/style user will crave next."""
    taste_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    if not taste_dna:
        raise TasteDNANotFoundException()

    # Simple prediction based on TasteDNA
    if taste_dna.adventure_score > 0.7:
        predicted_cuisine = "Fusion or Exotic"
        style = "Adventurous & Unique"
        reasoning = "Your high adventure score suggests you'll enjoy trying something new!"
    elif taste_dna.spice_tolerance > 0.7:
        predicted_cuisine = "Thai or Indian"
        style = "Spicy & Flavorful"
        reasoning = "Your spice tolerance indicates you might crave bold flavors."
    else:
        cuisines = taste_dna.preferred_cuisines or ["Italian"]
        predicted_cuisine = cuisines[0] if cuisines else "Comfort Food"
        style = taste_dna.ambiance_preference or "Casual"
        reasoning = "Based on your consistent preferences, you'll likely enjoy your favorites."

    return {
        "cuisine": predicted_cuisine,
        "restaurant_style": style,
        "confidence": 0.75,
        "reasoning": reasoning,
    }
