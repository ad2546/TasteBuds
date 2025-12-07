"""
Script to populate database with real San Francisco restaurants from Yelp API.
This will clean existing restaurant data and fetch fresh data from Yelp.
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.session import async_session_maker
from app.services.yelp_service import yelp_service
from app.models.saved_restaurant import SavedRestaurant
from app.models.interaction_log import InteractionLog


async def clean_restaurant_data(db: AsyncSession):
    """Clean all restaurant-related data from database."""
    print("🧹 Cleaning existing restaurant data...")

    # Delete interaction logs
    await db.execute(delete(InteractionLog))
    print("  ✓ Cleared interaction logs")

    # Delete saved restaurants
    await db.execute(delete(SavedRestaurant))
    print("  ✓ Cleared saved restaurants")

    await db.commit()
    print("✅ Database cleaned successfully\n")


async def fetch_sf_restaurants(limit: int = 50):
    """Fetch restaurants from Yelp API for San Francisco area."""
    print(f"🔍 Fetching {limit} restaurants from Yelp for San Francisco...")

    all_restaurants = []
    offset = 0
    batch_size = 50  # Yelp's max limit per request

    while len(all_restaurants) < limit:
        try:
            # Fetch batch of restaurants
            results = await yelp_service.search_businesses(
                term="restaurants",
                location="San Francisco, CA",
                sort_by="rating",
                limit=min(batch_size, limit - len(all_restaurants)),
                offset=offset,
            )

            businesses = results.get("businesses", [])
            if not businesses:
                break

            all_restaurants.extend(businesses)
            print(f"  📍 Fetched {len(businesses)} restaurants (total: {len(all_restaurants)})")

            offset += len(businesses)

            # Stop if we've reached the limit or no more results
            if len(businesses) < batch_size or len(all_restaurants) >= limit:
                break

        except Exception as e:
            print(f"  ⚠️  Error fetching batch at offset {offset}: {e}")
            break

    print(f"✅ Successfully fetched {len(all_restaurants)} restaurants from Yelp\n")
    return all_restaurants


async def display_restaurant_sample(restaurants: list):
    """Display a sample of fetched restaurants."""
    print("📋 Sample of fetched restaurants:")
    print("-" * 80)

    for i, r in enumerate(restaurants[:10], 1):
        name = r.get("name", "N/A")
        rating = r.get("rating", "N/A")
        review_count = r.get("review_count", 0)
        price = r.get("price", "N/A")
        category = r.get("categories", [{}])[0].get("title", "N/A") if r.get("categories") else "N/A"
        restaurant_id = r.get("id", "N/A")

        print(f"{i:2d}. {name[:40]:40s} | ⭐ {rating} ({review_count} reviews) | {price:4s} | {category[:20]:20s}")
        print(f"    ID: {restaurant_id}")

    if len(restaurants) > 10:
        print(f"\n... and {len(restaurants) - 10} more restaurants")

    print("-" * 80)
    print()


async def save_restaurant_ids_to_file(restaurants: list, filename: str = "sf_restaurant_ids.txt"):
    """Save restaurant IDs to a file for reference."""
    filepath = f"/Users/atharvadeshmukh/TasteSync/backend/{filename}"

    with open(filepath, "w") as f:
        f.write("# San Francisco Restaurant IDs from Yelp\n")
        f.write(f"# Total: {len(restaurants)} restaurants\n")
        f.write("# Format: YELP_ID | Name | Rating | Price | Category\n\n")

        for r in restaurants:
            restaurant_id = r.get("id", "N/A")
            name = r.get("name", "N/A")
            rating = r.get("rating", "N/A")
            price = r.get("price", "N/A")
            category = r.get("categories", [{}])[0].get("title", "N/A") if r.get("categories") else "N/A"

            f.write(f"{restaurant_id} | {name} | {rating} | {price} | {category}\n")

    print(f"💾 Saved restaurant IDs to: {filepath}\n")


async def main():
    """Main function to orchestrate the population process."""
    print("=" * 80)
    print("🍽️  TasteSync - San Francisco Restaurant Data Population")
    print("=" * 80)
    print()

    try:
        # Step 1: Fetch restaurants from Yelp
        restaurants = await fetch_sf_restaurants(limit=100)

        if not restaurants:
            print("❌ No restaurants fetched. Exiting.")
            return

        # Step 2: Display sample
        await display_restaurant_sample(restaurants)

        # Step 3: Save IDs to file for reference
        await save_restaurant_ids_to_file(restaurants)

        # Step 4: Clean existing data
        async with async_session_maker() as db:
            await clean_restaurant_data(db)

        print("✅ Process completed successfully!")
        print()
        print("📊 Summary:")
        print(f"  • Fetched {len(restaurants)} restaurants from Yelp API")
        print(f"  • Cleaned all existing restaurant data from database")
        print(f"  • Saved restaurant IDs to sf_restaurant_ids.txt")
        print()
        print("ℹ️  Note: The app now fetches all restaurant data fresh from Yelp API")
        print("   No restaurant data is permanently stored - only IDs in saved_restaurants table")
        print()

    except Exception as e:
        print(f"❌ Error during population: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
