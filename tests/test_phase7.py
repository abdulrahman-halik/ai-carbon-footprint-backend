import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_phase7():
    print("--- Phase 7 Verification: Community & Reports ---")
    
    # 1. Auth Setup
    user_email = f"community_test_{int(time.time())}@example.com"
    user_data = {
        "email": user_email,
        "password": "testpassword",
        "full_name": "Community Tester"
    }
    print(f"Registering user: {user_email}")
    requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    login_data = {"username": user_email, "password": "testpassword"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login Failed: {response.status_code} - {response.text}")
        return
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Auth successful!\n")

    # 2. Test Community Posting
    print("--- Testing Community Posting ---")
    post_data = {
        "content": "I just hit a 7-day reduction streak! 🌍✨",
        "post_type": "streak"
    }
    response = requests.post(f"{BASE_URL}/community/post", json=post_data, headers=headers)
    if response.status_code == 201:
        print(f"Post created successfully: {response.json().get('content')}")
    else:
        print(f"Post creation failed: {response.status_code} - {response.text}")

    # 3. Test Community Feed
    print("\n--- Testing Community Feed ---")
    response = requests.get(f"{BASE_URL}/community/feed")
    if response.status_code == 200:
        feed = response.json()
        print(f"Feed fetched successfully. Posts found: {len(feed)}")
        if len(feed) > 0:
            print(f"Latest post: {feed[0]['content']} by {feed[0]['user_name']}")
    else:
        print(f"Feed fetch failed: {response.status_code} - {response.text}")

    # 4. Test Report Generation (CSV)
    print("\n--- Testing Report Download (Monthly) ---")
    response = requests.get(f"{BASE_URL}/reports/download/monthly", headers=headers)
    if response.status_code == 200:
        print(f"Report downloaded successfully. Content type: {response.headers.get('Content-Type')}")
        print(f"Filename: {response.headers.get('Content-Disposition')}")
        # Preview first few lines of CSV
        csv_content = response.text
        lines = csv_content.splitlines()
        print(f"CSV Header: {lines[0] if lines else 'Empty'}")
        print(f"Total lines in CSV: {len(lines)}")
    else:
        print(f"Report download failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Small delay to ensure server is ready if started externally
    test_phase7()
