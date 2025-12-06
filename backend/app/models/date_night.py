"""Date night pairing database model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, Float, Boolean, DateTime, ForeignKey, String, JSON

from app.db.session import Base


class DateNightPairing(Base):
    """Model for date night pairings between two users."""

    __tablename__ = "date_night_pairings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user1_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    compatibility_score = Column(Float, nullable=True)
    merged_preferences = Column(JSON, nullable=True)  # Combined TasteDNA preferences
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DateNightPairing {self.user1_id} + {self.user2_id}>"
