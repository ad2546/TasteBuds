"""
Fast user addition - directly inserts users with same password hash
This is for demo/testing purposes only
"""

import asyncio
import random
import uuid
from datetime import datetime
from app.db.session import init_db, get_db
from sqlalchemy import text

FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
    "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
    "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Aiden", "Avery",
    "Jackson", "Ella", "Sebastian", "Scarlett", "David", "Grace", "Joseph",
    "Chloe", "Samuel", "Victoria", "Carter", "Riley", "Owen", "Aria", "Wyatt"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez"
]

CUISINES = [
    "Italian", "Japanese", "Mexican", "Chinese", "Indian", "Thai", "French",
    "Mediterranean", "Korean", "Vietnamese", "American", "Middle Eastern",
    "Greek", "Spanish", "Ethiopian", "Brazilian", "Peruvian", "Turkish"
]

AMBIANCES = ["Casual", "Trendy", "Upscale", "Cozy", "Romantic", "Lively", "Fine Dining"]

# Pre-computed bcrypt hash for "password123" - same for all users (demo only)
PASSWORD_HASH = "$2b$12$YQ7FqvYFZlijlqmlZncKiuN7EUQ8wSe9nBEjfd/kFyvTI8mpR41v."

async def add_users_fast(num_users=50):
    """Add users quickly using raw SQL"""
    print(f"Adding {num_users} users (fast mode)...")

    await init_db()

    async for db in get_db():
        try:
            users_added = 0

            for i in range(num_users):
                user_id = str(uuid.uuid4())
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                name = f"{first} {last}"
                email = f"{first.lower()}.{last.lower()}{random.randint(100, 999)}@example.com"

                # Insert user
                await db.execute(text("""
                    INSERT INTO users (id, email, password_hash, name, avatar_url, quiz_completed, created_at, updated_at)
                    VALUES (:id, :email, :password_hash, :name, :avatar_url, :quiz_completed, :created_at, :updated_at)
                """), {
                    "id": user_id,
                    "email": email,
                    "password_hash": PASSWORD_HASH,
                    "name": name,
                    "avatar_url": f"https://i.pravatar.cc/150?u={email}",
                    "quiz_completed": 1,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })

                # Insert TasteDNA
                dna_id = str(uuid.uuid4())
                adventure = round(random.uniform(0.1, 1.0), 2)
                spice = round(random.uniform(0.0, 1.0), 2)
                num_cuisines = random.randint(3, 8)
                cuisines = random.sample(CUISINES, num_cuisines)

                await db.execute(text("""
                    INSERT INTO taste_dna (
                        id, user_id, adventure_score, spice_tolerance,
                        price_sensitivity, cuisine_diversity, ambiance_preference,
                        preferred_cuisines, dietary_restrictions, quiz_answers,
                        created_at, updated_at
                    ) VALUES (
                        :id, :user_id, :adventure, :spice,
                        :price, :diversity, :ambiance,
                        :cuisines, :dietary, :quiz,
                        :created_at, :updated_at
                    )
                """), {
                    "id": dna_id,
                    "user_id": user_id,
                    "adventure": adventure,
                    "spice": spice,
                    "price": round(random.uniform(0.0, 1.0), 2),
                    "diversity": round(random.uniform(0.2, 1.0), 2),
                    "ambiance": random.choice(AMBIANCES),
                    "cuisines": str(cuisines).replace("'", '"'),
                    "dietary": "[]",
                    "quiz": "[]",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })

                users_added += 1

                if (i + 1) % 10 == 0:
                    await db.commit()
                    print(f"  Added {i + 1} users...")

            await db.commit()
            print(f"\n✅ Successfully added {users_added} users!")
            print("📧 All users have password: password123")

        finally:
            break

if __name__ == "__main__":
    asyncio.run(add_users_fast(50))
