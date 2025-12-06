"""TasteDNA service for quiz and profile management."""

from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.schemas.taste_dna import QuizQuestion, QuizAnswer, QuizSubmission


class TasteDNAService:
    """Service for managing TasteDNA profiles and quiz."""

    # Quiz questions for Taste DNA generation
    QUIZ_QUESTIONS: List[Dict] = [
        # Swipe-based questions (restaurant photos) - Real Unsplash images
        {
            "id": "swipe_1",
            "type": "swipe",
            "question": "Would you try this trendy urban restaurant?",
            "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&h=600&fit=crop",
            "options": [
                {"value": "left", "label": "Pass"},
                {"value": "right", "label": "Yes!"},
            ],
            "traits": {"adventure": 0.7, "ambiance": "trendy"},
        },
        {
            "id": "swipe_2",
            "type": "swipe",
            "question": "Would you try this exotic cuisine spot?",
            "image_url": "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&h=600&fit=crop",
            "options": [
                {"value": "left", "label": "Pass"},
                {"value": "right", "label": "Yes!"},
            ],
            "traits": {"adventure": 0.9, "cuisine": "exotic"},
        },
        {
            "id": "swipe_3",
            "type": "swipe",
            "question": "Would you try this upscale fine dining venue?",
            "image_url": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800&h=600&fit=crop",
            "options": [
                {"value": "left", "label": "Pass"},
                {"value": "right", "label": "Yes!"},
            ],
            "traits": {"price": "upscale", "ambiance": "romantic"},
        },
        {
            "id": "swipe_4",
            "type": "swipe",
            "question": "Would you try this spicy Thai restaurant?",
            "image_url": "https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=800&h=600&fit=crop",
            "options": [
                {"value": "left", "label": "Pass"},
                {"value": "right", "label": "Yes!"},
            ],
            "traits": {"spice": 0.8, "cuisine": "thai"},
        },
        {
            "id": "swipe_5",
            "type": "swipe",
            "question": "Would you try this casual family diner?",
            "image_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=600&fit=crop",
            "options": [
                {"value": "left", "label": "Pass"},
                {"value": "right", "label": "Yes!"},
            ],
            "traits": {"adventure": 0.3, "ambiance": "casual"},
        },
        # Slider questions
        {
            "id": "spice_tolerance",
            "type": "slider",
            "question": "How spicy do you like your food?",
            "min_value": 0.0,
            "max_value": 1.0,
            "min_label": "Mild",
            "max_label": "Fire!",
        },
        {
            "id": "adventure_level",
            "type": "slider",
            "question": "How adventurous are you with trying new foods?",
            "min_value": 0.0,
            "max_value": 1.0,
            "min_label": "Stick to favorites",
            "max_label": "Always exploring",
        },
        {
            "id": "price_range",
            "type": "slider",
            "question": "What's your typical dining budget?",
            "min_value": 0.0,
            "max_value": 1.0,
            "min_label": "Fine dining",
            "max_label": "Budget-friendly",
        },
        # Choice questions
        {
            "id": "ambiance_pref",
            "type": "choice",
            "question": "What's your ideal restaurant vibe?",
            "options": [
                {"value": "casual", "label": "Casual & Relaxed"},
                {"value": "upscale", "label": "Upscale & Elegant"},
                {"value": "cozy", "label": "Cozy & Intimate"},
                {"value": "trendy", "label": "Trendy & Hip"},
                {"value": "lively", "label": "Lively & Social"},
            ],
        },
        {
            "id": "cuisine_variety",
            "type": "slider",
            "question": "Do you prefer variety or consistency?",
            "min_value": 0.0,
            "max_value": 1.0,
            "min_label": "Same favorites",
            "max_label": "Always different",
        },
        # Multi-select for cuisines
        {
            "id": "preferred_cuisines",
            "type": "multiselect",
            "question": "Select your favorite cuisines (pick 3-5)",
            "options": [
                {"value": "italian", "label": "Italian"},
                {"value": "japanese", "label": "Japanese"},
                {"value": "mexican", "label": "Mexican"},
                {"value": "chinese", "label": "Chinese"},
                {"value": "indian", "label": "Indian"},
                {"value": "thai", "label": "Thai"},
                {"value": "french", "label": "French"},
                {"value": "mediterranean", "label": "Mediterranean"},
                {"value": "korean", "label": "Korean"},
                {"value": "vietnamese", "label": "Vietnamese"},
                {"value": "american", "label": "American"},
                {"value": "middle_eastern", "label": "Middle Eastern"},
            ],
        },
        # Dietary restrictions
        {
            "id": "dietary_restrictions",
            "type": "multiselect",
            "question": "Any dietary restrictions?",
            "options": [
                {"value": "none", "label": "None"},
                {"value": "vegetarian", "label": "Vegetarian"},
                {"value": "vegan", "label": "Vegan"},
                {"value": "gluten_free", "label": "Gluten-Free"},
                {"value": "dairy_free", "label": "Dairy-Free"},
                {"value": "halal", "label": "Halal"},
                {"value": "kosher", "label": "Kosher"},
            ],
        },
    ]

    def get_quiz_questions(self) -> List[QuizQuestion]:
        """Get all quiz questions."""
        questions = []
        for q in self.QUIZ_QUESTIONS:
            questions.append(QuizQuestion(
                id=q["id"],
                type=q["type"],
                question=q["question"],
                options=q.get("options"),
                image_url=q.get("image_url"),
                min_value=q.get("min_value"),
                max_value=q.get("max_value"),
            ))
        return questions

    def calculate_taste_dna(self, answers: List[QuizAnswer]) -> Dict:
        """Calculate TasteDNA from quiz answers."""
        # Initialize scores
        adventure_scores = []
        spice_tolerance = 0.5
        price_sensitivity = 0.5
        cuisine_diversity = 0.5
        ambiance_preference = "casual"
        preferred_cuisines = []
        dietary_restrictions = []

        # Create answer lookup
        answer_map = {a.question_id: a for a in answers}

        # Process each answer
        for question in self.QUIZ_QUESTIONS:
            q_id = question["id"]
            answer = answer_map.get(q_id)
            if not answer:
                continue

            if question["type"] == "swipe":
                # Swipe right = interested, adds to adventure if exotic
                if answer.choice == "right":
                    traits = question.get("traits", {})
                    if "adventure" in traits:
                        adventure_scores.append(traits["adventure"])

            elif question["type"] == "slider":
                if q_id == "spice_tolerance":
                    spice_tolerance = answer.value or 0.5
                elif q_id == "adventure_level":
                    adventure_scores.append(answer.value or 0.5)
                elif q_id == "price_range":
                    price_sensitivity = answer.value or 0.5
                elif q_id == "cuisine_variety":
                    cuisine_diversity = answer.value or 0.5

            elif question["type"] == "choice":
                if q_id == "ambiance_pref":
                    ambiance_preference = answer.choice or "casual"

            elif question["type"] == "multiselect":
                if q_id == "preferred_cuisines" and answer.choice:
                    preferred_cuisines = answer.choice.split(",")
                elif q_id == "dietary_restrictions" and answer.choice:
                    restrictions = answer.choice.split(",")
                    dietary_restrictions = [r for r in restrictions if r != "none"]

        # Calculate final adventure score
        adventure_score = sum(adventure_scores) / len(adventure_scores) if adventure_scores else 0.5

        return {
            "adventure_score": round(adventure_score, 2),
            "spice_tolerance": round(spice_tolerance, 2),
            "price_sensitivity": round(price_sensitivity, 2),
            "cuisine_diversity": round(cuisine_diversity, 2),
            "ambiance_preference": ambiance_preference,
            "preferred_cuisines": preferred_cuisines,
            "dietary_restrictions": dietary_restrictions,
        }

    async def create_taste_dna(
        self,
        db: AsyncSession,
        user_id: UUID,
        submission: QuizSubmission,
    ) -> TasteDNA:
        """Create or update TasteDNA for a user."""
        # Calculate DNA from answers
        dna_data = self.calculate_taste_dna(submission.answers)

        # Check if user already has TasteDNA
        result = await db.execute(
            select(TasteDNA).where(TasteDNA.user_id == user_id)
        )
        existing_dna = result.scalar_one_or_none()

        if existing_dna:
            # Update existing
            for key, value in dna_data.items():
                setattr(existing_dna, key, value)
            existing_dna.quiz_answers = [a.model_dump() for a in submission.answers]
            await db.commit()
            await db.refresh(existing_dna)
            return existing_dna
        else:
            # Create new
            taste_dna = TasteDNA(
                user_id=user_id,
                adventure_score=dna_data["adventure_score"],
                spice_tolerance=dna_data["spice_tolerance"],
                price_sensitivity=dna_data["price_sensitivity"],
                cuisine_diversity=dna_data["cuisine_diversity"],
                ambiance_preference=dna_data["ambiance_preference"],
                preferred_cuisines=dna_data["preferred_cuisines"],
                dietary_restrictions=dna_data["dietary_restrictions"],
                quiz_answers=[a.model_dump() for a in submission.answers],
            )
            db.add(taste_dna)

            # Update user's quiz_completed flag
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user.quiz_completed = True

            await db.commit()
            await db.refresh(taste_dna)
            return taste_dna

    async def get_user_taste_dna(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> Optional[TasteDNA]:
        """Get user's TasteDNA profile."""
        result = await db.execute(
            select(TasteDNA).where(TasteDNA.user_id == str(user_id))
        )
        return result.scalar_one_or_none()

    async def update_taste_dna_from_interaction(
        self,
        db: AsyncSession,
        user_id: UUID,
        interaction_type: str,
        restaurant_data: Dict,
    ) -> Optional[TasteDNA]:
        """Update TasteDNA based on user interaction (real-time learning)."""
        taste_dna = await self.get_user_taste_dna(db, user_id)
        if not taste_dna:
            return None

        # Learning rate for incremental updates
        lr = 0.05

        # Extract restaurant features
        restaurant_price = restaurant_data.get("price", "$$")
        restaurant_categories = [c.get("alias", "") for c in restaurant_data.get("categories", [])]

        if interaction_type in ["save", "book", "like"]:
            # Positive interaction - nudge preferences toward restaurant
            price_value = len(restaurant_price) / 4  # $ = 0.25, $$$$ = 1.0
            taste_dna.price_sensitivity += lr * (1 - price_value - taste_dna.price_sensitivity)

            # Increase diversity if trying new cuisine
            current_cuisines = set(taste_dna.preferred_cuisines or [])
            new_cuisines = set(restaurant_categories) - current_cuisines
            if new_cuisines:
                taste_dna.cuisine_diversity = min(1.0, taste_dna.cuisine_diversity + lr)

        elif interaction_type == "dismiss":
            # Negative interaction - slight adjustment away
            pass  # Could implement negative learning

        await db.commit()
        await db.refresh(taste_dna)
        return taste_dna


# Global service instance
taste_dna_service = TasteDNAService()


def get_taste_dna_service() -> TasteDNAService:
    """Dependency to get TasteDNA service."""
    return taste_dna_service
