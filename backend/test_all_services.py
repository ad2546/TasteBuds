#!/usr/bin/env python3
"""
TasteSync Complete Service Test
Tests all backend services with real API calls
"""

import requests
import json
from colorama import init, Fore, Style
import time

init(autoreset=True)

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Test data
TEST_EMAIL = "alex.chen@example.com"
TEST_PASSWORD = "password123"
TEST_LOCATION = "San Francisco, CA"

# Store token globally
AUTH_TOKEN = None

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text.center(70)}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def print_test(name):
    print(f"{Fore.YELLOW}[TEST] {name}{Style.RESET_ALL}")

def print_success(msg):
    print(f"  {Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"  {Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_info(msg):
    print(f"  {Fore.BLUE}ℹ {msg}{Style.RESET_ALL}")

def print_warning(msg):
    print(f"  {Fore.MAGENTA}⚠ {msg}{Style.RESET_ALL}")


# Test Results
results = {"total": 0, "passed": 0, "failed": 0}

def test(func):
    def wrapper():
        results["total"] += 1
        try:
            success = func()
            if success:
                results["passed"] += 1
            else:
                results["failed"] += 1
            return success
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            results["failed"] += 1
            return False
    return wrapper


@test
def test_health_check():
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Server healthy: {response.json()}")
            return True
        else:
            print_error(f"Failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_login():
    global AUTH_TOKEN
    print_test("User Login")
    try:
        response = requests.post(
            f"{API_V1}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data["access_token"]
            print_success(f"Logged in as: {data['user']['name']}")
            print_info(f"Token: {AUTH_TOKEN[:40]}...")
            return True
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_get_current_user():
    print_test("Get Current User")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_V1}/auth/me", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"User: {data['name']} ({data['email']})")
            print_info(f"Quiz completed: {data['quiz_completed']}")
            return True
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_get_taste_dna():
    print_test("Get TasteDNA Profile")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_V1}/taste-dna/profile", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("TasteDNA retrieved")
            print_info(f"Adventure: {data['adventure_score']}, Spice: {data['spice_tolerance']}")
            print_info(f"Cuisines: {', '.join(data['preferred_cuisines'][:3])}...")
            return True
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_get_taste_twins():
    print_test("Get Taste Twins")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_V1}/twins", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            twins = data.get("twins", [])
            print_success(f"Found {data.get('total_count', len(twins))} Taste Twins")
            for twin in twins[:3]:
                print_info(f"  - {twin['name']}: {twin['similarity_score']:.2f} similarity")
            return True
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_discovery_lucky():
    print_test("Discovery: Feeling Lucky")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        params = {"location": TEST_LOCATION}
        response = requests.get(f"{API_V1}/discovery/lucky", headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Restaurant: {data.get('name', 'N/A')}")
            print_info(f"Match Score: {data.get('match_score', 0):.2f}")
            print_info(f"Reason: {data.get('explanation', 'N/A')[:60]}...")
            return True
        else:
            print_warning(f"Failed: {response.status_code} (May need Yelp API)")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_restaurant_search():
    print_test("Restaurant Search")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        params = {"location": TEST_LOCATION, "term": "sushi", "limit": 3}
        response = requests.get(f"{API_V1}/restaurants/search", headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            businesses = data.get("businesses", [])
            print_success(f"Found {len(businesses)} restaurants")
            for biz in businesses[:2]:
                print_info(f"  - {biz.get('name', 'N/A')}: ⭐ {biz.get('rating', 'N/A')}")
            return True
        else:
            print_warning(f"Failed: {response.status_code} (May need Yelp API)")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_get_saved_restaurants():
    print_test("Get Saved Restaurants")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_V1}/restaurants/saved/list", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} saved restaurants")
            for saved in data[:3]:
                print_info(f"  - {saved['restaurant_name']}")
            return True
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_get_challenges():
    print_test("Get Gamification Challenges")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_V1}/gamification/challenges", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            challenges = data.get("challenges", [])
            print_success(f"Retrieved {len(challenges)} challenges")
            for challenge in challenges[:2]:
                progress = challenge.get('user_progress', 0)
                target = challenge.get('target_count', 0)
                print_info(f"  - {challenge['title']}: {progress}/{target}")
            return True
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_get_leaderboard():
    print_test("Get Leaderboard")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_V1}/gamification/leaderboard", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            leaderboard = data.get("leaderboard", [])
            print_success(f"Retrieved leaderboard with {len(leaderboard)} entries")
            for entry in leaderboard[:3]:
                print_info(f"  #{entry['rank']} {entry['name']}: {entry['score']} pts")
            return True
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


@test
def test_image_search_history():
    print_test("Image Search History")
    if not AUTH_TOKEN:
        print_warning("Skipped: No auth token")
        return False

    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_V1}/image-search/history", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} image searches")
            for search in data[:2]:
                print_info(f"  - {search['detected_dish']} ({search['detected_cuisine']})")
            return True
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def print_summary():
    print_header("TEST RESULTS SUMMARY")
    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"{Fore.CYAN}Total Tests: {total}")
    print(f"{Fore.GREEN}Passed: {passed}")
    print(f"{Fore.RED}Failed: {failed}")
    print(f"{Fore.YELLOW}Pass Rate: {pass_rate:.1f}%{Style.RESET_ALL}\n")

    if failed == 0:
        print(f"{Fore.GREEN}ALL TESTS PASSED! 🎉{Style.RESET_ALL}")
    elif pass_rate >= 70:
        print(f"{Fore.YELLOW}MOST TESTS PASSED ⚠️{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}MANY TESTS FAILED ❌{Style.RESET_ALL}")


def main():
    print_header("TasteSync Complete Service Test")
    print(f"{Fore.BLUE}Testing all backend services...")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}{Style.RESET_ALL}\n")

    # Run all tests
    print_header("CONNECTIVITY & AUTHENTICATION")
    test_health_check()
    test_login()
    test_get_current_user()

    print_header("TASTE DNA & TWINS")
    test_get_taste_dna()
    test_get_taste_twins()

    print_header("DISCOVERY & RESTAURANTS")
    test_discovery_lucky()
    test_restaurant_search()
    test_get_saved_restaurants()

    print_header("GAMIFICATION")
    test_get_challenges()
    test_get_leaderboard()

    print_header("ADDITIONAL FEATURES")
    test_image_search_history()

    # Print summary
    print_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
