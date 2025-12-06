"""Redis client for caching and real-time features."""

import json
from typing import Optional, Any
import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self):
        self._client: Optional[redis.Redis] = None

    async def connect(self):
        """Initialize Redis connection."""
        self._client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()

    @property
    def client(self) -> Optional[redis.Redis]:
        """Get Redis client instance."""
        return self._client

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._client is not None

    # User Session Cache
    async def cache_user_session(self, user_id: str, data: dict, ttl: int = 86400):
        """Cache user session data (24 hours default)."""
        key = f"user:session:{user_id}"
        await self.client.setex(key, ttl, json.dumps(data))

    async def get_user_session(self, user_id: str) -> Optional[dict]:
        """Get cached user session data."""
        key = f"user:session:{user_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def invalidate_user_session(self, user_id: str):
        """Invalidate user session cache."""
        key = f"user:session:{user_id}"
        await self.client.delete(key)

    # Restaurant Cache
    async def cache_restaurant(self, yelp_id: str, data: dict, ttl: int = 3600):
        """Cache restaurant data (1 hour default)."""
        key = f"restaurant:{yelp_id}"
        await self.client.setex(key, ttl, json.dumps(data))

    async def get_cached_restaurant(self, yelp_id: str) -> Optional[dict]:
        """Get cached restaurant data."""
        key = f"restaurant:{yelp_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None

    # Twin Recommendations Cache
    async def cache_twin_recommendations(self, user_id: str, data: list, ttl: int = 900):
        """Cache twin recommendations (15 minutes default)."""
        key = f"twins:recs:{user_id}"
        await self.client.setex(key, ttl, json.dumps(data))

    async def get_twin_recommendations(self, user_id: str) -> Optional[list]:
        """Get cached twin recommendations."""
        key = f"twins:recs:{user_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None

    # Leaderboard
    async def update_leaderboard(self, user_id: str, score: float, board: str = "adventure"):
        """Update user score on leaderboard."""
        key = f"leaderboard:{board}"
        await self.client.zadd(key, {user_id: score})

    async def get_leaderboard(self, board: str = "adventure", limit: int = 100) -> list:
        """Get top users from leaderboard."""
        key = f"leaderboard:{board}"
        results = await self.client.zrevrange(key, 0, limit - 1, withscores=True)
        return [{"user_id": user_id, "score": score} for user_id, score in results]

    async def get_user_rank(self, user_id: str, board: str = "adventure") -> Optional[int]:
        """Get user's rank on leaderboard."""
        key = f"leaderboard:{board}"
        rank = await self.client.zrevrank(key, user_id)
        return rank + 1 if rank is not None else None

    # Rate Limiting
    async def check_rate_limit(self, user_id: str, endpoint: str, max_requests: int = 60, window: int = 60) -> bool:
        """Check if user is within rate limit."""
        key = f"ratelimit:{user_id}:{endpoint}"
        current = await self.client.get(key)
        if current is None:
            await self.client.setex(key, window, 1)
            return True
        if int(current) >= max_requests:
            return False
        await self.client.incr(key)
        return True

    # Generic operations
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a key-value pair."""
        if not self.is_connected:
            return  # Silently skip if Redis not connected
        if ttl:
            await self.client.setex(key, ttl, json.dumps(value))
        else:
            await self.client.set(key, json.dumps(value))

    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        if not self.is_connected:
            return None  # Return None if Redis not connected
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def delete(self, key: str):
        """Delete a key."""
        if not self.is_connected:
            return  # Silently skip if Redis not connected
        await self.client.delete(key)


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency to get Redis client."""
    return redis_client
