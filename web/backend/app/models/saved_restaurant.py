"""Saved restaurant database model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


class SavedRestaurant(Base):
    """Model for user's saved restaurants."""

    __tablename__ = "saved_restaurants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    restaurant_id = Column(String(100), nullable=False)  # Yelp business ID
    restaurant_name = Column(String(255), nullable=True)
    restaurant_data = Column(JSON, nullable=True)  # Cached Yelp data
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="saved_restaurants")

    __table_args__ = (
        UniqueConstraint("user_id", "restaurant_id", name="unique_user_restaurant"),
    )

    def __repr__(self):
        return f"<SavedRestaurant {self.user_id} -> {self.restaurant_name}>"
