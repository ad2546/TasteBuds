"""Date Night API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.db.session import get_db
from app.services.taste_dna_service import taste_dna_service
from app.services.yelp_service import yelp_service
from app.services.yelp_ai_service import yelp_ai_service
from app.dependencies import get_current_user
from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.models.date_night import DateNightPairing
from app.core.exceptions import TasteDNANotFoundException

router = APIRouter()


class PairRequest(BaseModel):
    """Request to pair with another user."""
    partner_id: UUID


class CompatibilityResponse(BaseModel):
    """Compatibility response."""
    compatibility_score: float
    shared_cuisines: list
    compromise_cuisines: list
    analysis: str


@router.post("/pair")
async def pair_for_date_night(
    request: PairRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pair two users for date night."""
    # Get both users' TasteDNA
    user1_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    user2_dna = await taste_dna_service.get_user_taste_dna(db, request.partner_id)

    if not user1_dna or not user2_dna:
        raise TasteDNANotFoundException()

    # Calculate compatibility
    compatibility = _calculate_compatibility(user1_dna, user2_dna)

    # Create or update pairing
    result = await db.execute(
        select(DateNightPairing)
        .where(
            and_(
                DateNightPairing.user1_id == current_user.id,
                DateNightPairing.user2_id == request.partner_id,
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.compatibility_score = compatibility["score"]
        existing.merged_preferences = compatibility["merged"]
        existing.active = True
    else:
        pairing = DateNightPairing(
            user1_id=current_user.id,
            user2_id=request.partner_id,
            compatibility_score=compatibility["score"],
            merged_preferences=compatibility["merged"],
        )
        db.add(pairing)

    await db.commit()

    return {
        "message": "Pairing created successfully",
        "compatibility_score": compatibility["score"],
    }


@router.get("/compatibility")
async def get_compatibility(
    partner_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get compatibility score with a partner."""
    user1_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    user2_dna = await taste_dna_service.get_user_taste_dna(db, partner_id)

    if not user1_dna or not user2_dna:
        raise TasteDNANotFoundException()

    compatibility = _calculate_compatibility(user1_dna, user2_dna)

    # Get cuisines from merged preferences for compromise
    all_cuisines = set(user1_dna.preferred_cuisines or []) | set(user2_dna.preferred_cuisines or [])
    compromise_cuisines = list(all_cuisines - set(compatibility["common_cuisines"]))[:3]

    # Generate analysis text
    score = compatibility["score"]
    if score >= 0.8:
        analysis = "Excellent match! You both have very similar taste preferences."
    elif score >= 0.6:
        analysis = "Good compatibility! You share several common preferences."
    else:
        analysis = "Some differences in taste, but that makes for interesting dining adventures!"

    return CompatibilityResponse(
        compatibility_score=compatibility["score"],
        shared_cuisines=compatibility["common_cuisines"],
        compromise_cuisines=compromise_cuisines,
        analysis=analysis,
    )


@router.get("/suggestions")
async def get_date_night_suggestions(
    partner_id: UUID = Query(...),
    location: str = Query(...),
    limit: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-powered compatible restaurant suggestions for date night."""
    user1_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    user2_dna = await taste_dna_service.get_user_taste_dna(db, partner_id)

    if not user1_dna or not user2_dna:
        raise TasteDNANotFoundException()

    # Convert TasteDNA models to dictionaries for AI service
    user1_dna_dict = _taste_dna_to_dict(user1_dna)
    user2_dna_dict = _taste_dna_to_dict(user2_dna)

    # Get AI-powered date night recommendations
    ai_response = await yelp_ai_service.get_date_night_recommendations(
        user1_taste_dna=user1_dna_dict,
        user2_taste_dna=user2_dna_dict,
        location=location,
    )

    # Extract businesses from AI response
    ai_businesses = ai_response.get("businesses", [])

    # Calculate compatibility for scoring
    compatibility = _calculate_compatibility(user1_dna, user2_dna)

    # Also get fallback recommendations using traditional search
    merged = compatibility["merged"]
    fallback_results = await yelp_service.search_businesses(
        term="restaurants",
        location=location,
        categories=",".join(merged.get("preferred_cuisines", [])[:3]) or None,
        price=_get_merged_price_range(merged.get("price_sensitivity", 0.5)),
        sort_by="rating",
        limit=limit * 2,
    )

    # Combine AI recommendations with fallback (prioritize AI results)
    all_restaurants = ai_businesses + fallback_results.get("businesses", [])

    # Remove duplicates (keep first occurrence)
    seen_ids = set()
    unique_restaurants = []
    for restaurant in all_restaurants:
        restaurant_id = restaurant.get("id") or restaurant.get("restaurant_id")
        if restaurant_id and restaurant_id not in seen_ids:
            seen_ids.add(restaurant_id)
            unique_restaurants.append(restaurant)

    # Score restaurants for both users
    suggestions = []
    for restaurant in unique_restaurants[:limit * 3]:  # Process more for better categorization
        try:
            score1 = _score_restaurant_for_user(restaurant, user1_dna)
            score2 = _score_restaurant_for_user(restaurant, user2_dna)

            # Combined score (both partners should like it)
            combined_score = (score1 + score2) / 2 * min(score1, score2)

            suggestions.append({
                "restaurant": restaurant,
                "combined_score": round(combined_score, 2),
                "user1_score": round(score1, 2),
                "user2_score": round(score2, 2),
                "why_it_works": _explain_date_match(restaurant, compatibility),
                "from_ai": restaurant in ai_businesses,  # Mark AI-recommended restaurants
            })
        except Exception as e:
            # Skip restaurants that cause errors (e.g., missing required fields)
            print(f"Error scoring restaurant {restaurant.get('id', 'unknown')}: {e}")
            continue

    # Ensure we have at least some suggestions
    if not suggestions:
        # Return empty response if no valid restaurants found
        return {
            "perfect_matches": [],
            "you_will_love": [],
            "they_will_love": [],
            "ai_insight": ai_response.get("text", "We couldn't find matching restaurants at this time. Please try a different location or criteria."),
        }

    # Sort by combined score (with AI recommendations getting slight boost)
    suggestions.sort(key=lambda x: (x["from_ai"], x["combined_score"]), reverse=True)

    # Categorize suggestions
    perfect_matches = []
    you_will_love = []
    they_will_love = []

    for sug in suggestions:
        # Perfect match: both scores are high
        if sug["user1_score"] >= 0.7 and sug["user2_score"] >= 0.7:
            if len(perfect_matches) < limit:
                perfect_matches.append(sug["restaurant"])
        # User 1 will love: their score is significantly higher
        elif sug["user1_score"] > sug["user2_score"] + 0.15:
            if len(you_will_love) < limit:
                you_will_love.append(sug["restaurant"])
        # User 2 will love: their score is significantly higher
        elif sug["user2_score"] > sug["user1_score"] + 0.15:
            if len(they_will_love) < limit:
                they_will_love.append(sug["restaurant"])
        # Default to perfect matches if scores are close
        else:
            if len(perfect_matches) < limit:
                perfect_matches.append(sug["restaurant"])

    return {
        "perfect_matches": perfect_matches[:limit],
        "you_will_love": you_will_love[:limit],
        "they_will_love": they_will_love[:limit],
        "ai_insight": ai_response.get("text", ""),  # Include AI's explanation
    }


@router.delete("/unpair")
async def unpair(
    partner_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove date night pairing."""
    result = await db.execute(
        select(DateNightPairing)
        .where(
            and_(
                DateNightPairing.user1_id == current_user.id,
                DateNightPairing.user2_id == partner_id,
            )
        )
    )
    pairing = result.scalar_one_or_none()

    if pairing:
        pairing.active = False
        await db.commit()

    return {"message": "Pairing removed"}


def _taste_dna_to_dict(dna: TasteDNA) -> dict:
    """Convert TasteDNA model to dictionary for AI service."""
    return {
        "preferred_cuisines": dna.preferred_cuisines or [],
        "price_sensitivity": dna.price_sensitivity,
        "ambiance_preference": dna.ambiance_preference,
        "adventure_score": dna.adventure_score,
        "spice_tolerance": dna.spice_tolerance,
        "cuisine_diversity": dna.cuisine_diversity,
    }


def _calculate_compatibility(dna1: TasteDNA, dna2: TasteDNA) -> dict:
    """Calculate compatibility between two TasteDNA profiles."""
    # Score differences
    adventure_diff = abs(dna1.adventure_score - dna2.adventure_score)
    spice_diff = abs(dna1.spice_tolerance - dna2.spice_tolerance)
    price_diff = abs(dna1.price_sensitivity - dna2.price_sensitivity)
    diversity_diff = abs(dna1.cuisine_diversity - dna2.cuisine_diversity)

    # Compatibility is higher when differences are lower
    score = 1 - (adventure_diff + spice_diff + price_diff + diversity_diff) / 4

    # Common cuisines bonus
    cuisines1 = set(dna1.preferred_cuisines or [])
    cuisines2 = set(dna2.preferred_cuisines or [])
    common_cuisines = list(cuisines1 & cuisines2)
    if common_cuisines:
        score = min(1.0, score + 0.1 * len(common_cuisines))

    # Same ambiance bonus
    if dna1.ambiance_preference == dna2.ambiance_preference:
        score = min(1.0, score + 0.1)

    # Merged preferences (average or intersection)
    merged = {
        "adventure_score": (dna1.adventure_score + dna2.adventure_score) / 2,
        "spice_tolerance": min(dna1.spice_tolerance, dna2.spice_tolerance),  # Use lower
        "price_sensitivity": (dna1.price_sensitivity + dna2.price_sensitivity) / 2,
        "cuisine_diversity": (dna1.cuisine_diversity + dna2.cuisine_diversity) / 2,
        "preferred_cuisines": common_cuisines or list(cuisines1 | cuisines2)[:5],
        "ambiance_preference": dna1.ambiance_preference or dna2.ambiance_preference,
    }

    # Identify differences
    differences = []
    if adventure_diff > 0.3:
        differences.append("Adventure levels differ")
    if spice_diff > 0.3:
        differences.append("Spice preferences differ")
    if price_diff > 0.3:
        differences.append("Budget preferences differ")

    return {
        "score": round(score, 2),
        "common_cuisines": common_cuisines,
        "merged": merged,
        "differences": differences,
    }


def _get_merged_price_range(price_sensitivity: float) -> str:
    """Get price range string from sensitivity."""
    if price_sensitivity > 0.7:
        return "1,2"
    elif price_sensitivity > 0.4:
        return "2,3"
    else:
        return "3,4"


def _score_restaurant_for_user(restaurant: dict, dna: TasteDNA) -> float:
    """Score a restaurant for a single user."""
    score = 0.5

    # Price match
    price = restaurant.get("price", "$$")
    price_level = len(price) / 4
    score += (1 - abs(dna.price_sensitivity - (1 - price_level))) * 0.3

    # Rating
    rating = restaurant.get("rating", 3.5)
    score += (rating / 5) * 0.2

    # Category match
    categories = [c.get("alias", "") for c in restaurant.get("categories", [])]
    preferred = [c.lower() for c in (dna.preferred_cuisines or [])]
    if any(cat in preferred for cat in categories):
        score += 0.3

    return min(1.0, score)


def _explain_date_match(restaurant: dict, compatibility: dict) -> str:
    """Generate explanation for why restaurant works for date."""
    reasons = []

    price = restaurant.get("price", "$$")
    rating = restaurant.get("rating", 0)

    if rating >= 4.0:
        reasons.append(f"Highly rated ({rating}★)")

    common = compatibility.get("common_cuisines", [])
    categories = [c.get("title", "") for c in restaurant.get("categories", [])]
    if any(c.lower() in [cat.lower() for cat in categories] for c in common):
        reasons.append("Matches your shared cuisine tastes")

    reasons.append(f"Price point ({price}) works for both")

    return " • ".join(reasons) if reasons else "Great atmosphere for a date!"
