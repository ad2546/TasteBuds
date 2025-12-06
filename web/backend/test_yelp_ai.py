"""Test script for Yelp AI API integration."""

import asyncio
from app.services.yelp_ai_service import yelp_ai_service


async def test_yelp_ai():
    """Test the Yelp AI API."""
    print("Testing Yelp AI API...")
    print("=" * 60)

    try:
        # Test 1: Simple search
        print("\n1. Testing simple restaurant search:")
        result = await yelp_ai_service.chat(
            query="Find me a good Italian restaurant in San Francisco",
            latitude=37.7749,
            longitude=-122.4194,
        )
        print(f"Response: {result.get('text', 'No text')[:200]}...")
        print(f"Chat ID: {result.get('chat_id')}")
        print(f"Businesses found: {len(result.get('businesses', []))}")

        # Test 2: With TasteDNA context
        print("\n2. Testing search with TasteDNA:")
        taste_dna = {
            "preferred_cuisines": ["Italian", "Japanese"],
            "price_sensitivity": 0.3,  # Upscale
            "ambiance_preference": "Fine Dining",
            "adventure_score": 0.6,
        }
        result2 = await yelp_ai_service.search_with_context(
            query="Recommend a restaurant for date night",
            taste_dna=taste_dna,
            latitude=37.7749,
            longitude=-122.4194,
        )
        print(f"Response: {result2.get('text', 'No text')[:200]}...")
        print(f"Businesses found: {len(result2.get('businesses', []))}")

        print("\n✅ Yelp AI API is working!")

    except Exception as e:
        print(f"\n❌ Error testing Yelp AI API: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_yelp_ai())
