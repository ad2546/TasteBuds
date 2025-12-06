"""
TasteSync Large Dataset Generator
Generates 1000 users and comprehensive restaurant data with real images
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
NUM_USERS = 1000
INTERACTIONS_PER_USER = 50

# Real cuisine types
CUISINES = [
    "Italian", "Japanese", "Mexican", "Chinese", "Indian", "Thai", "French",
    "Mediterranean", "Korean", "Vietnamese", "American", "Middle Eastern",
    "Greek", "Spanish", "Ethiopian", "Brazilian", "Peruvian", "Turkish",
    "Lebanese", "Moroccan", "Caribbean", "Filipino", "Indonesian", "Malaysian",
    "German", "British", "Irish", "Russian", "Polish", "Scandinavian"
]

# Ambiance types
AMBIANCES = ["Casual", "Trendy", "Upscale", "Cozy", "Romantic", "Lively", "Fine Dining", "Family-Friendly"]

# Dietary restrictions
DIETARY_OPTIONS = ["none", "vegetarian", "vegan", "gluten-free", "dairy-free", "halal", "kosher", "pescatarian"]

# First and last names for realistic user generation
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William",
    "Mia", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn", "Alexander",
    "Abigail", "Michael", "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Aiden", "Avery", "Jackson",
    "Ella", "Sebastian", "Scarlett", "David", "Grace", "Joseph", "Chloe", "Samuel", "Victoria", "Carter",
    "Riley", "Owen", "Aria", "Wyatt", "Lily", "John", "Aubrey", "Jack", "Zoey", "Luke",
    "Penelope", "Jayden", "Lillian", "Dylan", "Addison", "Grayson", "Layla", "Levi", "Natalie", "Isaac",
    "Camila", "Gabriel", "Hannah", "Julian", "Brooklyn", "Mateo", "Zoe", "Anthony", "Nora", "Jaxon",
    "Leah", "Lincoln", "Savannah", "Joshua", "Audrey", "Christopher", "Claire", "Andrew", "Eleanor", "Theodore",
    "Skylar", "Caleb", "Ellie", "Ryan", "Stella", "Asher", "Paisley", "Nathan", "Violet", "Thomas",
    "Mila", "Leo", "Allison", "Isaiah", "Hazel", "Charles", "Lucy", "Josiah", "Anna", "Hudson"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez"
]

# Restaurant image URLs from Unsplash (food/restaurant themed)
RESTAURANT_IMAGES = [
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",  # Restaurant interior
    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5",  # Restaurant table
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0",  # Restaurant dining
    "https://images.unsplash.com/photo-1551218808-94e220e084d2",  # Modern restaurant
    "https://images.unsplash.com/photo-1552566626-52f8b828add9",  # Fine dining
    "https://images.unsplash.com/photo-1592861956120-e524fc739696",  # Cozy restaurant
    "https://images.unsplash.com/photo-1578474846511-04ba529f0b88",  # Outdoor dining
    "https://images.unsplash.com/photo-1552566626-52f8b828add9",  # Elegant setting
]

# Food images from Unsplash
FOOD_IMAGES = {
    "Italian": [
        "https://images.unsplash.com/photo-1595295333158-4742f28fbd85",  # Pizza
        "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9",  # Pasta
        "https://images.unsplash.com/photo-1574894709920-11b28e7367e3",  # Lasagna
    ],
    "Japanese": [
        "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351",  # Sushi
        "https://images.unsplash.com/photo-1617093727343-374698b1b08d",  # Ramen
        "https://images.unsplash.com/photo-1588561808747-3c0b1e5f8f63",  # Sushi platter
    ],
    "Mexican": [
        "https://images.unsplash.com/photo-1565299585323-38d6b0865b47",  # Tacos
        "https://images.unsplash.com/photo-1599974607841-f2a5e04b2a0a",  # Burritos
        "https://images.unsplash.com/photo-1613514785940-daed07799d1e",  # Nachos
    ],
    "Chinese": [
        "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43",  # Dim sum
        "https://images.unsplash.com/photo-1585032226651-759b368d7246",  # Noodles
        "https://images.unsplash.com/photo-1559314809-0d155014e29e",  # Chinese food
    ],
    "Indian": [
        "https://images.unsplash.com/photo-1585937421612-70a008356fbe",  # Curry
        "https://images.unsplash.com/photo-1596797038530-2c107229654b",  # Biryani
        "https://images.unsplash.com/photo-1565557623262-b51c2513a641",  # Tandoori
    ],
    "Thai": [
        "https://images.unsplash.com/photo-1559314809-0d155014e29e",  # Thai curry
        "https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4",  # Pad Thai
        "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43",  # Thai dishes
    ],
    "American": [
        "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",  # Burger
        "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5",  # BBQ
        "https://images.unsplash.com/photo-1551248429-40975aa4de74",  # Steak
    ],
}


def generate_user_data(index: int) -> Dict:
    """Generate realistic user data"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{index}@example.com"

    # Generate varied taste preferences
    adventure_score = round(random.uniform(0.1, 1.0), 2)
    spice_tolerance = round(random.uniform(0.0, 1.0), 2)
    price_sensitivity = round(random.uniform(0.0, 1.0), 2)
    cuisine_diversity = round(random.uniform(0.2, 1.0), 2)

    # More adventurous users prefer diverse cuisines
    num_cuisines = max(3, min(8, int(adventure_score * 8) + random.randint(0, 3)))
    preferred_cuisines = random.sample(CUISINES, num_cuisines)

    # Dietary restrictions (most users have none or one)
    dietary_count = random.choices([0, 1, 2], weights=[70, 25, 5])[0]
    dietary_restrictions = random.sample([d for d in DIETARY_OPTIONS if d != "none"], dietary_count)

    return {
        "name": name,
        "email": email,
        "password": "password123",
        "taste": {
            "adventure_score": adventure_score,
            "spice_tolerance": spice_tolerance,
            "price_sensitivity": price_sensitivity,
            "cuisine_diversity": cuisine_diversity,
            "ambiance_preference": random.choice(AMBIANCES),
            "preferred_cuisines": preferred_cuisines,
            "dietary_restrictions": dietary_restrictions
        }
    }


def generate_restaurant_data(restaurant_id: str, cuisine: str) -> Dict:
    """Generate realistic restaurant data with images"""
    # Get cuisine-specific images or fall back to general food images
    if cuisine in FOOD_IMAGES:
        image_url = random.choice(FOOD_IMAGES[cuisine])
    else:
        image_url = random.choice(RESTAURANT_IMAGES)

    # Add query parameters for proper image sizing
    image_url = f"{image_url}?w=800&h=600&fit=crop&crop=entropy"

    return {
        "id": restaurant_id,
        "name": f"{random.choice(['The', 'La', 'Il', 'Le', 'Chez'])} {random.choice(['Golden', 'Silver', 'Royal', 'Grand', 'Modern', 'Classic', 'Urban', 'Rustic'])} {cuisine}",
        "image_url": image_url,
        "rating": round(random.uniform(3.5, 5.0), 1),
        "review_count": random.randint(50, 5000),
        "price": random.choice(["$", "$$", "$$$", "$$$$"]),
        "categories": [{"alias": cuisine.lower(), "title": cuisine}],
        "location": {
            "address1": f"{random.randint(100, 9999)} Main St",
            "city": random.choice(["San Francisco", "New York", "Los Angeles", "Chicago", "Austin", "Seattle", "Portland", "Boston"]),
            "state": random.choice(["CA", "NY", "IL", "TX", "WA", "OR", "MA"]),
            "zip_code": f"{random.randint(10000, 99999)}"
        }
    }


async def clear_database(db):
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")

    # Delete in reverse order of dependencies
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
    print("✅ Database cleared")


async def create_users_with_taste_dna(db, num_users: int = NUM_USERS):
    """Create users with taste DNA profiles"""
    print(f"\n👥 Creating {num_users} users with TasteDNA profiles...")

    users = []
    for i in range(num_users):
        user_data = generate_user_data(i + 1)

        # Create user
        hashed_password = get_password_hash(user_data["password"])
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            hashed_password=hashed_password,
            quiz_completed=True
        )
        db.add(user)
        await db.flush()  # Get user.id

        # Create TasteDNA
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

        if (i + 1) % 100 == 0:
            await db.commit()
            print(f"  ✓ Created {i + 1} users...")

    await db.commit()
    print(f"✅ Created {num_users} users with TasteDNA")
    return users


async def create_twin_relationships(db, users: List[User]):
    """Create twin relationships based on taste similarity"""
    print("\n🤝 Creating twin relationships...")

    # Get all taste DNAs
    result = await db.execute(select(TasteDNA))
    taste_dnas = {td.user_id: td for td in result.scalars().all()}

    relationships_created = 0

    for user in users[:500]:  # Create relationships for first 500 users to save time
        user_taste = taste_dnas[user.id]

        # Find similar users
        similarities = []
        for other_user in users:
            if other_user.id == user.id:
                continue

            other_taste = taste_dnas[other_user.id]

            # Calculate simple similarity score
            score = 1.0
            score -= abs(user_taste.adventure_score - other_taste.adventure_score) * 0.3
            score -= abs(user_taste.spice_tolerance - other_taste.spice_tolerance) * 0.2
            score -= abs(user_taste.price_sensitivity - other_taste.price_sensitivity) * 0.2
            score -= abs(user_taste.cuisine_diversity - other_taste.cuisine_diversity) * 0.3

            # Cuisine overlap bonus
            common_cuisines = set(user_taste.preferred_cuisines) & set(other_taste.preferred_cuisines)
            score += len(common_cuisines) * 0.05

            similarities.append((other_user.id, max(0, min(1, score))))

        # Get top 20 twins
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_twins = similarities[:20]

        for twin_id, similarity in top_twins:
            if similarity > 0.5:  # Only create if reasonably similar
                relationship = TwinRelationship(
                    user_id=user.id,
                    twin_user_id=twin_id,
                    similarity_score=round(similarity, 3),
                    common_cuisines=list(set(user_taste.preferred_cuisines) & set(taste_dnas[twin_id].preferred_cuisines))
                )
                db.add(relationship)
                relationships_created += 1

        if relationships_created % 500 == 0 and relationships_created > 0:
            await db.commit()
            print(f"  ✓ Created {relationships_created} relationships...")

    await db.commit()
    print(f"✅ Created {relationships_created} twin relationships")


async def create_interactions_and_saved_restaurants(db, users: List[User]):
    """Create interaction logs and saved restaurants with real images"""
    print(f"\n💾 Creating interactions and saved restaurants...")

    # Get all taste DNAs
    result = await db.execute(select(TasteDNA))
    taste_dnas = {td.user_id: td for td in result.scalars().all()}

    interactions_created = 0
    saved_count = 0

    # Create a pool of restaurants (simulate real restaurants from Yelp)
    restaurant_pool = []
    for cuisine in CUISINES:
        for i in range(30):  # 30 restaurants per cuisine = 900 total
            restaurant_id = f"yelp_{cuisine.lower()}_{i}"
            restaurant_pool.append(generate_restaurant_data(restaurant_id, cuisine))

    for user in users[:500]:  # Create interactions for first 500 users
        user_taste = taste_dnas[user.id]

        # Users interact more with restaurants matching their preferences
        preferred_restaurants = [
            r for r in restaurant_pool
            if r["categories"][0]["title"] in user_taste.preferred_cuisines
        ]
        other_restaurants = [
            r for r in restaurant_pool
            if r["categories"][0]["title"] not in user_taste.preferred_cuisines
        ]

        # Mix of preferred (70%) and exploratory (30%)
        num_interactions = random.randint(20, INTERACTIONS_PER_USER)
        preferred_count = int(num_interactions * 0.7)

        selected_restaurants = (
            random.sample(preferred_restaurants, min(preferred_count, len(preferred_restaurants))) +
            random.sample(other_restaurants, min(num_interactions - preferred_count, len(other_restaurants)))
        )

        for restaurant in selected_restaurants:
            # Random interaction type
            action = random.choices(
                ["view", "save", "book", "dismiss"],
                weights=[50, 25, 15, 10]
            )[0]

            # Create interaction log
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

            # Save restaurant if action is save or book
            if action in ["save", "book"]:
                saved = SavedRestaurant(
                    user_id=user.id,
                    restaurant_id=restaurant["id"],
                    restaurant_name=restaurant["name"],
                    restaurant_data=restaurant,
                    notes=random.choice([
                        "Must try!",
                        "Great for date night",
                        "Recommended by twin",
                        "Love their menu",
                        None
                    ])
                )
                db.add(saved)
                saved_count += 1

        if interactions_created % 1000 == 0 and interactions_created > 0:
            await db.commit()
            print(f"  ✓ Created {interactions_created} interactions, {saved_count} saved restaurants...")

    await db.commit()
    print(f"✅ Created {interactions_created} interactions and {saved_count} saved restaurants")


async def main():
    """Main data generation flow"""
    print("=" * 60)
    print("TasteSync Large Dataset Generator")
    print("=" * 60)

    # Initialize database
    await init_db()

    async for db in get_db():
        try:
            # Clear existing data
            await clear_database(db)

            # Create users with taste DNA
            users = await create_users_with_taste_dna(db, NUM_USERS)

            # Create twin relationships
            await create_twin_relationships(db, users)

            # Create interactions and saved restaurants
            await create_interactions_and_saved_restaurants(db, users)

            print("\n" + "=" * 60)
            print("✨ Dataset generation complete!")
            print("=" * 60)
            print(f"📊 Summary:")
            print(f"  - Users: {NUM_USERS}")
            print(f"  - TasteDNA profiles: {NUM_USERS}")
            print(f"  - Twin relationships: Created based on similarity")
            print(f"  - Interactions: ~{INTERACTIONS_PER_USER} per user (first 500 users)")
            print(f"  - Saved restaurants: Mix of preferences")
            print(f"  - Restaurant images: Real Unsplash URLs")
            print("=" * 60)
        finally:
            break


if __name__ == "__main__":
    asyncio.run(main())
