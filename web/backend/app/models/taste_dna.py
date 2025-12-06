"""TasteDNA database model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


class TasteDNA(Base):
    """TasteDNA model storing user's taste profile."""

    __tablename__ = "taste_dna"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Core TasteDNA metrics (0.0 to 1.0)
    adventure_score = Column(Float, nullable=False, default=0.5)
    spice_tolerance = Column(Float, nullable=False, default=0.5)
    price_sensitivity = Column(Float, nullable=False, default=0.5)
    cuisine_diversity = Column(Float, nullable=False, default=0.5)

    # Categorical preference
    ambiance_preference = Column(String(50), nullable=True)  # Casual, Upscale, Cozy, Trendy, etc.

    # JSON fields for complex preferences
    preferred_cuisines = Column(JSON, nullable=True, default=list)  # ["Italian", "Japanese", ...]
    dietary_restrictions = Column(JSON, nullable=True, default=list)  # ["vegetarian", "gluten-free", ...]
    quiz_answers = Column(JSON, nullable=True)  # Raw quiz responses

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="taste_dna")

    def to_vector(self) -> list:
        """Convert TasteDNA to a feature vector for embedding."""
        return [
            self.adventure_score,
            self.spice_tolerance,
            self.price_sensitivity,
            self.cuisine_diversity,
        ]

    def to_dict(self) -> dict:
        """Convert TasteDNA to dictionary."""
        return {
            "adventure": self.adventure_score,
            "spice": self.spice_tolerance,
            "ambiance": self.ambiance_preference,
            "price_sensitivity": self.price_sensitivity,
            "cuisine_diversity": self.cuisine_diversity,
            "preferred_cuisines": self.preferred_cuisines or [],
            "dietary_restrictions": self.dietary_restrictions or [],
        }

    def __repr__(self):
        return f"<TasteDNA user_id={self.user_id}>"
