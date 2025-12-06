"""User database model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """User model for storing user account information."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    embedding_vector_id = Column(String(100), nullable=True)  # Pinecone reference
    quiz_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    taste_dna = relationship("TasteDNA", back_populates="user", uselist=False, cascade="all, delete-orphan")
    interaction_logs = relationship("InteractionLog", back_populates="user", cascade="all, delete-orphan")
    saved_restaurants = relationship("SavedRestaurant", back_populates="user", cascade="all, delete-orphan")
    user_challenges = relationship("UserChallenge", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    image_searches = relationship("ImageSearch", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
