"""
Add comprehensive data: saved restaurants and interactions for all users
"""

import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from app.db.session import init_db, get_db
from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.models.saved_restaurant import SavedRestaurant
from app.models.interaction_log import InteractionLog

# Real Unsplash food images by cuisine
FOOD_IMAGES = {
    "Italian": [
        "https://images.unsplash.com/photo-1595295333158-4742f28fbd85?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=800&h=600&fit=crop",
    ],
    "Japanese": [
        "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1553621042-f6e147245754?w=800&h=600&fit=crop",
    ],
    "Mexican": [
        "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1599974607841-f2a5e04b2a0a?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1552332386-f8dd00dc2f85?w=800&h=600&fit=crop",
    ],
    "American": [
        "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1550547660-d9450f859349?w=800&h=600&fit=crop",
    ],
    "Indian": [
        "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1574484284002-952d92456975?w=800&h=600&fit=crop",
    ],
    "Thai": [
        "https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&h=600&fit=crop",
    ],
    "Chinese": [
        "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&h=600&fit=crop",
    ],
    "French": [
        "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1564834744159-ff0ea41ba4b9?w=800&h=600&fit=crop",
    ],
}

RESTAURANT_NAMES = {
    "Italian": ["Bella Notte", "Luigi's Kitchen", "Pasta Paradise", "The Italian Corner", "Roma Trattoria"],
    "Japanese": ["Sakura Sushi", "Tokyo Garden", "Ramen House", "Sushi Palace", "Zen Kitchen"],
    "Mexican": ["El Mariachi", "Taco Haven", "Cantina Mexicana", "Casa de Tacos", "Fiesta Grill"],
    "American": ["The Burger Joint", "Classic Diner", "BBQ Pit", "Steakhouse 52", "All-American Grill"],
    "Indian": ["Taj Palace", "Curry House", "Spice Route", "Mumbai Kitchen", "Royal Indian"],
    "Thai": ["Thai Basil", "Bangkok Street", "Pad Thai Express", "Orchid Thai", "Lemongrass"],
    "Chinese": ["Golden Dragon", "Szechuan Palace", "Wok & Roll", "Peking House", "Fortune Garden"],
    "French": ["Le Bistro", "Café Paris", "La Maison", "French Quarter", "Petit Restaurant"],
}

CITIES = ["San Francisco", "New York", "Los Angeles", "Chicago", "Seattle", "Boston", "Austin", "Portland"]


def generate_restaurant(cuisine: str, index: int):
    """Generate realistic restaurant data"""
    name = random.choice(RESTAURANT_NAMES.get(cuisine, ["Restaurant"]))
    images = FOOD_IMAGES.get(cuisine, ["https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&h=600&fit=crop"])

    return {
        "id": f"yelp_{cuisine.lower()}_{index}_{random.randint(1000, 9999)}",
        "name": f"{name} - {random.choice(['Downtown', 'Uptown', 'Midtown', 'District'])}",
        "image_url": random.choice(images),
        "rating": round(random.uniform(3.5, 5.0), 1),
        "review_count": random.randint(50, 2000),
        "price": random.choice(["$", "$$", "$$$", "$$$$"]),
        "categories": [{"alias": cuisine.lower(), "title": cuisine}],
        "location": {
            "address1": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Market', 'Broadway'])} St",
            "city": random.choice(CITIES),
            "state": random.choice(["CA", "NY", "IL", "TX", "WA"]),
            "zip_code": f"{random.randint(10000, 99999)}",
        },
        "phone": f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
        "distance": round(random.uniform(0.5, 15.0), 1),
    }


async def add_restaurants_and_interactions():
    """Add saved restaurants and interactions for all users"""
    print("=" * 60)
    print("Adding Comprehensive User Data")
    print("=" * 60)

    await init_db()

    async for db in get_db():
        try:
            # Get all users with their taste DNA
            result = await db.execute(
                select(User, TasteDNA).join(TasteDNA, User.id == TasteDNA.user_id)
            )
            users_with_dna = result.all()

            print(f"\n📊 Processing {len(users_with_dna)} users...")

            # Generate restaurant pool (200 restaurants)
            all_cuisines = ["Italian", "Japanese", "Mexican", "American", "Indian", "Thai", "Chinese", "French"]
            restaurant_pool = []

            for cuisine in all_cuisines:
                for i in range(25):  # 25 restaurants per cuisine
                    restaurant_pool.append(generate_restaurant(cuisine, i))

            print(f"🍽️  Generated {len(restaurant_pool)} restaurants")

            interactions_created = 0
            saved_created = 0

            for idx, (user, taste_dna) in enumerate(users_with_dna):
                # Filter restaurants by user's preferred cuisines
                user_cuisines = [c.lower() for c in (taste_dna.preferred_cuisines or [])]

                # Get restaurants matching user preferences
                matching_restaurants = [
                    r for r in restaurant_pool
                    if r["categories"][0]["alias"] in user_cuisines
                ]

                # If no matches, use all restaurants
                if not matching_restaurants:
                    matching_restaurants = restaurant_pool

                # Each user gets 10-20 interactions
                num_interactions = random.randint(10, 20)
                selected = random.sample(
                    matching_restaurants,
                    min(num_interactions, len(matching_restaurants))
                )

                for restaurant in selected:
                    # Create interaction (view, save, or book)
                    action = random.choices(
                        ["view", "save", "book"],
                        weights=[50, 30, 20]
                    )[0]

                    interaction = InteractionLog(
                        user_id=user.id,
                        restaurant_id=restaurant["id"],
                        action_type=action,
                        metadata={
                            "restaurant_name": restaurant["name"],
                            "cuisine": restaurant["categories"][0]["title"],
                            "price": restaurant["price"],
                            "rating": restaurant["rating"],
                        },
                        timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 90))
                    )
                    db.add(interaction)
                    interactions_created += 1

                    # If saved or booked, add to saved restaurants
                    if action in ["save", "book"]:
                        saved = SavedRestaurant(
                            user_id=user.id,
                            restaurant_id=restaurant["id"],
                            restaurant_name=restaurant["name"],
                            restaurant_data=restaurant,
                            notes=random.choice([
                                "Must try!",
                                "Great atmosphere",
                                "Recommended by a friend",
                                "Perfect for date night",
                                None
                            ])
                        )
                        db.add(saved)
                        saved_created += 1

                if (idx + 1) % 20 == 0:
                    await db.commit()
                    print(f"  ✓ Processed {idx + 1} users...")

            await db.commit()

            print(f"\n✅ Successfully added:")
            print(f"   - {interactions_created} interactions")
            print(f"   - {saved_created} saved restaurants")
            print("=" * 60)

        finally:
            break


if __name__ == "__main__":
    asyncio.run(add_restaurants_and_interactions())
