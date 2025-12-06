"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1 import auth, users, taste_dna, taste_twins, discovery, restaurants, image_search, date_night, gamification, ai_chat

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(taste_dna.router, prefix="/taste-dna", tags=["Taste DNA"])
api_router.include_router(taste_twins.router, prefix="/twins", tags=["Taste Twins"])
api_router.include_router(discovery.router, prefix="/discovery", tags=["Discovery"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
api_router.include_router(image_search.router, prefix="/image-search", tags=["Image Search"])
api_router.include_router(date_night.router, prefix="/date-night", tags=["Date Night"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["Gamification"])
api_router.include_router(ai_chat.router, prefix="/ai-chat", tags=["AI Chat"])
