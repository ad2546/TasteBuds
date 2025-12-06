"""Image search database model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


class ImageSearch(Base):
    """Model for storing reverse image search history."""

    __tablename__ = "image_searches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=True)
    detected_dish = Column(String(200), nullable=True)
    detected_cuisine = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)
    results = Column(JSON, nullable=True)  # Matched restaurants
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="image_searches")

    def __repr__(self):
        return f"<ImageSearch {self.user_id} -> {self.detected_dish}>"
