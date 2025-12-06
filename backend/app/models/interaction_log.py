"""Interaction log database model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.db.session import Base


class InteractionLog(Base):
    """Model for logging user interactions with restaurants."""

    __tablename__ = "interaction_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    restaurant_id = Column(String(100), nullable=False)  # Yelp business ID
    action_type = Column(String(50), nullable=False)  # view, save, book, dismiss, like
    context = Column(String(100), nullable=True)  # lucky, compare, date_night, search, twins
    session_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="interaction_logs")

    __table_args__ = (
        Index("idx_interaction_user", "user_id"),
        Index("idx_interaction_restaurant", "restaurant_id"),
        Index("idx_interaction_action", "action_type"),
    )

    def __repr__(self):
        return f"<InteractionLog {self.user_id} {self.action_type} {self.restaurant_id}>"
