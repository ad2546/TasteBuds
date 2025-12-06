"""Challenge and achievement database models."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


class Challenge(Base):
    """Model for gamification challenges."""

    __tablename__ = "challenges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    challenge_type = Column(String(50), nullable=True)  # twin_picks, cuisine_explore, adventure, etc.
    target_count = Column(Integer, nullable=True)
    points_reward = Column(Integer, default=0)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user_challenges = relationship("UserChallenge", back_populates="challenge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Challenge {self.title}>"


class UserChallenge(Base):
    """Model for user's challenge progress."""

    __tablename__ = "user_challenges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(String(36), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    progress = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_challenges")
    challenge = relationship("Challenge", back_populates="user_challenges")

    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="unique_user_challenge"),
    )

    def __repr__(self):
        return f"<UserChallenge {self.user_id} -> {self.challenge_id}>"


class UserAchievement(Base):
    """Model for user achievements."""

    __tablename__ = "user_achievements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_type = Column(String(100), nullable=False)
    achievement_data = Column(JSON, nullable=True)
    earned_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="achievements")

    def __repr__(self):
        return f"<UserAchievement {self.user_id} -> {self.achievement_type}>"
