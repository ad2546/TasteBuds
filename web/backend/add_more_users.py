"""
Add more users to TasteSync database
Quickly adds 50 additional users with varied taste profiles
"""

import asyncio
import random
from app.db.session import init_db, get_db
from app.models.user import User
from app.models.taste_dna import TasteDNA
from app.core.security import get_password_hash

FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
    "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
    "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Aiden", "Avery",
    "Jackson", "Ella", "Sebastian", "Scarlett", "David", "Grace", "Joseph",
    "Chloe", "Samuel", "Victoria", "Carter", "Riley", "Owen", "Aria"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark"
]

CUISINES = [
    "Italian", "Japanese", "Mexican", "Chinese", "Indian", "Thai", "French",
    "Mediterranean", "Korean", "Vietnamese", "American", "Middle Eastern",
    "Greek", "Spanish", "Ethiopian", "Brazilian"
]

AMBIANCES = ["Casual", "Trendy", "Upscale", "Cozy", "Romantic", "Lively"]

async def add_users(num_users=50):
    """Add more users to database"""
    print(f"Adding {num_users} new users...")

    await init_db()

    async for db in get_db():
        try:
            users_added = 0

            for i in range(num_users):
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                name = f"{first} {last}"
                email = f"{first.lower()}.{last.lower()}{random.randint(100, 999)}@example.com"

                # Varied taste profiles
                adventure = round(random.uniform(0.1, 1.0), 2)
                spice = round(random.uniform(0.0, 1.0), 2)
                num_cuisines = random.randint(3, 8)

                user = User(
                    name=name,
                    email=email,
                    hashed_password=get_password_hash("password123"),
                    quiz_completed=True,
                    avatar_url=f"https://i.pravatar.cc/150?u={email}"
                )
                db.add(user)
                await db.flush()

                taste_dna = TasteDNA(
                    user_id=user.id,
                    adventure_score=adventure,
                    spice_tolerance=spice,
                    price_sensitivity=round(random.uniform(0.0, 1.0), 2),
                    cuisine_diversity=round(random.uniform(0.2, 1.0), 2),
                    ambiance_preference=random.choice(AMBIANCES),
                    preferred_cuisines=random.sample(CUISINES, num_cuisines),
                    dietary_restrictions=[],
                    quiz_answers=[]
                )
                db.add(taste_dna)
                users_added += 1

                if (i + 1) % 10 == 0:
                    await db.commit()
                    print(f"  Added {i + 1} users...")

            await db.commit()
            print(f"\n✅ Successfully added {users_added} new users!")

        finally:
            break

if __name__ == "__main__":
    asyncio.run(add_users(50))
