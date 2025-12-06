"""TasteDNA Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class TasteDNABase(BaseModel):
    """Base TasteDNA schema."""

    adventure_score: float = Field(..., ge=0.0, le=1.0, description="How adventurous with food (0-1)")
    spice_tolerance: float = Field(..., ge=0.0, le=1.0, description="Spice tolerance level (0-1)")
    price_sensitivity: float = Field(..., ge=0.0, le=1.0, description="Price sensitivity (0=luxury, 1=budget)")
    cuisine_diversity: float = Field(..., ge=0.0, le=1.0, description="Variety seeking score (0-1)")
    ambiance_preference: Optional[str] = Field(None, description="Preferred ambiance (Casual, Upscale, Cozy, Trendy)")
    preferred_cuisines: Optional[List[str]] = Field(default_factory=list)
    dietary_restrictions: Optional[List[str]] = Field(default_factory=list)


class TasteDNAResponse(TasteDNABase):
    """Schema for TasteDNA response."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TasteDNACard(BaseModel):
    """Schema for shareable TasteDNA card."""

    user_name: str
    adventure_score: float
    spice_tolerance: float
    price_sensitivity: float
    cuisine_diversity: float
    ambiance_preference: Optional[str]
    top_cuisines: List[str]
    twin_count: int = 0


# Quiz related schemas
class QuizQuestion(BaseModel):
    """Schema for a quiz question."""

    id: str
    type: str  # swipe, slider, choice
    question: str
    options: Optional[List[dict]] = None
    image_url: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class QuizAnswer(BaseModel):
    """Schema for a quiz answer."""

    question_id: str
    answer_type: str  # swipe_right, swipe_left, slider_value, choice
    value: Optional[float] = None
    choice: Optional[str] = None


class QuizSubmission(BaseModel):
    """Schema for quiz submission."""

    answers: List[QuizAnswer]


class QuizResponse(BaseModel):
    """Schema for quiz questions response."""

    total_questions: int
    questions: List[QuizQuestion]


class TasteDNACalculationResult(BaseModel):
    """Schema for TasteDNA calculation result."""

    taste_dna: TasteDNAResponse
    twin_count: int
    top_twin_similarity: Optional[float] = None
