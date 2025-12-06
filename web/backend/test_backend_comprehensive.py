"""
TasteSync Comprehensive Backend Testing Script
Tests all API endpoints and services with generated dummy data
"""

import asyncio
import httpx
import json
from typing import Dict, List, Optional
from datetime import datetime
import sys
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Test credentials (from dummy data)
TEST_USERS = [
    {"email": "alex.chen@example.com", "password": "password123", "name": "Alex Chen"},
    {"email": "sarah.m@example.com", "password": "password123", "name": "Sarah Martinez"},
    {"email": "james.w@example.com", "password": "password123", "name": "James Wilson"},
]

# Global test results
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": []
}

# Global auth tokens
auth_tokens: Dict[str, str] = {}


def print_header(text: str):
    """Print colored section header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text.center(70)}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def print_test(test_name: str):
    """Print test name"""
    print(f"{Fore.YELLOW}Testing: {test_name}{Style.RESET_ALL}")


def print_success(message: str):
    """Print success message"""
    print(f"  {Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message"""
    print(f"  {Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message"""
    print(f"  {Fore.MAGENTA}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message"""
    print(f"  {Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def record_test(passed: bool, error_msg: Optional[str] = None):
    """Record test result"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        if error_msg:
            test_results["errors"].append(error_msg)


async def test_health_check(client: httpx.AsyncClient) -> bool:
    """Test basic health check endpoint"""
    print_test("Health Check")
    try:
        response = await client.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is healthy: {data}")
            record_test(True)
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            record_test(False, f"Health check returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        record_test(False, f"Health check exception: {str(e)}")
        return False


async def test_auth_registration(client: httpx.AsyncClient) -> bool:
    """Test user registration"""
    print_test("User Registration (New User)")
    try:
        new_user = {
            "email": f"test_user_{datetime.now().timestamp()}@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
        response = await client.post(f"{API_V1}/auth/register", json=new_user)

        if response.status_code == 201:
            data = response.json()
            print_success(f"User registered: {data['user']['name']}")
            print_info(f"User ID: {data['user']['id']}")
            record_test(True)
            return True
        else:
            print_error(f"Registration failed: {response.status_code} - {response.text}")
            record_test(False, f"Registration failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        record_test(False, f"Registration exception: {str(e)}")
        return False


async def test_auth_login(client: httpx.AsyncClient) -> bool:
    """Test user login for all test users"""
    print_test("User Login (Multiple Users)")
    all_success = True

    for user in TEST_USERS:
        try:
            response = await client.post(
                f"{API_V1}/auth/login",
                json={"email": user["email"], "password": user["password"]}
            )

            if response.status_code == 200:
                data = response.json()
                auth_tokens[user["email"]] = data["access_token"]
                print_success(f"Logged in: {user['name']}")
                print_info(f"Token: {data['access_token'][:30]}...")
            else:
                print_error(f"Login failed for {user['name']}: {response.status_code}")
                all_success = False
        except Exception as e:
            print_error(f"Login error for {user['name']}: {str(e)}")
            all_success = False

    record_test(all_success)
    return all_success


async def test_auth_me(client: httpx.AsyncClient) -> bool:
    """Test getting current user info"""
    print_test("Get Current User Info")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/auth/me", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved user: {data['name']} ({data['email']})")
            print_info(f"Quiz completed: {data['quiz_completed']}")
            record_test(True)
            return True
        else:
            print_error(f"Get user failed: {response.status_code}")
            record_test(False, f"Get user failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get user error: {str(e)}")
        record_test(False, f"Get user exception: {str(e)}")
        return False


async def test_taste_dna_quiz(client: httpx.AsyncClient) -> bool:
    """Test getting quiz questions"""
    print_test("Get TasteDNA Quiz Questions")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/taste-dna/quiz", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} quiz questions")
            print_info(f"Question types: {set(q['type'] for q in data)}")
            record_test(True)
            return True
        else:
            print_error(f"Get quiz failed: {response.status_code}")
            record_test(False, f"Get quiz failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get quiz error: {str(e)}")
        record_test(False, f"Get quiz exception: {str(e)}")
        return False


async def test_taste_dna_profile(client: httpx.AsyncClient) -> bool:
    """Test getting user's TasteDNA profile"""
    print_test("Get TasteDNA Profile")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/taste-dna/profile", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved TasteDNA profile")
            print_info(f"Adventure Score: {data.get('adventure_score', 'N/A')}")
            print_info(f"Spice Tolerance: {data.get('spice_tolerance', 'N/A')}")
            print_info(f"Preferred Cuisines: {', '.join(data.get('preferred_cuisines', []))}")
            record_test(True)
            return True
        else:
            print_error(f"Get TasteDNA failed: {response.status_code}")
            record_test(False, f"Get TasteDNA failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get TasteDNA error: {str(e)}")
        record_test(False, f"Get TasteDNA exception: {str(e)}")
        return False


async def test_taste_twins(client: httpx.AsyncClient) -> bool:
    """Test getting user's Taste Twins"""
    print_test("Get Taste Twins")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/twins", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} Taste Twins")
            for twin in data[:3]:  # Show first 3
                print_info(f"  Twin: {twin.get('twin_name', 'N/A')} - Similarity: {twin.get('similarity_score', 0):.2f}")
            record_test(True)
            return True
        else:
            print_error(f"Get twins failed: {response.status_code}")
            record_test(False, f"Get twins failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get twins error: {str(e)}")
        record_test(False, f"Get twins exception: {str(e)}")
        return False


async def test_taste_twins_count(client: httpx.AsyncClient) -> bool:
    """Test getting twin count"""
    print_test("Get Taste Twins Count")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/twins/count", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Twin count: {data.get('count', 0)}")
            record_test(True)
            return True
        else:
            print_error(f"Get twin count failed: {response.status_code}")
            record_test(False, f"Get twin count failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get twin count error: {str(e)}")
        record_test(False, f"Get twin count exception: {str(e)}")
        return False


async def test_discovery_lucky(client: httpx.AsyncClient) -> bool:
    """Test 'Feeling Lucky' discovery"""
    print_test("Discovery: Feeling Lucky")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        params = {"location": "San Francisco, CA"}
        response = await client.get(f"{API_V1}/discovery/lucky", headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Found restaurant: {data.get('name', 'N/A')}")
            print_info(f"Match Score: {data.get('match_score', 0):.2f}")
            print_info(f"Explanation: {data.get('explanation', 'N/A')[:80]}...")
            record_test(True)
            return True
        else:
            print_warning(f"Feeling Lucky returned: {response.status_code}")
            print_info("This may be expected if Yelp API is not configured")
            record_test(False, f"Feeling Lucky failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Feeling Lucky error: {str(e)}")
        record_test(False, f"Feeling Lucky exception: {str(e)}")
        return False


async def test_discovery_compare(client: httpx.AsyncClient) -> bool:
    """Test compare discovery"""
    print_test("Discovery: Compare Options")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        params = {"location": "San Francisco, CA"}
        response = await client.get(f"{API_V1}/discovery/compare", headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            options = data.get("options", [])
            print_success(f"Found {len(options)} comparison options")
            for i, opt in enumerate(options, 1):
                print_info(f"  Option {i}: {opt.get('name', 'N/A')} - Score: {opt.get('match_score', 0):.2f}")
            record_test(True)
            return True
        else:
            print_warning(f"Compare returned: {response.status_code}")
            record_test(False, f"Compare failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Compare error: {str(e)}")
        record_test(False, f"Compare exception: {str(e)}")
        return False


async def test_discovery_trending(client: httpx.AsyncClient) -> bool:
    """Test trending discovery"""
    print_test("Discovery: Trending Among Twins")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        params = {"location": "San Francisco, CA"}
        response = await client.get(f"{API_V1}/discovery/trending", headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            items = data.get("trending", [])
            print_success(f"Found {len(items)} trending restaurants")
            for item in items[:3]:
                print_info(f"  {item.get('name', 'N/A')} - {item.get('twin_likes', 0)} twin likes")
            record_test(True)
            return True
        else:
            print_warning(f"Trending returned: {response.status_code}")
            record_test(False, f"Trending failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Trending error: {str(e)}")
        record_test(False, f"Trending exception: {str(e)}")
        return False


async def test_restaurant_search(client: httpx.AsyncClient) -> bool:
    """Test restaurant search"""
    print_test("Restaurant Search")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        params = {
            "location": "San Francisco, CA",
            "term": "sushi",
            "limit": 5
        }
        response = await client.get(f"{API_V1}/restaurants/search", headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            restaurants = data.get("businesses", [])
            print_success(f"Found {len(restaurants)} restaurants")
            for rest in restaurants[:3]:
                print_info(f"  {rest.get('name', 'N/A')} - Rating: {rest.get('rating', 'N/A')}")
            record_test(True)
            return True
        else:
            print_warning(f"Restaurant search returned: {response.status_code}")
            record_test(False, f"Restaurant search failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Restaurant search error: {str(e)}")
        record_test(False, f"Restaurant search exception: {str(e)}")
        return False


async def test_saved_restaurants(client: httpx.AsyncClient) -> bool:
    """Test getting saved restaurants"""
    print_test("Get Saved Restaurants")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/restaurants/saved/list", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} saved restaurants")
            for saved in data[:3]:
                print_info(f"  {saved.get('restaurant_name', 'N/A')}")
            record_test(True)
            return True
        else:
            print_error(f"Get saved restaurants failed: {response.status_code}")
            record_test(False, f"Get saved restaurants failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get saved restaurants error: {str(e)}")
        record_test(False, f"Get saved restaurants exception: {str(e)}")
        return False


async def test_challenges(client: httpx.AsyncClient) -> bool:
    """Test getting gamification challenges"""
    print_test("Get Gamification Challenges")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/gamification/challenges", headers=headers)

        if response.status_code == 200:
            data = response.json()
            challenges = data.get("challenges", [])
            print_success(f"Retrieved {len(challenges)} challenges")
            for challenge in challenges[:3]:
                print_info(f"  {challenge.get('title', 'N/A')} - Progress: {challenge.get('user_progress', 0)}/{challenge.get('target_count', 0)}")
            record_test(True)
            return True
        else:
            print_error(f"Get challenges failed: {response.status_code}")
            record_test(False, f"Get challenges failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get challenges error: {str(e)}")
        record_test(False, f"Get challenges exception: {str(e)}")
        return False


async def test_leaderboard(client: httpx.AsyncClient) -> bool:
    """Test getting leaderboard"""
    print_test("Get Leaderboard")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/gamification/leaderboard", headers=headers)

        if response.status_code == 200:
            data = response.json()
            leaderboard = data.get("leaderboard", [])
            print_success(f"Retrieved leaderboard with {len(leaderboard)} entries")
            for entry in leaderboard[:3]:
                print_info(f"  #{entry.get('rank', 'N/A')} {entry.get('name', 'N/A')} - {entry.get('score', 0)} points")
            record_test(True)
            return True
        else:
            print_error(f"Get leaderboard failed: {response.status_code}")
            record_test(False, f"Get leaderboard failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get leaderboard error: {str(e)}")
        record_test(False, f"Get leaderboard exception: {str(e)}")
        return False


async def test_date_night_compatibility(client: httpx.AsyncClient) -> bool:
    """Test date night compatibility"""
    print_test("Date Night Compatibility Check")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/date-night/compatibility", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Compatibility score: {data.get('compatibility_score', 0):.2f}")
            print_info(f"Partner: {data.get('partner_name', 'N/A')}")
            record_test(True)
            return True
        elif response.status_code == 404:
            print_warning("No active date night pairing found")
            record_test(True)  # This is expected
            return True
        else:
            print_error(f"Get compatibility failed: {response.status_code}")
            record_test(False, f"Get compatibility failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get compatibility error: {str(e)}")
        record_test(False, f"Get compatibility exception: {str(e)}")
        return False


async def test_image_search_history(client: httpx.AsyncClient) -> bool:
    """Test image search history"""
    print_test("Image Search History")
    email = TEST_USERS[0]["email"]

    if email not in auth_tokens:
        print_warning("Skipping: No auth token available")
        test_results["skipped"] += 1
        return False

    try:
        headers = {"Authorization": f"Bearer {auth_tokens[email]}"}
        response = await client.get(f"{API_V1}/image-search/history", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} image search records")
            for search in data[:3]:
                print_info(f"  Detected: {search.get('detected_dish', 'N/A')} ({search.get('detected_cuisine', 'N/A')})")
            record_test(True)
            return True
        else:
            print_error(f"Get image search history failed: {response.status_code}")
            record_test(False, f"Get image search history failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get image search history error: {str(e)}")
        record_test(False, f"Get image search history exception: {str(e)}")
        return False


def print_summary():
    """Print test results summary"""
    print_header("TEST RESULTS SUMMARY")

    total = test_results["total"]
    passed = test_results["passed"]
    failed = test_results["failed"]
    skipped = test_results["skipped"]

    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"{Fore.CYAN}Total Tests: {total + skipped}")
    print(f"{Fore.GREEN}Passed: {passed}")
    print(f"{Fore.RED}Failed: {failed}")
    print(f"{Fore.MAGENTA}Skipped: {skipped}")
    print(f"{Fore.YELLOW}Pass Rate: {pass_rate:.1f}%{Style.RESET_ALL}\n")

    if test_results["errors"]:
        print(f"{Fore.RED}Errors encountered:{Style.RESET_ALL}")
        for i, error in enumerate(test_results["errors"][:10], 1):  # Show first 10
            print(f"  {i}. {error}")
        if len(test_results["errors"]) > 10:
            print(f"  ... and {len(test_results['errors']) - 10} more errors")

    print()

    if failed == 0 and total > 0:
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}ALL TESTS PASSED! 🎉{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*70}\n")
    elif pass_rate >= 70:
        print(f"{Fore.YELLOW}{'='*70}")
        print(f"{Fore.YELLOW}TESTS MOSTLY PASSED ⚠️{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*70}\n")
    else:
        print(f"{Fore.RED}{'='*70}")
        print(f"{Fore.RED}MANY TESTS FAILED ❌{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*70}\n")


async def main():
    """Run all tests"""
    print_header("TasteSync Backend Comprehensive Test Suite")

    print(f"{Fore.BLUE}Base URL: {BASE_URL}")
    print(f"API Version: v1")
    print(f"Test Users: {len(TEST_USERS)}{Style.RESET_ALL}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Basic tests
        print_header("BASIC CONNECTIVITY TESTS")
        server_ok = await test_health_check(client)

        if not server_ok:
            print_error("\nServer is not responding. Please ensure:")
            print_error("1. Backend server is running (uvicorn app.main:app --reload)")
            print_error("2. Server is accessible at http://localhost:8000")
            print_error("3. .env file is properly configured")
            sys.exit(1)

        # Authentication tests
        print_header("AUTHENTICATION TESTS")
        await test_auth_registration(client)
        await test_auth_login(client)
        await test_auth_me(client)

        # TasteDNA tests
        print_header("TASTE DNA TESTS")
        await test_taste_dna_quiz(client)
        await test_taste_dna_profile(client)

        # Twin matching tests
        print_header("TASTE TWIN MATCHING TESTS")
        await test_taste_twins(client)
        await test_taste_twins_count(client)

        # Discovery tests
        print_header("DISCOVERY TESTS")
        await test_discovery_lucky(client)
        await test_discovery_compare(client)
        await test_discovery_trending(client)

        # Restaurant tests
        print_header("RESTAURANT TESTS")
        await test_restaurant_search(client)
        await test_saved_restaurants(client)

        # Gamification tests
        print_header("GAMIFICATION TESTS")
        await test_challenges(client)
        await test_leaderboard(client)

        # Date night tests
        print_header("DATE NIGHT TESTS")
        await test_date_night_compatibility(client)

        # Image search tests
        print_header("IMAGE SEARCH TESTS")
        await test_image_search_history(client)

    # Print summary
    print_summary()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
