"""Yelp AI Chat API endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.services.yelp_ai_service import yelp_ai_service
from app.services.taste_dna_service import taste_dna_service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


class ChatRequest(BaseModel):
    """Request to chat with Yelp AI."""
    query: str = Field(..., max_length=1000, description="Natural language query")
    chat_id: Optional[str] = Field(None, description="Conversation ID to continue")
    latitude: Optional[float] = Field(None, description="User latitude")
    longitude: Optional[float] = Field(None, description="User longitude")
    use_taste_dna: bool = Field(True, description="Whether to enhance query with TasteDNA")


class CompareRequest(BaseModel):
    """Request to compare restaurants."""
    restaurant_ids: List[str] = Field(..., max_items=3, description="Restaurant IDs to compare")
    criteria: str = Field("overall experience", description="What to compare")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RecommendationRequest(BaseModel):
    """Request for occasion-based recommendations."""
    occasion: str = Field(..., description="Type of occasion (date night, birthday, etc.)")
    party_size: Optional[int] = Field(None, ge=1, le=20)
    date_time: Optional[str] = Field(None, description="When to go")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RestaurantQuestionRequest(BaseModel):
    """Request to ask about a specific restaurant."""
    restaurant_id: str = Field(..., description="Yelp business ID")
    question: str = Field(..., max_length=500, description="Question about the restaurant")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@router.post("/chat")
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Chat with Yelp AI for restaurant discovery and questions.

    This endpoint supports natural language queries like:
    - "Find me a romantic Italian restaurant"
    - "What's a good place for brunch in downtown?"
    - "Show me vegan-friendly spots with outdoor seating"
    """
    # Get user's TasteDNA if requested
    taste_dna = None
    if request.use_taste_dna:
        taste_dna_obj = await taste_dna_service.get_user_taste_dna(db, current_user.id)
        if taste_dna_obj:
            taste_dna = taste_dna_obj.to_dict()

    # Call Yelp AI with enhanced context
    if taste_dna and not request.chat_id:  # First message with TasteDNA
        result = await yelp_ai_service.search_with_context(
            query=request.query,
            taste_dna=taste_dna,
            latitude=request.latitude,
            longitude=request.longitude,
        )
    else:
        result = await yelp_ai_service.chat(
            query=request.query,
            chat_id=request.chat_id,
            latitude=request.latitude,
            longitude=request.longitude,
        )

    return result


@router.post("/compare")
async def compare_restaurants(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Use AI to compare multiple restaurants.

    Example: Compare 2-3 restaurants on price, atmosphere, food quality, etc.
    """
    result = await yelp_ai_service.compare_restaurants(
        restaurant_ids=request.restaurant_ids,
        comparison_criteria=request.criteria,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    return result


@router.post("/recommend")
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI-powered recommendations for specific occasions.

    Examples:
    - "date night" for 2 people on Friday evening
    - "birthday celebration" for 10 people
    - "business lunch" near downtown
    """
    # Get user's TasteDNA for personalization
    taste_dna = None
    taste_dna_obj = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    if taste_dna_obj:
        taste_dna = taste_dna_obj.to_dict()

    result = await yelp_ai_service.get_restaurant_recommendations(
        occasion=request.occasion,
        party_size=request.party_size,
        date_time=request.date_time,
        taste_dna=taste_dna,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    return result


@router.post("/ask")
async def ask_about_restaurant(
    request: RestaurantQuestionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Ask specific questions about a restaurant.

    Examples:
    - "Is this place good for kids?"
    - "Do they have vegetarian options?"
    - "What's their most popular dish?"
    - "Is parking available?"
    """
    result = await yelp_ai_service.ask_about_restaurant(
        restaurant_id=request.restaurant_id,
        question=request.question,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    return result


@router.get("/smart-search")
async def smart_search(
    query: str = Query(..., description="Natural language search query"),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Smart search that combines natural language with TasteDNA.

    This is a simplified endpoint for quick searches without managing chat sessions.
    """
    # Get user's TasteDNA
    taste_dna = None
    taste_dna_obj = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    if taste_dna_obj:
        taste_dna = taste_dna_obj.to_dict()

    result = await yelp_ai_service.search_with_context(
        query=query,
        taste_dna=taste_dna,
        latitude=latitude,
        longitude=longitude,
    )
    return result
