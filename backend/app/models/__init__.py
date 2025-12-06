"""Database models."""

from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.models.twin_relationship import TwinRelationship
from app.models.interaction_log import InteractionLog
from app.models.challenge import Challenge, UserChallenge, UserAchievement
from app.models.saved_restaurant import SavedRestaurant
from app.models.date_night import DateNightPairing
from app.models.image_search import ImageSearch

__all__ = [
    "User",
    "TasteDNA",
    "TwinRelationship",
    "InteractionLog",
    "Challenge",
    "UserChallenge",
    "UserAchievement",
    "SavedRestaurant",
    "DateNightPairing",
    "ImageSearch",
]
