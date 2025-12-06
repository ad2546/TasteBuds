"""Discovery and recommendation service."""

from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.taste_dna import TasteDNA
from app.models.interaction_log import InteractionLog
from app.services.yelp_service import yelp_service
from app.services.twin_matching_service import twin_matching_service
from app.db.redis_client import redis_client


class DiscoveryService:
    """Service for restaurant discovery and recommendations."""

    async def get_feeling_lucky(
        self,
        db: AsyncSession,
        user_id: UUID,
        location: str,
    ) -> Dict:
        """Get a single highly-matched restaurant recommendation."""
        # Get user's TasteDNA
        result = await db.execute(
            select(TasteDNA).where(TasteDNA.user_id == user_id)
        )
        taste_dna = result.scalar_one_or_none()

        if not taste_dna:
            raise ValueError("TasteDNA not found. Complete the quiz first.")

        # Get user's twins
        twins = await twin_matching_service.get_user_twins(db, user_id)

        # Search for restaurants based on taste profile
        dna_dict = taste_dna.to_dict()
        restaurants = await yelp_service.search_restaurants_for_taste(
            location=location,
            taste_dna=dna_dict,
            limit=10,
        )

        if not restaurants:
            # Fallback to general search
            search_result = await yelp_service.search_businesses(
                term="restaurants",
                location=location,
                sort_by="rating",
                limit=10,
            )
            restaurants = search_result.get("businesses", [])

        if not restaurants:
            return None

        # Score and select best restaurant
        best_restaurant = self._score_and_select(restaurants, taste_dna, twins)

        # Generate explanation
        explanation = self._generate_explanation(best_restaurant, taste_dna, twins)

        return {
            "restaurant": best_restaurant,
            "explanation": explanation,
            "match_score": best_restaurant.get("_match_score", 0.85),
            "twin_count": len([t for t in twins if t["similarity_score"] > 0.7]),
        }

    async def get_compare_options(
        self,
        db: AsyncSession,
        user_id: UUID,
        location: str,
    ) -> List[Dict]:
        """Get 3 restaurant options for comparison."""
        result = await db.execute(
            select(TasteDNA).where(TasteDNA.user_id == user_id)
        )
        taste_dna = result.scalar_one_or_none()

        if not taste_dna:
            raise ValueError("TasteDNA not found")

        dna_dict = taste_dna.to_dict()
        restaurants = await yelp_service.search_restaurants_for_taste(
            location=location,
            taste_dna=dna_dict,
            limit=20,
        )

        # Select diverse options
        options = self._select_diverse_options(restaurants, taste_dna, count=3)

        result_options = []
        for restaurant in options:
            pros, cons = self._analyze_pros_cons(restaurant, taste_dna)
            result_options.append({
                "restaurant": restaurant,
                "pros": pros,
                "cons": cons,
                "explanation": self._generate_explanation(restaurant, taste_dna, []),
            })

        return result_options

    async def get_trending_among_twins(
        self,
        db: AsyncSession,
        user_id: UUID,
        location: str,
        limit: int = 10,
    ) -> List[Dict]:
        """Get restaurants trending among user's Taste Twins."""
        # Get twins
        twins = await twin_matching_service.get_user_twins(db, user_id)
        twin_ids = [UUID(t["user_id"]) for t in twins]

        if not twin_ids:
            return []

        # Get twin interactions
        result = await db.execute(
            select(InteractionLog)
            .where(InteractionLog.user_id.in_(twin_ids))
            .where(InteractionLog.action_type.in_(["save", "book", "like"]))
            .order_by(InteractionLog.created_at.desc())
            .limit(100)
        )
        interactions = result.scalars().all()

        # Count restaurant popularity among twins
        restaurant_counts = {}
        for interaction in interactions:
            rid = interaction.restaurant_id
            if rid not in restaurant_counts:
                restaurant_counts[rid] = 0
            restaurant_counts[rid] += 1

        # Get top restaurants
        sorted_restaurants = sorted(
            restaurant_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        # Fetch restaurant details
        trending = []
        for restaurant_id, count in sorted_restaurants:
            try:
                restaurant = await yelp_service.get_business(restaurant_id)
                trending.append({
                    "restaurant": restaurant,
                    "twin_visits": count,
                    "trend_score": min(1.0, count / 10),
                })
            except Exception:
                continue

        return trending

    def _score_and_select(
        self,
        restaurants: List[Dict],
        taste_dna: TasteDNA,
        twins: List[Dict],
    ) -> Dict:
        """Score restaurants and select the best match."""
        scored = []

        for restaurant in restaurants:
            score = self._calculate_match_score(restaurant, taste_dna)
            restaurant["_match_score"] = score
            scored.append((score, restaurant))

        # Sort by score and return top
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else restaurants[0]

    def _calculate_match_score(
        self,
        restaurant: Dict,
        taste_dna: TasteDNA,
    ) -> float:
        """Calculate how well a restaurant matches TasteDNA."""
        score = 0.5  # Base score

        # Price match
        price = restaurant.get("price", "$$")
        price_level = len(price) / 4  # 0.25 to 1.0
        price_diff = abs(taste_dna.price_sensitivity - (1 - price_level))
        score += (1 - price_diff) * 0.2

        # Rating bonus
        rating = restaurant.get("rating", 3.5)
        score += (rating / 5) * 0.2

        # Category match
        categories = [c.get("alias", "") for c in restaurant.get("categories", [])]
        preferred = [c.lower() for c in (taste_dna.preferred_cuisines or [])]
        matching_categories = len(set(categories) & set(preferred))
        score += min(0.3, matching_categories * 0.1)

        return min(1.0, score)

    def _select_diverse_options(
        self,
        restaurants: List[Dict],
        taste_dna: TasteDNA,
        count: int = 3,
    ) -> List[Dict]:
        """Select diverse restaurant options."""
        if len(restaurants) <= count:
            return restaurants

        # Score all restaurants
        for r in restaurants:
            r["_match_score"] = self._calculate_match_score(r, taste_dna)

        # Sort by score
        restaurants.sort(key=lambda x: x.get("_match_score", 0), reverse=True)

        # Select diverse options (top match, mid-range, adventurous)
        options = [restaurants[0]]  # Best match

        # Find different price point
        for r in restaurants[1:10]:
            if r.get("price") != restaurants[0].get("price"):
                options.append(r)
                break

        # Find different cuisine
        first_categories = set(c["alias"] for c in restaurants[0].get("categories", []))
        for r in restaurants[1:10]:
            r_categories = set(c["alias"] for c in r.get("categories", []))
            if not (first_categories & r_categories) and r not in options:
                options.append(r)
                break

        # Fill remaining slots
        while len(options) < count and len(restaurants) > len(options):
            for r in restaurants:
                if r not in options:
                    options.append(r)
                    break

        return options[:count]

    def _analyze_pros_cons(
        self,
        restaurant: Dict,
        taste_dna: TasteDNA,
    ) -> tuple:
        """Analyze pros and cons of a restaurant for the user."""
        pros = []
        cons = []

        # Rating
        rating = restaurant.get("rating", 0)
        if rating >= 4.5:
            pros.append(f"Excellent rating: {rating}★")
        elif rating < 3.5:
            cons.append(f"Lower rating: {rating}★")

        # Review count
        reviews = restaurant.get("review_count", 0)
        if reviews > 500:
            pros.append("Very popular with many reviews")
        elif reviews < 50:
            cons.append("Newer/less reviewed spot")

        # Price match
        price = restaurant.get("price", "$$")
        price_level = len(price) / 4
        if abs(taste_dna.price_sensitivity - (1 - price_level)) < 0.2:
            pros.append(f"Price ({price}) matches your preference")
        elif price_level > 0.7 and taste_dna.price_sensitivity > 0.6:
            cons.append("Might be pricier than preferred")

        # Categories
        categories = [c.get("title", "") for c in restaurant.get("categories", [])]
        preferred = taste_dna.preferred_cuisines or []
        for cat in categories:
            if any(p.lower() in cat.lower() for p in preferred):
                pros.append(f"Serves your favorite: {cat}")
                break

        return pros[:3], cons[:2]

    def _generate_explanation(
        self,
        restaurant: Dict,
        taste_dna: TasteDNA,
        twins: List[Dict],
    ) -> str:
        """Generate explanation for why this restaurant matches."""
        explanations = []

        # Match score
        score = restaurant.get("_match_score", 0.8)
        explanations.append(f"{int(score * 100)}% match with your TasteDNA")

        # Category match
        categories = [c.get("title", "") for c in restaurant.get("categories", [])]
        preferred = taste_dna.preferred_cuisines or []
        for cat in categories:
            if any(p.lower() in cat.lower() for p in preferred):
                explanations.append(f"Features your favorite cuisine: {cat}")
                break

        # Price alignment
        price = restaurant.get("price", "$$")
        explanations.append(f"Price point ({price}) aligns with your preferences")

        # Twin endorsements
        if twins:
            high_similarity_twins = len([t for t in twins if t["similarity_score"] > 0.7])
            if high_similarity_twins > 0:
                explanations.append(
                    f"{high_similarity_twins} Taste Twins love similar restaurants"
                )

        return " • ".join(explanations)


# Global service instance
discovery_service = DiscoveryService()


def get_discovery_service() -> DiscoveryService:
    """Dependency to get discovery service."""
    return discovery_service
