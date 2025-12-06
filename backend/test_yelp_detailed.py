"""Detailed test script for Yelp AI API to debug responses."""

import asyncio
import httpx
import json
from app.config import get_settings

async def test_yelp_ai_detailed():
    """Test Yelp AI API with detailed logging."""
    settings = get_settings()
    api_key = settings.yelp_api_key
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    print("=" * 80)
    print("YELP AI API DETAILED TEST")
    print("=" * 80)
    
    # Test 1: Very simple query
    print("\nTest 1: Simple query without location")
    payload1 = {
        "query": "Italian restaurants"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.yelp.com/ai/chat/v2",
                headers=headers,
                json=payload1,
                timeout=30.0,
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 80)
    
    # Test 2: Query with San Francisco location
    print("\nTest 2: Query with San Francisco location")
    payload2 = {
        "query": "Find me Italian restaurants",
        "user_context": {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.yelp.com/ai/chat/v2",
                headers=headers,
                json=payload2,
                timeout=30.0,
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 80)
    
    # Test 3: More conversational query
    print("\nTest 3: Conversational query with location")
    payload3 = {
        "query": "I'm looking for a romantic Italian restaurant for a date night in San Francisco",
        "user_context": {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.yelp.com/ai/chat/v2",
                headers=headers,
                json=payload3,
                timeout=30.0,
            )
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response Body:\n{json.dumps(data, indent=2)}")
            
            # Analyze response structure
            print("\n" + "-" * 80)
            print("RESPONSE ANALYSIS:")
            print(f"  - Has 'text' field: {bool(data.get('text'))}")
            print(f"  - Has 'chat_id' field: {bool(data.get('chat_id'))}")
            print(f"  - Has 'businesses' field: {bool(data.get('businesses'))}")
            print(f"  - Number of businesses: {len(data.get('businesses', []))}")
            if data.get('businesses'):
                print(f"  - First business keys: {list(data['businesses'][0].keys())}")
            print(f"  - All response keys: {list(data.keys())}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_yelp_ai_detailed())
