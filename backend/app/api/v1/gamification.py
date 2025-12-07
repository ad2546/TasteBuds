"""Gamification API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.session import get_db
from app.db.redis_client import redis_client
from app.schemas.gamification import (
    ChallengeResponse,
    UserChallengeProgress,
    ChallengeListResponse,
    LeaderboardResponse,
    LeaderboardEntry,
    ShareCardRequest,
    ShareCardResponse,
)
from app.services.taste_dna_service import taste_dna_service
from app.services.twin_matching_service import twin_matching_service
from app.dependencies import get_current_user
from app.models.user import User
from app.models.challenge import Challenge, UserChallenge, UserAchievement
from app.models.taste_dna import TasteDNA

router = APIRouter()


# Predefined challenges
DEFAULT_CHALLENGES = [
    {
        "title": "Twin Explorer",
        "description": "Try 5 restaurants loved by your Taste Twins",
        "challenge_type": "twin_picks",
        "target_count": 5,
        "points_reward": 100,
    },
    {
        "title": "Cuisine Adventurer",
        "description": "Try 3 different cuisine types this week",
        "challenge_type": "cuisine_explore",
        "target_count": 3,
        "points_reward": 75,
    },
    {
        "title": "Spice Pioneer",
        "description": "Visit 3 restaurants known for spicy food",
        "challenge_type": "spice_challenge",
        "target_count": 3,
        "points_reward": 50,
    },
    {
        "title": "Social Foodie",
        "description": "Share your TasteDNA card 3 times",
        "challenge_type": "social_share",
        "target_count": 3,
        "points_reward": 30,
    },
]


@router.get("/challenges", response_model=ChallengeListResponse)
async def get_challenges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all challenges with user's progress."""
    # Get all active challenges
    result = await db.execute(
        select(Challenge).where(Challenge.active == True)
    )
    challenges = result.scalars().all()

    # If no challenges exist, create defaults
    if not challenges:
        for challenge_data in DEFAULT_CHALLENGES:
            challenge = Challenge(**challenge_data)
            db.add(challenge)
        await db.commit()

        result = await db.execute(
            select(Challenge).where(Challenge.active == True)
        )
        challenges = result.scalars().all()

    # Get user's progress on each challenge
    active_challenges = []
    completed_challenges = []

    for challenge in challenges:
        # Get or create user challenge progress
        progress_result = await db.execute(
            select(UserChallenge)
            .where(UserChallenge.user_id == current_user.id)
            .where(UserChallenge.challenge_id == challenge.id)
        )
        user_challenge = progress_result.scalar_one_or_none()

        if not user_challenge:
            user_challenge = UserChallenge(
                user_id=current_user.id,
                challenge_id=challenge.id,
                progress=0,
                completed=False,
            )
            db.add(user_challenge)
            await db.flush()  # Ensure defaults are applied

        # Ensure completed is never None
        if user_challenge.completed is None:
            user_challenge.completed = False

        progress = UserChallengeProgress(
            challenge=ChallengeResponse.model_validate(challenge),
            progress=user_challenge.progress,
            completed=user_challenge.completed,
            completed_at=user_challenge.completed_at,
            percentage=min(100.0, (user_challenge.progress / challenge.target_count) * 100),
        )

        if user_challenge.completed:
            completed_challenges.append(progress)
        else:
            active_challenges.append(progress)

    await db.commit()

    return ChallengeListResponse(
        active_challenges=active_challenges,
        completed_challenges=completed_challenges,
    )


@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a challenge."""
    # Check if challenge exists
    result = await db.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()

    if not challenge:
        return {"error": "Challenge not found"}

    # Check if already joined
    progress_result = await db.execute(
        select(UserChallenge)
        .where(UserChallenge.user_id == current_user.id)
        .where(UserChallenge.challenge_id == challenge_id)
    )
    existing = progress_result.scalar_one_or_none()

    if existing:
        return {"message": "Already joined this challenge"}

    user_challenge = UserChallenge(
        user_id=current_user.id,
        challenge_id=challenge_id,
    )
    db.add(user_challenge)
    await db.commit()

    return {"message": "Joined challenge successfully"}


@router.post("/challenges/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: str,
    increment: int = Query(1, ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update progress on a challenge."""
    result = await db.execute(
        select(UserChallenge)
        .where(UserChallenge.user_id == current_user.id)
        .where(UserChallenge.challenge_id == challenge_id)
    )
    user_challenge = result.scalar_one_or_none()

    if not user_challenge:
        return {"error": "Not joined this challenge"}

    if user_challenge.completed:
        return {"message": "Challenge already completed"}

    # Get challenge for target
    challenge_result = await db.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = challenge_result.scalar_one()

    # Update progress
    user_challenge.progress += increment

    # Check completion
    if user_challenge.progress >= challenge.target_count:
        from datetime import datetime
        user_challenge.completed = True
        user_challenge.completed_at = datetime.utcnow()

        # Award points (update leaderboard)
        await redis_client.connect()
        current_score = await redis_client.get(f"user:score:{current_user.id}") or 0
        new_score = float(current_score) + challenge.points_reward
        await redis_client.update_leaderboard(str(current_user.id), new_score)

    await db.commit()

    return {
        "progress": user_challenge.progress,
        "completed": user_challenge.completed,
        "target": challenge.target_count,
    }


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    board_type: str = Query("adventure", description="Leaderboard type"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get leaderboard rankings."""
    await redis_client.connect()

    # Get leaderboard from Redis
    leaderboard_data = await redis_client.get_leaderboard(board_type, limit)

    # Get user names for each entry
    entries = []
    for i, entry in enumerate(leaderboard_data):
        user_result = await db.execute(
            select(User).where(User.id == UUID(entry["user_id"]))
        )
        user = user_result.scalar_one_or_none()

        if user:
            entries.append(LeaderboardEntry(
                rank=i + 1,
                user_id=UUID(entry["user_id"]),
                user_name=user.name,
                avatar_url=user.avatar_url,
                score=entry["score"],
            ))

    # Get current user's rank
    user_rank = await redis_client.get_user_rank(str(current_user.id), board_type)
    user_score_data = await redis_client.get(f"user:score:{current_user.id}")
    user_score = float(user_score_data) if user_score_data else 0.0

    return LeaderboardResponse(
        board_type=board_type,
        entries=entries,
        user_rank=user_rank,
        user_score=user_score,
    )


@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's achievements."""
    result = await db.execute(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
        .order_by(UserAchievement.earned_at.desc())
    )
    achievements = result.scalars().all()

    # Define achievement metadata
    achievement_info = {
        "first_quiz": {"title": "Taste Pioneer", "description": "Completed your first Taste DNA quiz", "icon": "🧬"},
        "first_twin": {"title": "Twin Found", "description": "Found your first Taste Twin", "icon": "👯"},
        "adventurer": {"title": "Food Adventurer", "description": "Tried 10 different restaurants", "icon": "🗺️"},
        "social_butterfly": {"title": "Social Butterfly", "description": "Shared your TasteDNA card", "icon": "🦋"},
        "spice_master": {"title": "Spice Master", "description": "Visited 5 spicy restaurants", "icon": "🌶️"},
        "first_visit": {"title": "First Step", "description": "Marked your first restaurant as visited", "icon": "🎯"},
        "explorer_5": {"title": "Explorer", "description": "Visited 5 restaurants", "icon": "🗺️"},
        "explorer_10": {"title": "Food Tourist", "description": "Visited 10 restaurants", "icon": "✈️"},
        "explorer_25": {"title": "Gastronome", "description": "Visited 25 restaurants", "icon": "👨‍🍳"},
        "explorer_50": {"title": "Culinary Legend", "description": "Visited 50 restaurants", "icon": "🏆"},
    }

    return {
        "achievements": [
            {
                "id": str(a.id),
                "achievement_type": a.achievement_type,
                "title": achievement_info.get(a.achievement_type, {}).get("title", a.achievement_type),
                "description": achievement_info.get(a.achievement_type, {}).get("description", ""),
                "icon": achievement_info.get(a.achievement_type, {}).get("icon", "🏆"),
                "earned_at": a.earned_at,
            }
            for a in achievements
        ],
        "total_points": len(achievements) * 25,  # 25 points per achievement
    }


@router.post("/share/taste-card", response_model=ShareCardResponse)
async def generate_share_card(
    request: ShareCardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate shareable TasteDNA card."""
    taste_dna = await taste_dna_service.get_user_taste_dna(db, current_user.id)
    twin_count = await twin_matching_service.get_twin_count(db, current_user.id)

    if not taste_dna:
        return ShareCardResponse(
            card_data={},
            share_text="I haven't discovered my TasteDNA yet! Try TasteSync to find yours.",
        )

    # Build card data for client-side rendering
    card_data = {
        "user_name": current_user.name,
        "avatar_url": current_user.avatar_url,
        "adventure_score": taste_dna.adventure_score,
        "spice_tolerance": taste_dna.spice_tolerance,
        "price_sensitivity": taste_dna.price_sensitivity,
        "cuisine_diversity": taste_dna.cuisine_diversity,
        "ambiance": taste_dna.ambiance_preference,
        "style": request.style,
    }

    if request.include_twins:
        card_data["twin_count"] = twin_count

    if request.include_top_cuisines:
        card_data["top_cuisines"] = (taste_dna.preferred_cuisines or [])[:3]

    # Generate share text
    adventure_desc = "adventurous" if taste_dna.adventure_score > 0.7 else "classic"
    spice_desc = "spice lover" if taste_dna.spice_tolerance > 0.7 else "mild fan"

    share_text = (
        f"🧬 My TasteDNA: I'm a {adventure_desc} {spice_desc} with "
        f"{twin_count} Taste Twins! "
        f"Discover your food personality with TasteSync! #TasteDNA #TasteSync"
    )

    return ShareCardResponse(
        card_url=None,  # Would be generated URL in production
        card_data=card_data,
        share_text=share_text,
    )
