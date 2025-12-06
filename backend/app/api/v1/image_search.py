"""Image Search API endpoints."""

from typing import Optional
import base64

from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.session import get_db
from app.services.yelp_service import yelp_service
from app.dependencies import get_current_user
from app.models.user import User
from app.models.image_search import ImageSearch

router = APIRouter()


class ImageSearchResult(BaseModel):
    """Result from image search."""
    detected_dish: str
    detected_cuisine: str
    confidence: float
    restaurants: list


@router.post("/upload")
async def upload_and_search(
    file: UploadFile = File(...),
    location: str = Query(..., description="Location to search restaurants"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload food image and find similar restaurants."""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    # Read image data
    image_data = await file.read()

    # In production, you would:
    # 1. Upload to cloud storage (S3, etc.)
    # 2. Run through food classification model (CLIP, custom CNN, etc.)
    # 3. Extract dish and cuisine type

    # For hackathon demo, simulate food detection
    detected = _simulate_food_detection(file.filename)

    # Search for restaurants serving similar food
    search_results = await yelp_service.search_businesses(
        term=detected["dish"],
        location=location,
        categories=detected["category"],
        sort_by="rating",
        limit=10,
    )

    restaurants = search_results.get("businesses", [])

    # Store search in history
    search_record = ImageSearch(
        user_id=current_user.id,
        detected_dish=detected["dish"],
        detected_cuisine=detected["cuisine"],
        confidence_score=detected["confidence"],
        results=[
            {"id": r.get("id"), "name": r.get("name")}
            for r in restaurants[:5]
        ],
    )
    db.add(search_record)
    await db.commit()

    return {
        "detected_dish": detected["dish"],
        "detected_cuisine": detected["cuisine"],
        "confidence": detected["confidence"],
        "restaurants": [
            {
                **r,
                "match_reason": f"Serves {detected['dish']} and similar dishes",
            }
            for r in restaurants
        ],
    }


@router.get("/results/{search_id}")
async def get_search_results(
    search_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get results from a previous image search."""
    from uuid import UUID
    result = await db.execute(
        select(ImageSearch)
        .where(ImageSearch.id == UUID(search_id))
        .where(ImageSearch.user_id == current_user.id)
    )
    search = result.scalar_one_or_none()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found",
        )

    return {
        "id": str(search.id),
        "detected_dish": search.detected_dish,
        "detected_cuisine": search.detected_cuisine,
        "confidence": search.confidence_score,
        "results": search.results,
        "created_at": search.created_at,
    }


@router.get("/history")
async def get_search_history(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's image search history."""
    result = await db.execute(
        select(ImageSearch)
        .where(ImageSearch.user_id == current_user.id)
        .order_by(ImageSearch.created_at.desc())
        .limit(limit)
    )
    searches = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "detected_dish": s.detected_dish,
            "detected_cuisine": s.detected_cuisine,
            "confidence": s.confidence_score,
            "result_count": len(s.results or []),
            "created_at": s.created_at,
        }
        for s in searches
    ]


def _simulate_food_detection(filename: str) -> dict:
    """Simulate food detection for demo purposes."""
    # In production, this would use a real ML model

    # Simple keyword-based detection from filename
    filename_lower = filename.lower() if filename else ""

    food_mappings = {
        "pizza": {"dish": "Pizza", "cuisine": "Italian", "category": "pizza"},
        "sushi": {"dish": "Sushi", "cuisine": "Japanese", "category": "sushi"},
        "burger": {"dish": "Burger", "cuisine": "American", "category": "burgers"},
        "taco": {"dish": "Tacos", "cuisine": "Mexican", "category": "mexican"},
        "curry": {"dish": "Curry", "cuisine": "Indian", "category": "indpak"},
        "ramen": {"dish": "Ramen", "cuisine": "Japanese", "category": "ramen"},
        "pasta": {"dish": "Pasta", "cuisine": "Italian", "category": "italian"},
        "pho": {"dish": "Pho", "cuisine": "Vietnamese", "category": "vietnamese"},
        "dim sum": {"dish": "Dim Sum", "cuisine": "Chinese", "category": "dimsum"},
        "pad thai": {"dish": "Pad Thai", "cuisine": "Thai", "category": "thai"},
    }

    for keyword, mapping in food_mappings.items():
        if keyword in filename_lower:
            return {
                "dish": mapping["dish"],
                "cuisine": mapping["cuisine"],
                "category": mapping["category"],
                "confidence": 0.85,
            }

    # Default fallback
    return {
        "dish": "Restaurant Food",
        "cuisine": "Various",
        "category": "restaurants",
        "confidence": 0.6,
    }
