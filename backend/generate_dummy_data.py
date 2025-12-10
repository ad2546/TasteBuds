"""
TasteSync Dummy Data Generator
Generates realistic test data for all backend services
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.session import async_sessionmaker, init_db
from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.models.twin_relationship import TwinRelationship
from app.models.interaction_log import InteractionLog
from app.models.saved_restaurant import SavedRestaurant
from app.models.image_search import ImageSearch
from app.models.challenge import Challenge, UserChallenge, UserAchievement
from app.models.date_night import DateNightPairing
from app.core.security import get_password_hash

# Dummy data configurations
DUMMY_USERS = [
    {
        "name": "Alex Chen",
        "email": "alex.chen@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": 0.85,
            "spice_tolerance": 0.70,
            "price_sensitivity": 0.30,
            "cuisine_diversity": 0.80,
            "ambiance_preference": "Trendy",
            "preferred_cuisines": ["Japanese", "Thai", "Mexican", "Korean"],
            "dietary_restrictions": ["pescatarian"]
        }
    },
    {
        "name": "Sarah Martinez",
        "email": "sarah.m@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": 0.45,
            "spice_tolerance": 0.30,
            "price_sensitivity": 0.60,
            "cuisine_diversity": 0.40,
            "ambiance_preference": "Casual",
            "preferred_cuisines": ["Italian", "American", "Mediterranean"],
            "dietary_restrictions": ["vegetarian"]
        }
    },
    {
        "name": "James Wilson",
        "email": "james.w@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": 0.90,
            "spice_tolerance": 0.85,
            "price_sensitivity": 0.20,
            "cuisine_diversity": 0.90,
            "ambiance_preference": "Fine Dining",
            "preferred_cuisines": ["Indian", "Thai", "Ethiopian", "Vietnamese", "Sichuan"],
            "dietary_restrictions": []
        }
    },
    {
        "name": "Emily Parker",
        "email": "emily.p@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": 0.60,
            "spice_tolerance": 0.50,
            "price_sensitivity": 0.50,
            "cuisine_diversity": 0.65,
            "ambiance_preference": "Romantic",
            "preferred_cuisines": ["French", "Italian", "Spanish", "Japanese"],
            "dietary_restrictions": ["gluten-free"]
        }
    },
    {
        "name": "Michael Brown",
        "email": "michael.b@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": 0.25,
            "spice_tolerance": 0.20,
            "price_sensitivity": 0.70,
            "cuisine_diversity": 0.30,
            "ambiance_preference": "Casual",
            "preferred_cuisines": ["American", "Italian", "Burgers"],
            "dietary_restrictions": []
        }
    },
    {
        "name": "Priya Patel",
        "email": "priya.p@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": 0.70,
            "spice_tolerance": 0.90,
            "price_sensitivity": 0.40,
            "cuisine_diversity": 0.75,
            "ambiance_preference": "Lively",
            "preferred_cuisines": ["Indian", "Thai", "Mexican", "Middle Eastern"],
            "dietary_restrictions": ["vegetarian"]
        }
    },
    {
        "name": "David Kim",
        "email": "david.k@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": 0.55,
            "spice_tolerance": 0.60,
            "price_sensitivity": 0.45,
            "cuisine_diversity": 0.70,
            "ambiance_preference": "Trendy",
            "preferred_cuisines": ["Korean", "Japanese", "Chinese", "Vietnamese"],
            "dietary_restrictions": []
        }
    },
    {
        "name": "Lisa Anderson",
        "email": "lisa.a@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": 0.40,
            "spice_tolerance": 0.35,
            "price_sensitivity": 0.80,
            "cuisine_diversity": 0.35,
            "ambiance_preference": "Family-Friendly",
            "preferred_cuisines": ["Italian", "American", "Pizza"],
            "dietary_restrictions": []
        }
    }
]

DUMMY_RESTAURANTS = [
    {"id": "rest_sushi_1", "name": "Nobu Sushi", "cuisine": "Japanese"},
    {"id": "rest_thai_1", "name": "Thai Basil", "cuisine": "Thai"},
    {"id": "rest_italian_1", "name": "Bella Napoli", "cuisine": "Italian"},
    {"id": "rest_mexican_1", "name": "El Mariachi", "cuisine": "Mexican"},
    {"id": "rest_indian_1", "name": "Spice Route", "cuisine": "Indian"},
    {"id": "rest_french_1", "name": "Le Petit Bistro", "cuisine": "French"},
    {"id": "rest_burger_1", "name": "The Burger Joint", "cuisine": "American"},
    {"id": "rest_korean_1", "name": "Seoul Kitchen", "cuisine": "Korean"},
    {"id": "rest_ethiopian_1", "name": "Addis Cafe", "cuisine": "Ethiopian"},
    {"id": "rest_vietnamese_1", "name": "Pho Saigon", "cuisine": "Vietnamese"},
]

DUMMY_CHALLENGES = [
    {
        "title": "Twin Taste Explorer",
        "description": "Try 5 restaurants loved by your Taste Twins",
        "challenge_type": "restaurant_visits",
        "target_count": 5,
        "points_reward": 100
    },
    {
        "title": "Adventure Seeker",
        "description": "Try 3 new cuisines you've never had before",
        "challenge_type": "new_cuisines",
        "target_count": 3,
        "points_reward": 150
    },
    {
        "title": "Social Foodie",
        "description": "Share your TasteDNA card 3 times",
        "challenge_type": "social_shares",
        "target_count": 3,
        "points_reward": 50
    },
    {
        "title": "Review Master",
        "description": "Log interactions with 10 different restaurants",
        "challenge_type": "interactions",
        "target_count": 10,
        "points_reward": 75
    }
]

DUMMY_DISHES = [
    "Spicy Tuna Roll", "Pad Thai", "Margherita Pizza", "Tacos al Pastor",
    "Chicken Tikka Masala", "Coq au Vin", "Classic Burger", "Bibimbap",
    "Doro Wat", "Pho Bo"
]


async def clear_database():
    """Clear all existing data from database"""
    print("Clearing existing database data...")
    session = async_sessionmaker()
    async with session() as db:
        # Delete in correct order due to foreign keys
        await db.execute("DELETE FROM user_achievements")
        await db.execute("DELETE FROM user_challenges")
        await db.execute("DELETE FROM challenges")
        await db.execute("DELETE FROM date_night_pairings")
        await db.execute("DELETE FROM image_searches")
        await db.execute("DELETE FROM saved_restaurants")
        await db.execute("DELETE FROM interaction_logs")
        await db.execute("DELETE FROM twin_relationships")
        await db.execute("DELETE FROM taste_dnas")
        await db.execute("DELETE FROM users")
        await db.commit()
    print("Database cleared!")


async def create_users() -> List[User]:
    """Create dummy users with TasteDNA profiles"""
    print("\nCreating users and TasteDNA profiles...")
    users = []

    async with async_sessionmaker() as session:
        for user_data in DUMMY_USERS:
            # Create user
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                password_hash=get_password_hash(user_data["password"]),
                quiz_completed=True,
                avatar_url=f"https://i.pravatar.cc/150?u={user_data['email']}"
            )
            session.add(user)
            await session.flush()  # Get user ID

            # Create TasteDNA
            taste = user_data["taste"]
            taste_dna = TasteDNA(
                user_id=user.id,
                adventure_score=taste["adventure_score"],
                spice_tolerance=taste["spice_tolerance"],
                price_sensitivity=taste["price_sensitivity"],
                cuisine_diversity=taste["cuisine_diversity"],
                ambiance_preference=taste["ambiance_preference"],
                preferred_cuisines=taste["preferred_cuisines"],
                dietary_restrictions=taste["dietary_restrictions"],
                quiz_answers={"completed": True, "timestamp": datetime.utcnow().isoformat()}
            )
            session.add(taste_dna)

            users.append(user)
            print(f"  Created: {user.name} ({user.email})")

        await session.commit()
        print(f"Total users created: {len(users)}")

    return users


async def create_twin_relationships(users: List[User]):
    """Create twin relationships based on taste similarity"""
    print("\nCreating twin relationships...")

    async with async_sessionmaker() as session:
        twin_count = 0

        # Create some twin relationships
        # Alex (adventure) <-> James (adventure)
        twin1 = TwinRelationship(
            user_id=users[0].id,
            twin_user_id=users[2].id,
            similarity_score=0.88,
            common_cuisines=["Japanese", "Thai", "Mexican"]
        )
        session.add(twin1)
        twin_count += 1

        # Alex <-> Priya (spicy food lovers)
        twin2 = TwinRelationship(
            user_id=users[0].id,
            twin_user_id=users[5].id,
            similarity_score=0.82,
            common_cuisines=["Thai", "Mexican", "Indian"]
        )
        session.add(twin2)
        twin_count += 1

        # Sarah <-> Michael (casual, traditional)
        twin3 = TwinRelationship(
            user_id=users[1].id,
            twin_user_id=users[4].id,
            similarity_score=0.75,
            common_cuisines=["Italian", "American"]
        )
        session.add(twin3)
        twin_count += 1

        # Emily <-> David (moderate adventurers)
        twin4 = TwinRelationship(
            user_id=users[3].id,
            twin_user_id=users[6].id,
            similarity_score=0.79,
            common_cuisines=["Japanese", "Italian"]
        )
        session.add(twin4)
        twin_count += 1

        # James <-> Priya (spice lovers)
        twin5 = TwinRelationship(
            user_id=users[2].id,
            twin_user_id=users[5].id,
            similarity_score=0.85,
            common_cuisines=["Indian", "Thai"]
        )
        session.add(twin5)
        twin_count += 1

        await session.commit()
        print(f"Total twin relationships created: {twin_count}")


async def create_interactions(users: List[User]):
    """Create restaurant interaction logs"""
    print("\nCreating interaction logs...")

    async with async_sessionmaker() as session:
        interaction_count = 0
        action_types = ["view", "save", "book", "like", "dismiss"]

        for user in users[:6]:  # First 6 users have interactions
            # Each user has 5-10 interactions
            num_interactions = random.randint(5, 10)

            for _ in range(num_interactions):
                restaurant = random.choice(DUMMY_RESTAURANTS)
                interaction = InteractionLog(
                    user_id=user.id,
                    restaurant_id=restaurant["id"],
                    action_type=random.choice(action_types),
                    context={"source": "discovery", "match_score": random.uniform(0.6, 0.95)},
                    session_id=f"session_{user.id}_{random.randint(1000, 9999)}",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                session.add(interaction)
                interaction_count += 1

        await session.commit()
        print(f"Total interactions created: {interaction_count}")


async def create_saved_restaurants(users: List[User]):
    """Create saved restaurants for users"""
    print("\nCreating saved restaurants...")

    async with async_sessionmaker() as session:
        saved_count = 0

        for user in users[:5]:  # First 5 users have saved restaurants
            # Each user saves 2-4 restaurants
            num_saved = random.randint(2, 4)
            restaurants_to_save = random.sample(DUMMY_RESTAURANTS, num_saved)

            for restaurant in restaurants_to_save:
                saved = SavedRestaurant(
                    user_id=user.id,
                    restaurant_id=restaurant["id"],
                    restaurant_name=restaurant["name"],
                    restaurant_data={
                        "name": restaurant["name"],
                        "cuisine": restaurant["cuisine"],
                        "rating": random.uniform(4.0, 5.0),
                        "price": random.choice(["$", "$$", "$$$"])
                    },
                    notes=f"Want to try this {restaurant['cuisine']} place!",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 15))
                )
                session.add(saved)
                saved_count += 1

        await session.commit()
        print(f"Total saved restaurants: {saved_count}")


async def create_image_searches(users: List[User]):
    """Create image search history"""
    print("\nCreating image search history...")

    async with async_sessionmaker() as session:
        search_count = 0

        for user in users[:4]:  # First 4 users have image searches
            # Each user has 1-3 searches
            num_searches = random.randint(1, 3)

            for i in range(num_searches):
                dish = random.choice(DUMMY_DISHES)
                cuisine = random.choice(DUMMY_RESTAURANTS)["cuisine"]

                search = ImageSearch(
                    user_id=user.id,
                    image_url=f"https://example.com/food_images/{user.id}_{i}.jpg",
                    detected_dish=dish,
                    detected_cuisine=cuisine,
                    confidence_score=random.uniform(0.75, 0.95),
                    results={
                        "restaurants_found": 5,
                        "top_match": random.choice(DUMMY_RESTAURANTS)["name"]
                    },
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
                )
                session.add(search)
                search_count += 1

        await session.commit()
        print(f"Total image searches created: {search_count}")


async def create_challenges():
    """Create gamification challenges"""
    print("\nCreating gamification challenges...")

    async with async_sessionmaker() as session:
        challenges = []

        for challenge_data in DUMMY_CHALLENGES:
            challenge = Challenge(
                title=challenge_data["title"],
                description=challenge_data["description"],
                challenge_type=challenge_data["challenge_type"],
                target_count=challenge_data["target_count"],
                points_reward=challenge_data["points_reward"],
                start_date=datetime.utcnow() - timedelta(days=30),
                end_date=datetime.utcnow() + timedelta(days=30),
                active=True
            )
            session.add(challenge)
            challenges.append(challenge)

        await session.commit()
        print(f"Total challenges created: {len(challenges)}")
        return challenges


async def create_user_challenges(users: List[User], challenges: List[Challenge]):
    """Create user challenge progress"""
    print("\nCreating user challenge progress...")

    async with async_sessionmaker() as session:
        progress_count = 0

        for user in users[:6]:  # First 6 users participate in challenges
            # Each user joins 2-3 challenges
            num_challenges = random.randint(2, 3)
            user_challenges = random.sample(challenges, num_challenges)

            for challenge in user_challenges:
                progress = random.randint(0, challenge.target_count)
                completed = progress >= challenge.target_count

                user_challenge = UserChallenge(
                    user_id=user.id,
                    challenge_id=challenge.id,
                    progress=progress,
                    completed=completed,
                    completed_at=datetime.utcnow() if completed else None,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 20))
                )
                session.add(user_challenge)
                progress_count += 1

        await session.commit()
        print(f"Total user challenge progress records: {progress_count}")


async def create_achievements(users: List[User]):
    """Create user achievements"""
    print("\nCreating user achievements...")

    achievement_types = [
        "first_restaurant_saved",
        "completed_first_challenge",
        "found_10_twins",
        "tried_5_cuisines",
        "adventure_master"
    ]

    async with async_sessionmaker() as session:
        achievement_count = 0

        for user in users[:4]:  # First 4 users have achievements
            # Each user has 1-3 achievements
            num_achievements = random.randint(1, 3)

            for achievement_type in random.sample(achievement_types, num_achievements):
                achievement = UserAchievement(
                    user_id=user.id,
                    achievement_type=achievement_type,
                    achievement_data={
                        "type": achievement_type,
                        "points": random.randint(25, 100)
                    },
                    earned_at=datetime.utcnow() - timedelta(days=random.randint(0, 15))
                )
                session.add(achievement)
                achievement_count += 1

        await session.commit()
        print(f"Total achievements created: {achievement_count}")


async def create_date_night_pairings(users: List[User]):
    """Create date night pairings"""
    print("\nCreating date night pairings...")

    async with async_sessionmaker() as session:
        # Create 2 date night pairings
        pairing1 = DateNightPairing(
            user1_id=users[0].id,  # Alex
            user2_id=users[3].id,  # Emily
            compatibility_score=0.72,
            merged_preferences={
                "avg_adventure": 0.725,
                "avg_spice": 0.60,
                "common_cuisines": ["Japanese", "Italian"],
                "compromise_needed": ["price_range"]
            },
            active=True
        )
        session.add(pairing1)

        pairing2 = DateNightPairing(
            user1_id=users[1].id,  # Sarah
            user2_id=users[4].id,  # Michael
            compatibility_score=0.85,
            merged_preferences={
                "avg_adventure": 0.35,
                "avg_spice": 0.25,
                "common_cuisines": ["Italian", "American"],
                "compromise_needed": []
            },
            active=True
        )
        session.add(pairing2)

        await session.commit()
        print("Total date night pairings created: 2")


async def print_summary(users: List[User]):
    """Print summary of generated data"""
    print("\n" + "="*60)
    print("DUMMY DATA GENERATION COMPLETE")
    print("="*60)

    print("\nGenerated Test Users:")
    print("-" * 60)
    for i, user_data in enumerate(DUMMY_USERS):
        print(f"\n{i+1}. {user_data['name']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Password: {user_data['password']}")
        print(f"   Adventure Score: {user_data['taste']['adventure_score']}")
        print(f"   Spice Tolerance: {user_data['taste']['spice_tolerance']}")
        print(f"   Preferred Cuisines: {', '.join(user_data['taste']['preferred_cuisines'])}")

    print("\n" + "="*60)
    print("\nYou can now use these credentials to test the API!")
    print("Example: POST /api/v1/auth/login")
    print('  {"email": "alex.chen@example.com", "password": "password123"}')
    print("="*60 + "\n")


async def main():
    """Main function to generate all dummy data"""
    print("="*60)
    print("TasteSync Dummy Data Generator")
    print("="*60)

    try:
        # Initialize database
        print("\nInitializing database...")
        await init_db()

        # Clear existing data
        await clear_database()

        # Generate all data
        users = await create_users()
        await create_twin_relationships(users)
        await create_interactions(users)
        await create_saved_restaurants(users)
        await create_image_searches(users)

        challenges = await create_challenges()
        await create_user_challenges(users, challenges)
        await create_achievements(users)
        await create_date_night_pairings(users)

        # Print summary
        await print_summary(users)

        print("Success! Dummy data generated successfully.\n")

    except Exception as e:
        print(f"\n❌ Error generating dummy data: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
