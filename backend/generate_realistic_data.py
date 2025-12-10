"""
TasteSync Realistic Dataset Generator
Generates 100 users with comprehensive restaurant data and real images
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, text
from app.db.session import async_sessionmaker, init_db, get_db
from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.models.twin_relationship import TwinRelationship
from app.models.interaction_log import InteractionLog
from app.models.saved_restaurant import SavedRestaurant
from app.core.security import get_password_hash

# Configuration
NUM_USERS = 100
INTERACTIONS_PER_USER = 30

# Import data from large dataset generator
CUISINES = [
    "Italian", "Japanese", "Mexican", "Chinese", "Indian", "Thai", "French",
    "Mediterranean", "Korean", "Vietnamese", "American", "Middle Eastern",
    "Greek", "Spanish", "Ethiopian", "Brazilian", "Peruvian", "Turkish"
]

AMBIANCES = ["Casual", "Trendy", "Upscale", "Cozy", "Romantic", "Lively", "Fine Dining"]

DIETARY_OPTIONS = ["none", "vegetarian", "vegan", "gluten-free", "dairy-free", "halal", "kosher"]

FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William",
    "Mia", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn", "Alexander"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
]

# Restaurant images
FOOD_IMAGES = {
    "Italian": [
        "https://images.unsplash.com/photo-1595295333158-4742f28fbd85?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800&h=600&fit=crop",
    ],
    "Japanese": [
        "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=800&h=600&fit=crop",
    ],
    "Mexican": [
        "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1599974607841-f2a5e04b2a0a?w=800&h=600&fit=crop",
    ],
    "American": [
        "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=800&h=600&fit=crop",
    ],
}


def generate_user_data(index: int) -> Dict:
    """Generate realistic user data"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    adventure_score = round(random.uniform(0.1, 1.0), 2)
    spice_tolerance = round(random.uniform(0.0, 1.0), 2)
    num_cuisines = max(3, min(8, int(adventure_score * 8) + random.randint(0, 3)))

    return {
        "name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{last_name.lower()}{index}@example.com",
        "password": "password123",
        "taste": {
            "adventure_score": adventure_score,
            "spice_tolerance": spice_tolerance,
            "price_sensitivity": round(random.uniform(0.0, 1.0), 2),
            "cuisine_diversity": round(random.uniform(0.2, 1.0), 2),
            "ambiance_preference": random.choice(AMBIANCES),
            "preferred_cuisines": random.sample(CUISINES, num_cuisines),
            "dietary_restrictions": random.sample(DIETARY_OPTIONS[:7], random.randint(0, 2))
        }
    }


def generate_restaurant_data(restaurant_id: str, cuisine: str) -> Dict:
    """Generate restaurant data with images"""
    image_url = FOOD_IMAGES.get(cuisine, ["https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&h=600&fit=crop"])[0]

    return {
        "id": restaurant_id,
        "name": f"{random.choice(['The', 'La'])} {random.choice(['Golden', 'Modern'])} {cuisine}",
        "image_url": image_url,
        "rating": round(random.uniform(3.5, 5.0), 1),
        "review_count": random.randint(50, 2000),
        "price": random.choice(["$", "$$", "$$$", "$$$$"]),
        "categories": [{"alias": cuisine.lower(), "title": cuisine}],
        "location": {
            "address1": f"{random.randint(100, 9999)} Main St",
            "city": random.choice(["San Francisco", "New York", "Los Angeles"]),
            "state": random.choice(["CA", "NY"]),
            "zip_code": f"{random.randint(10000, 99999)}"
        }
    }


async def clear_database(db):
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    await db.execute(text("DELETE FROM user_achievements"))
    await db.execute(text("DELETE FROM user_challenges"))
    await db.execute(text("DELETE FROM challenges"))
    await db.execute(text("DELETE FROM date_night_pairings"))
    await db.execute(text("DELETE FROM image_searches"))
    await db.execute(text("DELETE FROM saved_restaurants"))
    await db.execute(text("DELETE FROM interaction_logs"))
    await db.execute(text("DELETE FROM twin_relationships"))
    await db.execute(text("DELETE FROM taste_dna"))
    await db.execute(text("DELETE FROM users"))
    await db.commit()
    print("✅ Database cleared\n")


async def create_users_and_data(db):
    """Create all users and related data"""
    print(f"👥 Creating {NUM_USERS} users with TasteDNA profiles...")

    users = []
    for i in range(NUM_USERS):
        user_data = generate_user_data(i + 1)
        hashed_password = get_password_hash(user_data["password"])

        user = User(
            name=user_data["name"],
            email=user_data["email"],
            hashed_password=hashed_password,
            quiz_completed=True
        )
        db.add(user)
        await db.flush()

        taste_dna = TasteDNA(
            user_id=user.id,
            adventure_score=user_data["taste"]["adventure_score"],
            spice_tolerance=user_data["taste"]["spice_tolerance"],
            price_sensitivity=user_data["taste"]["price_sensitivity"],
            cuisine_diversity=user_data["taste"]["cuisine_diversity"],
            ambiance_preference=user_data["taste"]["ambiance_preference"],
            preferred_cuisines=user_data["taste"]["preferred_cuisines"],
            dietary_restrictions=user_data["taste"]["dietary_restrictions"],
            quiz_answers=[]
        )
        db.add(taste_dna)
        users.append(user)

        if (i + 1) % 25 == 0:
            await db.commit()
            print(f"  ✓ Created {i + 1} users...")

    await db.commit()
    print(f"✅ Created {NUM_USERS} users with TasteDNA\n")
    return users


async def create_interactions(db, users):
    """Create restaurant interactions"""
    print(f"💾 Creating interactions and saved restaurants...")

    # Create restaurant pool
    restaurant_pool = []
    for cuisine in CUISINES[:10]:  # Use 10 cuisines
        for i in range(20):  # 20 restaurants per cuisine = 200 total
            restaurant_id = f"yelp_{cuisine.lower()}_{i}"
            restaurant_pool.append(generate_restaurant_data(restaurant_id, cuisine))

    result = await db.execute(select(TasteDNA))
    taste_dnas = {td.user_id: td for td in result.scalars().all()}

    interactions_created = 0
    saved_count = 0

    for user in users:
        user_taste = taste_dnas[user.id]
        preferred_restaurants = [
            r for r in restaurant_pool
            if r["categories"][0]["title"] in user_taste.preferred_cuisines
        ]

        num_interactions = random.randint(15, INTERACTIONS_PER_USER)
        selected_restaurants = random.sample(
            preferred_restaurants if preferred_restaurants else restaurant_pool,
            min(num_interactions, len(preferred_restaurants if preferred_restaurants else restaurant_pool))
        )

        for restaurant in selected_restaurants:
            action = random.choices(["view", "save", "book"], weights=[50, 30, 20])[0]

            interaction = InteractionLog(
                user_id=user.id,
                restaurant_id=restaurant["id"],
                action_type=action,
                metadata={
                    "restaurant_name": restaurant["name"],
                    "cuisine": restaurant["categories"][0]["title"],
                    "price": restaurant["price"],
                    "rating": restaurant["rating"]
                },
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 90))
            )
            db.add(interaction)
            interactions_created += 1

            if action in ["save", "book"]:
                saved = SavedRestaurant(
                    user_id=user.id,
                    restaurant_id=restaurant["id"],
                    restaurant_name=restaurant["name"],
                    restaurant_data=restaurant,
                    notes=random.choice(["Must try!", "Great spot", None])
                )
                db.add(saved)
                saved_count += 1

        if interactions_created % 500 == 0 and interactions_created > 0:
            await db.commit()
            print(f"  ✓ Created {interactions_created} interactions...")

    await db.commit()
    print(f"✅ Created {interactions_created} interactions and {saved_count} saved restaurants\n")


async def create_twins(db, users):
    """Create twin relationships"""
    print("🤝 Creating twin relationships...")

    result = await db.execute(select(TasteDNA))
    taste_dnas = {td.user_id: td for td in result.scalars().all()}

    relationships_created = 0

    for user in users:
        user_taste = taste_dnas[user.id]
        similarities = []

        for other_user in users:
            if other_user.id == user.id:
                continue

            other_taste = taste_dnas[other_user.id]
            score = 1.0
            score -= abs(user_taste.adventure_score - other_taste.adventure_score) * 0.3
            score -= abs(user_taste.spice_tolerance - other_taste.spice_tolerance) * 0.2

            common_cuisines = set(user_taste.preferred_cuisines) & set(other_taste.preferred_cuisines)
            score += len(common_cuisines) * 0.05

            similarities.append((other_user.id, max(0, min(1, score))))

        similarities.sort(key=lambda x: x[1], reverse=True)

        for twin_id, similarity in similarities[:10]:  # Top 10 twins
            if similarity > 0.5:
                relationship = TwinRelationship(
                    user_id=user.id,
                    twin_user_id=twin_id,
                    similarity_score=round(similarity, 3),
                    common_cuisines=list(set(user_taste.preferred_cuisines) & set(taste_dnas[twin_id].preferred_cuisines))
                )
                db.add(relationship)
                relationships_created += 1

    await db.commit()
    print(f"✅ Created {relationships_created} twin relationships\n")


async def main():
    """Main data generation flow"""
    print("=" * 60)
    print("TasteSync Realistic Dataset Generator")
    print("=" * 60 + "\n")

    await init_db()

    async for db in get_db():
        try:
            await clear_database(db)
            users = await create_users_and_data(db)
            await create_twins(db, users)
            await create_interactions(db, users)

            print("=" * 60)
            print("✨ Dataset generation complete!")
            print("=" * 60)
            print(f"📊 Summary:")
            print(f"  - Users: {NUM_USERS}")
            print(f"  - Restaurant pool: ~200 with real images")
            print(f"  - Interactions: ~{INTERACTIONS_PER_USER} per user")
            print(f"  - Quiz images: Real Unsplash URLs")
            print("=" * 60)
        finally:
            break


if __name__ == "__main__":
    asyncio.run(main())
