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
                select(User).where(User.id == twin_user_id)
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

        # MINIMUM TWINS GUARANTEE: Ensure at least 5 twins if possible
        MIN_TWINS = 5
        if len(twins) < MIN_TWINS:
            # Get user's taste DNA to find similar users
            user_dna_result = await db.execute(
                select(TasteDNA).where(TasteDNA.user_id == user_id)
            )
            user_dna = user_dna_result.scalar_one_or_none()

            if user_dna:
                # Get existing twin IDs
                existing_twin_ids = {t["twin_id"] for t in twins}

                # Find additional users who aren't already twins
                additional_users_result = await db.execute(
                    select(User)
                    .join(TasteDNA, TasteDNA.user_id == User.id)
                    .where(
                        User.id != user_id,
                        ~User.id.in_([UUID(tid) for tid in existing_twin_ids])
                    )
                    .limit(MIN_TWINS - len(twins))
                )
                additional_users = additional_users_result.scalars().all()

                # Add them as twins with a default similarity score
                for additional_user in additional_users:
                    additional_dna_result = await db.execute(
                        select(TasteDNA).where(TasteDNA.user_id == additional_user.id)
                    )
                    additional_dna = additional_dna_result.scalar_one_or_none()

                    # Calculate basic similarity based on shared preferences
                    shared_cuisines = []
                    if additional_dna and user_dna.preferred_cuisines and additional_dna.preferred_cuisines:
                        user_cuisines = set(user_dna.preferred_cuisines)
                        other_cuisines = set(additional_dna.preferred_cuisines)
                        shared_cuisines = list(user_cuisines & other_cuisines)

                    # Default similarity score (lower than matched twins)
                    default_score = 0.5

                    twins.append({
                        "twin_id": str(additional_user.id),
                        "name": additional_user.name,
                        "email": additional_user.email,
                        "avatar_url": additional_user.avatar_url,
                        "similarity_score": default_score,
                        "shared_cuisines": shared_cuisines,
                        "adventure_score": additional_dna.adventure_score if additional_dna else 0.0,
                        "spice_tolerance": additional_dna.spice_tolerance if additional_dna else 0.0,
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
