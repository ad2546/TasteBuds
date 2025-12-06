"""Discovery and recommendation Pydantic schemas."""

from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.restaurant import RestaurantWithExplanation, RestaurantBase


class FeelingLuckyResponse(BaseModel):
    """Response for Feeling Lucky one-tap discovery."""

    restaurant: RestaurantWithExplanation
    twin_count: int  # Number of twins who endorsed this
    confidence: float = Field(..., ge=0.0, le=1.0)


class CompareOption(BaseModel):
    """A restaurant option in compare mode."""

    restaurant: RestaurantWithExplanation
    pros: List[str]
    cons: List[str]


class CompareResponse(BaseModel):
    """Response for compare mode (3 options)."""

    options: List[CompareOption]
    recommendation: str  # AI-generated recommendation text


class TrendingItem(BaseModel):
    """A trending restaurant among twins."""

    restaurant: RestaurantBase
    twin_visits: int
    trend_score: float


class TrendingResponse(BaseModel):
    """Response for trending among twins."""

    items: List[TrendingItem]
    time_period: str  # "this_week", "this_month"


class TastePrediction(BaseModel):
    """Predicted taste trend for user."""

    cuisine: str
    restaurant_style: str
    confidence: float
    reasoning: str


class ExplainRequest(BaseModel):
    """Request for restaurant explanation."""

    restaurant_id: str


class ExplainResponse(BaseModel):
    """Response with detailed explanation."""

    restaurant_id: str
    restaurant_name: str
    explanation: str
    match_factors: List[dict]  # [{factor: "Spice", score: 0.9, description: "..."}]
    twin_insights: Optional[str] = None


class DiscoveryFeedItem(BaseModel):
    """Item in discovery feed."""

    restaurant: RestaurantWithExplanation
    reason: str  # "twin_favorite", "matches_dna", "trending", "new_match"
    priority: int


class DiscoveryFeedResponse(BaseModel):
    """Response for discovery feed."""

    items: List[DiscoveryFeedItem]
    next_offset: Optional[int] = None
