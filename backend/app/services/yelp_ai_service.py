"""Yelp AI API service for conversational search and discovery."""

from typing import Optional, Dict, Any, List
import httpx
from uuid import uuid4

from app.config import get_settings
from app.core.exceptions import YelpAPIException
from app.db.redis_client import redis_client


class YelpAIService:
    """Service for interacting with Yelp AI Chat API."""

    AI_API_URL = "https://api.yelp.com/ai/chat/v2"

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.yelp_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _transform_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Yelp AI API response to expected format.

        Yelp AI returns:
        {
          "chat_id": "...",
          "response": {"text": "...", "tags": []},
          "entities": [{"businesses": [...]}],
          "types": [...]
        }

        We transform to:
        {
          "chat_id": "...",
          "text": "...",
          "businesses": [...],
          "entities": [...],
          "types": [...],
          "tags": [...]
        }
        """
        transformed = {
            "chat_id": raw_data.get("chat_id"),
            "text": raw_data.get("response", {}).get("text", ""),
            "tags": raw_data.get("response", {}).get("tags", []),
            "types": raw_data.get("types", []),
            "entities": raw_data.get("entities", []),
        }

        # Extract businesses from entities array
        businesses = []
        if raw_data.get("entities") and len(raw_data["entities"]) > 0:
            businesses = raw_data["entities"][0].get("businesses", [])

        transformed["businesses"] = businesses

        return transformed

    async def chat(
        self,
        query: str,
        chat_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        skip_text_generation: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a natural language query to Yelp AI API.

        Args:
            query: Natural language query (e.g., "Find me a Thai restaurant near me")
            chat_id: Optional conversation ID to continue a multi-turn conversation
            latitude: User's latitude for location-based results
            longitude: User's longitude for location-based results
            skip_text_generation: If True, returns only structured data without AI text

        Returns:
            Dict containing AI response with businesses, text, and conversation metadata
        """
        payload: Dict[str, Any] = {
            "query": query[:1000],  # Max 1000 characters
        }

        # Add chat_id for continuing conversations
        if chat_id:
            payload["chat_id"] = chat_id

        # Add user location context if provided
        if latitude is not None and longitude is not None:
            payload["user_context"] = {
                "latitude": latitude,
                "longitude": longitude,
            }

        # Add request context settings
        if skip_text_generation:
            payload["request_context"] = {
                "skip_text_generation": True,
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.AI_API_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                raw_data = response.json()

                # Transform Yelp AI response to expected format
                return self._transform_response(raw_data)
        except httpx.HTTPStatusError as e:
            error_detail = f"Yelp AI API error: {e.response.status_code}"
            try:
                error_body = e.response.json()
                error_detail += f" - {error_body}"
            except Exception:
                pass
            raise YelpAPIException(error_detail)
        except httpx.RequestError as e:
            raise YelpAPIException(f"Yelp AI API request failed: {str(e)}")

    async def search_with_context(
        self,
        query: str,
        taste_dna: Optional[Dict] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Enhanced search that incorporates user's TasteDNA into the query.

        Args:
            query: User's natural language query
            taste_dna: User's taste DNA profile to enhance the query
            latitude: User's location
            longitude: User's location

        Returns:
            AI response with personalized results
        """
        # Enhance query with taste preferences
        enhanced_query = query

        if taste_dna:
            preferences = []

            # Add cuisine preferences
            if taste_dna.get("preferred_cuisines"):
                cuisines = ", ".join(taste_dna["preferred_cuisines"][:3])
                preferences.append(f"I prefer {cuisines} cuisine")

            # Add price preference
            price_sensitivity = taste_dna.get("price_sensitivity", 0.5)
            if price_sensitivity > 0.7:
                preferences.append("budget-friendly options")
            elif price_sensitivity < 0.3:
                preferences.append("upscale dining")

            # Add ambiance preference
            if taste_dna.get("ambiance_preference"):
                preferences.append(f"{taste_dna['ambiance_preference']} atmosphere")

            # Add adventure level
            adventure = taste_dna.get("adventure_score", 0.5)
            if adventure > 0.7:
                preferences.append("unique and adventurous places")
            elif adventure < 0.3:
                preferences.append("classic and reliable spots")

            if preferences:
                enhanced_query = f"{query}. My preferences: {', '.join(preferences)}."

        return await self.chat(
            query=enhanced_query,
            latitude=latitude,
            longitude=longitude,
        )

    async def compare_restaurants(
        self,
        restaurant_ids: List[str],
        comparison_criteria: str = "overall experience",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Use AI to compare multiple restaurants.

        Args:
            restaurant_ids: List of Yelp business IDs to compare
            comparison_criteria: What to compare (e.g., "price and atmosphere")
            latitude: User location
            longitude: User location

        Returns:
            AI comparison analysis
        """
        # Build business names/IDs into query
        businesses_str = " and ".join(restaurant_ids[:3])  # Limit to 3 for clarity
        query = f"Compare these restaurants for {comparison_criteria}: {businesses_str}. Give me pros and cons for each."

        return await self.chat(
            query=query,
            latitude=latitude,
            longitude=longitude,
        )

    async def get_restaurant_recommendations(
        self,
        occasion: str,
        party_size: Optional[int] = None,
        date_time: Optional[str] = None,
        taste_dna: Optional[Dict] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get AI recommendations for specific occasions.

        Args:
            occasion: Type of occasion (date night, birthday, business meeting, etc.)
            party_size: Number of people
            date_time: When they want to go
            taste_dna: User preferences
            latitude: Location
            longitude: Location

        Returns:
            AI recommendations
        """
        query_parts = [f"Recommend restaurants for a {occasion}"]

        if party_size:
            query_parts.append(f"for {party_size} people")

        if date_time:
            query_parts.append(f"on {date_time}")

        query = " ".join(query_parts)

        return await self.search_with_context(
            query=query,
            taste_dna=taste_dna,
            latitude=latitude,
            longitude=longitude,
        )

    async def ask_about_restaurant(
        self,
        restaurant_id: str,
        question: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Ask specific questions about a restaurant.

        Args:
            restaurant_id: Yelp business ID
            question: Question about the restaurant
            latitude: User location
            longitude: User location

        Returns:
            AI answer about the restaurant
        """
        query = f"Tell me about the restaurant with ID {restaurant_id}: {question}"

        return await self.chat(
            query=query,
            latitude=latitude,
            longitude=longitude,
        )

    async def continue_conversation(
        self,
        chat_id: str,
        message: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Continue a multi-turn conversation.

        Args:
            chat_id: Existing conversation ID
            message: Follow-up message
            latitude: User location
            longitude: User location

        Returns:
            AI response continuing the conversation
        """
        return await self.chat(
            query=message,
            chat_id=chat_id,
            latitude=latitude,
            longitude=longitude,
        )

    async def get_date_night_recommendations(
        self,
        user1_taste_dna: Dict,
        user2_taste_dna: Dict,
        location: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get AI-powered restaurant recommendations for a date night based on two users' preferences.

        Args:
            user1_taste_dna: First user's TasteDNA profile
            user2_taste_dna: Second user's TasteDNA profile
            location: Location string (e.g., "San Francisco, CA")
            latitude: Optional latitude
            longitude: Optional longitude

        Returns:
            AI recommendations optimized for both users
        """
        # Build a query that incorporates both users' preferences
        query_parts = [f"Recommend restaurants in {location} for a romantic date night"]

        # Combine cuisine preferences
        cuisines1 = set(user1_taste_dna.get("preferred_cuisines", []))
        cuisines2 = set(user2_taste_dna.get("preferred_cuisines", []))
        common_cuisines = list(cuisines1 & cuisines2)
        all_cuisines = list(cuisines1 | cuisines2)

        if common_cuisines:
            query_parts.append(f"We both love {', '.join(common_cuisines[:3])} food")
        elif all_cuisines:
            query_parts.append(f"We enjoy {', '.join(all_cuisines[:4])} cuisine")

        # Handle price preferences (use lower to accommodate both)
        avg_price_sensitivity = (
            user1_taste_dna.get("price_sensitivity", 0.5) +
            user2_taste_dna.get("price_sensitivity", 0.5)
        ) / 2

        if avg_price_sensitivity > 0.7:
            query_parts.append("with reasonable prices")
        elif avg_price_sensitivity < 0.3:
            query_parts.append("upscale and special occasion worthy")

        # Handle ambiance (prioritize romantic)
        ambiance1 = user1_taste_dna.get("ambiance_preference", "").lower()
        ambiance2 = user2_taste_dna.get("ambiance_preference", "").lower()

        if ambiance1 == ambiance2:
            query_parts.append(f"with a {ambiance1} atmosphere")
        else:
            query_parts.append("with a romantic and intimate atmosphere")

        # Handle adventure level
        avg_adventure = (
            user1_taste_dna.get("adventure_score", 0.5) +
            user2_taste_dna.get("adventure_score", 0.5)
        ) / 2

        if avg_adventure > 0.7:
            query_parts.append("unique and adventurous spots preferred")
        elif avg_adventure < 0.3:
            query_parts.append("classic and well-established restaurants")

        query_parts.append("Please suggest places that would work well for both of us")

        query = ". ".join(query_parts) + "."

        return await self.chat(
            query=query,
            latitude=latitude,
            longitude=longitude,
        )


# Global service instance
yelp_ai_service = YelpAIService()


def get_yelp_ai_service() -> YelpAIService:
    """Dependency to get Yelp AI service."""
    return yelp_ai_service
