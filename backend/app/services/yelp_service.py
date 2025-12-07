"""Yelp Fusion API service wrapper."""

from typing import Optional, List, Dict, Any
import httpx

from app.config import get_settings
from app.core.exceptions import YelpAPIException
from app.db.redis_client import redis_client


class YelpService:
    """Service for interacting with Yelp Fusion API."""

    BASE_URL = "https://api.yelp.com/v3"

    def __init__(self):
        settings = get_settings()  # Get settings fresh each time
        self.api_key = settings.yelp_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        cache_key: Optional[str] = None,
        cache_ttl: int = 3600,
    ) -> Dict:
        """Make HTTP request to Yelp API - always fetch fresh data, no caching."""
        # DISABLED CACHING: Always fetch fresh data from Yelp API
        # This ensures all restaurant data is real-time and up-to-date

        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # No caching - always return fresh data from Yelp
                return data
            except httpx.HTTPStatusError as e:
                raise YelpAPIException(f"Yelp API error: {e.response.status_code}")
            except httpx.RequestError as e:
                raise YelpAPIException(f"Yelp API request failed: {str(e)}")

    async def search_businesses(
        self,
        term: Optional[str] = None,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None,
        categories: Optional[str] = None,
        price: Optional[str] = None,
        open_now: bool = False,
        sort_by: str = "best_match",
        limit: int = 20,
        offset: int = 0,
    ) -> Dict:
        """Search for businesses on Yelp."""
        params = {
            "term": term or "restaurants",
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset,
        }

        if location:
            params["location"] = location
        elif latitude and longitude:
            params["latitude"] = latitude
            params["longitude"] = longitude
        else:
            raise YelpAPIException("Either location or coordinates required")

        if radius:
            params["radius"] = min(radius, 40000)  # Max 40km
        if categories:
            params["categories"] = categories
        if price:
            params["price"] = price
        if open_now:
            params["open_now"] = True

        return await self._make_request("GET", "/businesses/search", params=params)

    async def get_business(self, business_id: str) -> Dict:
        """Get detailed business information."""
        cache_key = f"yelp:business:{business_id}"
        return await self._make_request(
            "GET",
            f"/businesses/{business_id}",
            cache_key=cache_key,
            cache_ttl=3600,
        )

    async def get_business_reviews(
        self,
        business_id: str,
        locale: str = "en_US",
        limit: int = 3,
        sort_by: str = "yelp_sort",
    ) -> Dict:
        """Get reviews for a business."""
        params = {
            "locale": locale,
            "limit": limit,
            "sort_by": sort_by,
        }
        cache_key = f"yelp:reviews:{business_id}"
        return await self._make_request(
            "GET",
            f"/businesses/{business_id}/reviews",
            params=params,
            cache_key=cache_key,
            cache_ttl=1800,  # 30 minutes
        )

    async def search_by_phone(self, phone: str) -> Dict:
        """Search for business by phone number."""
        params = {"phone": phone}
        return await self._make_request("GET", "/businesses/search/phone", params=params)

    async def get_autocomplete(
        self,
        text: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        locale: str = "en_US",
    ) -> Dict:
        """Get autocomplete suggestions."""
        params = {"text": text, "locale": locale}
        if latitude and longitude:
            params["latitude"] = latitude
            params["longitude"] = longitude
        return await self._make_request("GET", "/autocomplete", params=params)

    async def search_restaurants_for_taste(
        self,
        location: str,
        taste_dna: Dict,
        limit: int = 20,
    ) -> List[Dict]:
        """Search restaurants based on TasteDNA profile."""
        # Build search parameters based on TasteDNA
        categories = []
        price_range = []

        # Map price sensitivity to price range
        price_sensitivity = taste_dna.get("price_sensitivity", 0.5)
        if price_sensitivity > 0.7:
            price_range = ["1", "2"]  # Budget-friendly
        elif price_sensitivity > 0.4:
            price_range = ["2", "3"]  # Mid-range
        else:
            price_range = ["3", "4"]  # Upscale

        # Add preferred cuisines to categories
        preferred_cuisines = taste_dna.get("preferred_cuisines", [])
        for cuisine in preferred_cuisines[:3]:  # Limit to top 3
            categories.append(cuisine.lower().replace(" ", ""))

        # Build search params
        results = await self.search_businesses(
            term="restaurants",
            location=location,
            price=",".join(price_range) if price_range else None,
            categories=",".join(categories) if categories else None,
            sort_by="rating",
            limit=limit,
        )

        return results.get("businesses", [])

    async def get_restaurants_by_ids(self, business_ids: List[str]) -> List[Dict]:
        """Get multiple restaurants by their IDs."""
        restaurants = []
        for business_id in business_ids:
            try:
                restaurant = await self.get_business(business_id)
                restaurants.append(restaurant)
            except YelpAPIException:
                continue  # Skip failed requests
        return restaurants


# Global service instance
yelp_service = YelpService()


def get_yelp_service() -> YelpService:
    """Dependency to get Yelp service."""
    return yelp_service
