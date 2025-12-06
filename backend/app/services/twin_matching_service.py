"""Taste Twin matching service."""

from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.models.twin_relationship import TwinRelationship
from app.db.pinecone_client import pinecone_client
from app.db.redis_client import redis_client
from app.ai.embeddings.taste_encoder import taste_embedding_service


class TwinMatchingService:
    """Service for finding and managing Taste Twins."""

    def __init__(self):
        self.embedding_service = taste_embedding_service
        self.pinecone = pinecone_client

    async def store_user_embedding(
        self,
        user_id: UUID,
        taste_dna: TasteDNA,
        city: Optional[str] = None,
    ) -> List[float]:
        """Generate and store user's taste embedding in Pinecone."""
        # Convert TasteDNA to dict
        dna_dict = taste_dna.to_dict()

        # Generate embedding
        embedding = self.embedding_service.generate_embedding(dna_dict)

        # Prepare metadata for Pinecone
        metadata = {
            "user_id": str(user_id),
            "adventure_score": taste_dna.adventure_score,
            "spice_tolerance": taste_dna.spice_tolerance,
            "price_sensitivity": taste_dna.price_sensitivity,
            "cuisine_diversity": taste_dna.cuisine_diversity,
            "ambiance_preference": taste_dna.ambiance_preference or "casual",
            "preferred_cuisines": taste_dna.preferred_cuisines or [],
        }
        if city:
            metadata["city"] = city

        # Store in Pinecone
        await self.pinecone.upsert_user_embedding(
            user_id=str(user_id),
            embedding=embedding,
            metadata=metadata,
        )

        return embedding

    async def find_twins(
        self,
        db: AsyncSession,
        user_id: UUID,
        taste_dna: TasteDNA,
        top_k: int = None,
        city_filter: Optional[str] = None,
    ) -> List[Dict]:
        """Find Taste Twins for a user."""
        # Generate embedding for query
        dna_dict = taste_dna.to_dict()
        embedding = self.embedding_service.generate_embedding(dna_dict)

        # Build filter if city specified
        filter_dict = None
        if city_filter:
            filter_dict = {"city": {"$eq": city_filter}}

        # Get total user count if top_k not specified (to get all users)
        if top_k is None:
            total_users = self.pinecone.get_total_user_count()
            # Use total users count, capped at Pinecone's 10000 limit
            top_k = min(total_users if total_users > 0 else 10000, 10000)

        # Query Pinecone for similar users
        twins_data = await self.pinecone.find_taste_twins(
            user_id=str(user_id),
            embedding=embedding,
            top_k=top_k,
            filter_dict=filter_dict,
        )

        # Enrich with user data from database
        twins = []
        for twin_data in twins_data:
            twin_user_id = twin_data["user_id"]
            result = await db.execute(
                select(User).where(User.id == UUID(twin_user_id))
            )
            twin_user = result.scalar_one_or_none()

            if twin_user:
                # Find common cuisines
                twin_cuisines = set(twin_data["metadata"].get("preferred_cuisines", []))
                user_cuisines = set(taste_dna.preferred_cuisines or [])
                common = list(twin_cuisines & user_cuisines)

                twins.append({
                    "twin_id": twin_user_id,
                    "name": twin_user.name,
                    "email": twin_user.email,
                    "avatar_url": twin_user.avatar_url,
                    "similarity_score": twin_data["similarity_score"],
                    "shared_cuisines": common,
                    "adventure_score": twin_data["metadata"].get("adventure_score", 0.0),
                    "spice_tolerance": twin_data["metadata"].get("spice_tolerance", 0.0),
                })

        return twins

    async def update_twin_relationships(
        self,
        db: AsyncSession,
        user_id: UUID,
        twins: List[Dict],
    ):
        """Store or update twin relationships in database."""
        # Delete existing relationships for this user
        await db.execute(
            delete(TwinRelationship).where(TwinRelationship.user_id == user_id)
        )

        # Create new relationships
        for twin in twins:
            relationship = TwinRelationship(
                user_id=user_id,
                twin_user_id=UUID(twin["twin_id"]),
                similarity_score=twin["similarity_score"],
                common_cuisines=twin["shared_cuisines"],
            )
            db.add(relationship)

        await db.commit()

    async def get_user_twins(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> List[Dict]:
        """Get stored twin relationships for a user."""
        # Check cache first
        cache_key = f"twins:{user_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return cached

        # Query database
        result = await db.execute(
            select(TwinRelationship)
            .where(TwinRelationship.user_id == user_id)
            .order_by(TwinRelationship.similarity_score.desc())
        )
        relationships = result.scalars().all()

        twins = []
        for rel in relationships:
            # Get twin user data
            user_result = await db.execute(
                select(User).where(User.id == rel.twin_user_id)
            )
            twin_user = user_result.scalar_one_or_none()

            if twin_user:
                # Get twin's TasteDNA for adventure_score and spice_tolerance
                dna_result = await db.execute(
                    select(TasteDNA).where(TasteDNA.user_id == rel.twin_user_id)
                )
                twin_dna = dna_result.scalar_one_or_none()

                twins.append({
                    "twin_id": str(rel.twin_user_id),
                    "name": twin_user.name,
                    "email": twin_user.email,
                    "avatar_url": twin_user.avatar_url,
                    "similarity_score": rel.similarity_score,
                    "shared_cuisines": rel.common_cuisines or [],
                    "adventure_score": twin_dna.adventure_score if twin_dna else 0.0,
                    "spice_tolerance": twin_dna.spice_tolerance if twin_dna else 0.0,
                })

        # Cache results
        if twins:
            await redis_client.set(cache_key, twins, ttl=900)  # 15 minutes

        return twins

    async def get_twin_count(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> int:
        """Get count of user's Taste Twins."""
        result = await db.execute(
            select(TwinRelationship)
            .where(TwinRelationship.user_id == user_id)
        )
        return len(result.scalars().all())

    async def refresh_twins(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> List[Dict]:
        """Refresh twin matching for a user."""
        # Get user's TasteDNA
        result = await db.execute(
            select(TasteDNA).where(TasteDNA.user_id == user_id)
        )
        taste_dna = result.scalar_one_or_none()

        if not taste_dna:
            return []

        # Find new twins
        twins = await self.find_twins(db, user_id, taste_dna)

        # Update relationships
        await self.update_twin_relationships(db, user_id, twins)

        # Invalidate cache
        cache_key = f"twins:{user_id}"
        await redis_client.delete(cache_key)

        return twins


# Global service instance
twin_matching_service = TwinMatchingService()


def get_twin_matching_service() -> TwinMatchingService:
    """Dependency to get twin matching service."""
    return twin_matching_service
