"""Twin relationship database model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, Float, DateTime, ForeignKey, UniqueConstraint, Index, String, JSON

from app.db.session import Base


class TwinRelationship(Base):
    """Model for storing Taste Twin relationships between users."""

    __tablename__ = "twin_relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    twin_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    common_cuisines = Column(JSON, nullable=True)  # Shared cuisine preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "twin_user_id", name="unique_twin_pair"),
        Index("idx_twin_user", "user_id"),
        Index("idx_twin_score", "similarity_score"),
    )

    def __repr__(self):
        return f"<TwinRelationship {self.user_id} <-> {self.twin_user_id} ({self.similarity_score:.2f})>"
