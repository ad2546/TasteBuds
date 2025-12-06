"""Restaurant Pydantic schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field


class RestaurantLocation(BaseModel):
    """Restaurant location schema."""

    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    display_address: List[str] = Field(default_factory=list)


class RestaurantCoordinates(BaseModel):
    """Restaurant coordinates schema."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RestaurantCategory(BaseModel):
    """Restaurant category schema."""

    alias: str
    title: str


class RestaurantBase(BaseModel):
    """Base restaurant schema (Yelp data)."""

    id: str
    name: str
    image_url: Optional[str] = None
    url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price: Optional[str] = None  # $, $$, $$$, $$$$
    phone: Optional[str] = None
    display_phone: Optional[str] = None
    distance: Optional[float] = None
    is_closed: bool = False
    categories: List[RestaurantCategory] = Field(default_factory=list)
    location: Optional[RestaurantLocation] = None
    coordinates: Optional[RestaurantCoordinates] = None


class RestaurantDetail(RestaurantBase):
    """Detailed restaurant schema with additional info."""

    photos: List[str] = Field(default_factory=list)
    hours: Optional[List[dict]] = None
    special_hours: Optional[List[dict]] = None
    transactions: List[str] = Field(default_factory=list)  # delivery, pickup, reservation


class RestaurantReview(BaseModel):
    """Restaurant review schema."""

    id: str
    text: str
    rating: int
    time_created: str
    user: dict


class RestaurantSearchParams(BaseModel):
    """Search parameters for restaurant search."""

    term: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[int] = Field(None, le=40000)  # Max 40km
    categories: Optional[str] = None
    price: Optional[str] = None  # 1,2,3,4
    open_now: bool = False
    sort_by: str = "best_match"  # best_match, rating, review_count, distance
    limit: int = Field(20, ge=1, le=50)
    offset: int = Field(0, ge=0)


class RestaurantSearchResponse(BaseModel):
    """Response for restaurant search."""

    total: int
    businesses: List[RestaurantBase]


class RestaurantWithExplanation(RestaurantBase):
    """Restaurant with TasteSync explanation."""

    explanation: str  # Why this matches your TasteDNA
    twin_endorsements: int = 0  # Number of Taste Twins who loved it
    match_score: float = Field(..., ge=0.0, le=1.0)  # How well it matches
    twin_reviews: Optional[List[str]] = None  # Highlighted twin reviews
