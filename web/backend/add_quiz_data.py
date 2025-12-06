"""
Add dummy quiz answers to all users and calculate twin relationships
"""

import asyncio
import random
from sqlalchemy import select
from app.db.session import init_db, get_db
from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.models.twin_relationship import TwinRelationship


async def generate_quiz_answers_for_users():
    """Generate realistic quiz answers for all users based on their TasteDNA"""
    print("🎯 Generating quiz answers for all users...")

    await init_db()

    async for db in get_db():
        try:
            # Get all users with their TasteDNA
            result = await db.execute(
                select(User, TasteDNA).join(TasteDNA, User.id == TasteDNA.user_id)
            )
            users_with_dna = result.all()

            print(f"Found {len(users_with_dna)} users with TasteDNA")

            updated = 0
            for user, taste_dna in users_with_dna:
                # Generate quiz answers based on their TasteDNA profile
                quiz_answers = []

                # Swipe questions (5 questions)
                swipe_questions = [
                    {"id": "swipe_1", "adventure_threshold": 0.7},  # trendy urban
                    {"id": "swipe_2", "adventure_threshold": 0.8},  # exotic cuisine
                    {"id": "swipe_3", "price_threshold": 0.6},      # upscale fine dining
                    {"id": "swipe_4", "spice_threshold": 0.6},      # spicy Thai
                    {"id": "swipe_5", "adventure_threshold": 0.4},  # casual diner (inverse)
                ]

                for swipe in swipe_questions:
                    # Determine swipe direction based on user's profile
                    if "adventure_threshold" in swipe:
                        threshold = swipe["adventure_threshold"]
                        # For casual diner (swipe_5), invert the logic
                        if swipe["id"] == "swipe_5":
                            choice = "right" if taste_dna.adventure_score < threshold else "left"
                        else:
                            choice = "right" if taste_dna.adventure_score >= threshold else "left"
                    elif "price_threshold" in swipe:
                        # Lower price_sensitivity = willing to spend more
                        choice = "right" if taste_dna.price_sensitivity < swipe["price_threshold"] else "left"
                    elif "spice_threshold" in swipe:
                        choice = "right" if taste_dna.spice_tolerance >= swipe["spice_threshold"] else "left"
                    else:
                        choice = random.choice(["left", "right"])

                    # Add some randomness (10% chance to flip)
                    if random.random() < 0.1:
                        choice = "left" if choice == "right" else "right"

                    quiz_answers.append({
                        "question_id": swipe["id"],
                        "answer_type": f"swipe_{choice}",
                        "choice": choice
                    })

                # Slider questions
                quiz_answers.extend([
                    {
                        "question_id": "spice_tolerance",
                        "answer_type": "slider_value",
                        "value": taste_dna.spice_tolerance
                    },
                    {
                        "question_id": "adventure_level",
                        "answer_type": "slider_value",
                        "value": taste_dna.adventure_score
                    },
                    {
                        "question_id": "price_range",
                        "answer_type": "slider_value",
                        "value": taste_dna.price_sensitivity
                    },
                    {
                        "question_id": "cuisine_variety",
                        "answer_type": "slider_value",
                        "value": taste_dna.cuisine_diversity
                    }
                ])

                # Choice question - ambiance
                quiz_answers.append({
                    "question_id": "ambiance_pref",
                    "answer_type": "choice",
                    "choice": taste_dna.ambiance_preference.lower()
                })

                # Multiselect - preferred cuisines
                cuisines = taste_dna.preferred_cuisines or []
                quiz_answers.append({
                    "question_id": "preferred_cuisines",
                    "answer_type": "choice",
                    "choice": ",".join([c.lower().replace(" ", "_") for c in cuisines[:5]])
                })

                # Multiselect - dietary restrictions
                restrictions = taste_dna.dietary_restrictions or []
                if not restrictions:
                    restrictions = ["none"]
                quiz_answers.append({
                    "question_id": "dietary_restrictions",
                    "answer_type": "choice",
                    "choice": ",".join([r.lower().replace(" ", "_") for r in restrictions])
                })

                # Update TasteDNA with quiz answers
                taste_dna.quiz_answers = quiz_answers
                updated += 1

                if updated % 20 == 0:
                    await db.commit()
                    print(f"  ✓ Updated {updated} users...")

            await db.commit()
            print(f"✅ Generated quiz answers for {updated} users\n")

            return users_with_dna

        finally:
            break


async def calculate_twin_relationships(users_with_dna):
    """Calculate twin relationships based on TasteDNA similarity"""
    print("🤝 Calculating twin relationships...")

    async for db in get_db():
        try:
            # Clear existing twin relationships
            await db.execute(select(TwinRelationship))
            result = await db.execute(select(TwinRelationship))
            existing = result.scalars().all()
            for twin in existing:
                await db.delete(twin)
            await db.commit()

            print(f"Analyzing {len(users_with_dna)} users for twin matches...")

            relationships_created = 0

            for user, taste_dna in users_with_dna:
                similarities = []

                # Calculate similarity with all other users
                for other_user, other_taste_dna in users_with_dna:
                    if other_user.id == user.id:
                        continue

                    # Calculate similarity score
                    score = 1.0

                    # Adventure score similarity (30% weight)
                    score -= abs(taste_dna.adventure_score - other_taste_dna.adventure_score) * 0.3

                    # Spice tolerance similarity (20% weight)
                    score -= abs(taste_dna.spice_tolerance - other_taste_dna.spice_tolerance) * 0.2

                    # Price sensitivity similarity (15% weight)
                    score -= abs(taste_dna.price_sensitivity - other_taste_dna.price_sensitivity) * 0.15

                    # Cuisine diversity similarity (10% weight)
                    score -= abs(taste_dna.cuisine_diversity - other_taste_dna.cuisine_diversity) * 0.1

                    # Common cuisines (25% weight - 5% per common cuisine, max 5)
                    user_cuisines = set(taste_dna.preferred_cuisines or [])
                    other_cuisines = set(other_taste_dna.preferred_cuisines or [])
                    common_cuisines = user_cuisines & other_cuisines
                    score += min(len(common_cuisines) * 0.05, 0.25)

                    # Ambiance match bonus (5% weight)
                    if taste_dna.ambiance_preference == other_taste_dna.ambiance_preference:
                        score += 0.05

                    # Normalize score to 0-1 range
                    score = max(0, min(1, score))

                    similarities.append((other_user.id, score, list(common_cuisines)))

                # Sort by similarity score (highest first)
                similarities.sort(key=lambda x: x[1], reverse=True)

                # Create twin relationships for top matches (score > 0.5)
                for twin_id, similarity, common_cuisines in similarities[:15]:
                    if similarity > 0.5:
                        relationship = TwinRelationship(
                            user_id=user.id,
                            twin_user_id=twin_id,
                            similarity_score=round(similarity, 3),
                            common_cuisines=common_cuisines[:5]  # Top 5 common cuisines
                        )
                        db.add(relationship)
                        relationships_created += 1

                if relationships_created % 100 == 0 and relationships_created > 0:
                    await db.commit()
                    print(f"  ✓ Created {relationships_created} twin relationships...")

            await db.commit()
            print(f"✅ Created {relationships_created} twin relationships\n")

        finally:
            break


async def main():
    """Main execution flow"""
    print("=" * 60)
    print("TasteSync Quiz Data Generator")
    print("=" * 60)
    print()

    # Generate quiz answers for all users
    users_with_dna = await generate_quiz_answers_for_users()

    # Calculate twin relationships
    await calculate_twin_relationships(users_with_dna)

    print("=" * 60)
    print("✨ Quiz data generation complete!")
    print("=" * 60)
    print("All users now have:")
    print("  - Complete quiz answers")
    print("  - Twin relationships calculated")
    print("  - Ready for matching and recommendations")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
