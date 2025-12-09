"""TasteDNA API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.redis_client import redis_client
from app.schemas.taste_dna import (
    QuizResponse,
    QuizSubmission,
    TasteDNAResponse,
    TasteDNACalculationResult,
    TasteDNACard,
)
from app.services.taste_dna_service import taste_dna_service
from app.services.twin_matching_service import twin_matching_service
from app.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import TasteDNANotFoundException

router = APIRouter()


@router.get("/quiz", response_model=QuizResponse)
async def get_quiz_questions(
    current_user: User = Depends(get_current_user),
):
    """Get all quiz questions for Taste DNA generation."""
    questions = taste_dna_service.get_quiz_questions()
    return QuizResponse(
        total_questions=len(questions),
        questions=questions,
    )


@router.post("/quiz/submit", response_model=TasteDNACalculationResult)
async def submit_quiz(
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit quiz answers and generate Taste DNA."""
    # Create/update TasteDNA
    taste_dna = await taste_dna_service.create_taste_dna(
        db, current_user.id, submission
    )

    # Store embedding and find twins
    await twin_matching_service.store_user_embedding(
        current_user.id, taste_dna
    )
    twins = await twin_matching_service.find_twins(
        db, current_user.id, taste_dna
    )
    await twin_matching_service.update_twin_relationships(
        db, current_user.id, twins
    )

    # Invalidate cache for the current user (who just submitted the quiz)
    current_user_cache_key = f"twins:{current_user.id}"
    await redis_client.delete(current_user_cache_key)

    # Invalidate cache for all users who have this user as a twin
    # So their twin lists will be refreshed on next request
    for twin in twins:
        twin_cache_key = f"twins:{twin['twin_id']}"
        await redis_client.delete(twin_cache_key)

    # Get top twin similarity
    top_similarity = twins[0]["similarity_score"] if twins else None

    return TasteDNACalculationResult(
        taste_dna=TasteDNAResponse.model_validate(taste_dna),
        twin_count=len(twins),
        top_twin_similarity=top_similarity,
    )


@router.get("/profile", response_model=TasteDNAResponse)
async def get_taste_dna_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's Taste DNA profile."""
    taste_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    if not taste_dna:
        raise TasteDNANotFoundException()
    return TasteDNAResponse.model_validate(taste_dna)


@router.post("/regenerate", response_model=TasteDNACalculationResult)
async def regenerate_taste_dna(
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retake quiz and regenerate Taste DNA."""
    # Same as submit, but explicitly for retaking
    return await submit_quiz(submission, current_user, db)


@router.get("/card", response_model=TasteDNACard)
async def get_taste_dna_card(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get shareable Taste DNA card data."""
    taste_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    if not taste_dna:
        raise TasteDNANotFoundException()

    twin_count = await twin_matching_service.get_twin_count(db, current_user.id)

    return TasteDNACard(
        user_name=current_user.name,
        adventure_score=taste_dna.adventure_score,
        spice_tolerance=taste_dna.spice_tolerance,
        price_sensitivity=taste_dna.price_sensitivity,
        cuisine_diversity=taste_dna.cuisine_diversity,
        ambiance_preference=taste_dna.ambiance_preference,
        top_cuisines=(taste_dna.preferred_cuisines or [])[:5],
        twin_count=twin_count,
    )
