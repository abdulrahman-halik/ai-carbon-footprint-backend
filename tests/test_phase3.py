import requests
import sys
import time

BASE_URL = "http://localhost:8000/api"

def test_phase3():
    # 1. Register and Login (to get token)
    print("--- Preparation: Auth ---")
    user_email = f"phase3test_{int(time.time())}@example.com"
    user_data = {
        "email": user_email,
        "password": "testpassword",
        "full_name": "Phase 3 Tester"
    }
    requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    login_data = {"username": user_email, "password": "testpassword"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login Failed: {response.status_code} - {response.text}")
        return
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Auth successful for {user_email}\n")

    # 2. Test Onboarding Start
    print("--- Testing Onboarding Start ---")
    response = requests.post(f"{BASE_URL}/onboarding/start", headers=headers)
    if response.status_code == 200:
        print(f"Onboarding Start: {response.json()}")
    else:
        print(f"Onboarding Start Failed: {response.status_code} - {response.text}")

    # 3. Test Onboarding Complete
    print("\n--- Testing Onboarding Complete ---")
    onboarding_data = {
        "profile": {
            "food": "Vegan",
            "shopping": "Minimalist",
            "home": "Solar powered",
            "water": "Low usage"
        }
    }
    response = requests.put(f"{BASE_URL}/onboarding/complete", json=onboarding_data, headers=headers)
    if response.status_code == 200:
        print(f"Onboarding Complete: {response.json()}")
    else:
        print(f"Onboarding Complete Failed: {response.status_code} - {response.text}")

    # 4. Test Goal Set
    print("\n--- Testing Goal Set ---")
    goal_data = {
        "target_value": 500.0,
        "category": "Overall",
        "target_date": "2026-12-31T23:59:59"
    }
    response = requests.post(f"{BASE_URL}/goals/set", json=goal_data, headers=headers)
    if response.status_code == 200:
        print(f"Goal Set: {response.json()}")
    else:
        print(f"Goal Set Failed: {response.status_code} - {response.text}")

    # 5. Test Goal Progress
    print("\n--- Testing Goal Progress ---")
    response = requests.get(f"{BASE_URL}/goals/progress", headers=headers)
    if response.status_code == 200:
        print(f"Goal Progress: {response.json()}")
    else:
        print(f"Goal Progress Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_phase3()
