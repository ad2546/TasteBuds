"""Gamification Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class ChallengeBase(BaseModel):
    """Base challenge schema."""

    title: str
    description: Optional[str] = None
    challenge_type: str  # twin_picks, cuisine_explore, adventure, streak
    target_count: int
    points_reward: int


class ChallengeResponse(ChallengeBase):
    """Response for a challenge."""

    id: str  # Changed from UUID to str to match database String(36)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    active: bool

    class Config:
        from_attributes = True


class UserChallengeProgress(BaseModel):
    """User's progress on a challenge."""

    challenge: ChallengeResponse
    progress: int
    completed: bool
    completed_at: Optional[datetime] = None
    percentage: float = Field(..., ge=0.0, le=100.0)


class ChallengeListResponse(BaseModel):
    """List of challenges with user progress."""

    active_challenges: List[UserChallengeProgress]
    completed_challenges: List[UserChallengeProgress]


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""

    rank: int
    user_id: UUID
    user_name: str
    avatar_url: Optional[str] = None
    score: float


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""

    board_type: str  # adventure, weekly, all_time
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    user_score: Optional[float] = None


class AchievementResponse(BaseModel):
    """Achievement response."""

    id: UUID
    achievement_type: str
    title: str
    description: str
    icon: str
    earned_at: datetime

    class Config:
        from_attributes = True


class UserAchievementsResponse(BaseModel):
    """User's achievements response."""

    achievements: List[AchievementResponse]
    total_points: int


class ShareCardRequest(BaseModel):
    """Request to generate shareable card."""

    include_twins: bool = True
    include_top_cuisines: bool = True
    style: str = "default"  # default, minimal, colorful


class ShareCardResponse(BaseModel):
    """Response with shareable card data."""

    card_url: Optional[str] = None
    card_data: dict  # Data for client-side rendering
    share_text: str
