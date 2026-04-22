import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_new_features():
    print("--- 1. Login to get token ---")
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        print("Please ensure testuser@example.com exists (run verify_auth.py first)")
        return
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    print("\n--- 2. Testing Profile Update ---")
    profile_data = {
        "full_name": "Test User Updated",
        "profile": {
            "location": "New York",
            "bio": "Sustainability enthusiast"
        }
    }
    response = requests.put(f"{BASE_URL}/users/profile", json=profile_data, headers=headers)
    if response.status_code == 200:
        print("Profile update successful!")
        print(f"Updated Data: {response.json().get('full_name')} - {response.json().get('profile')}")
    else:
        print(f"Profile update failed: {response.status_code} - {response.text}")

    print("\n--- 3. Testing 2FA Toggle ---")
    twofa_data = {"enabled": True}
    response = requests.put(f"{BASE_URL}/auth/2fa", json=twofa_data, headers=headers)
    if response.status_code == 200:
        print(f"2FA toggle successful: {response.json().get('message')}")
    else:
        print(f"2FA toggle failed: {response.status_code} - {response.text}")

    print("\n--- 4. Testing Password Change ---")
    pw_data = {
        "current_password": "testpassword",
        "new_password": "newtestpassword"
    }
    response = requests.put(f"{BASE_URL}/auth/change-password", json=pw_data, headers=headers)
    if response.status_code == 200:
        print("Password change successful!")
    else:
        print(f"Password change failed: {response.status_code} - {response.text}")

    print("\n--- 5. Verify Login with New Password ---")
    login_data["password"] = "newtestpassword"
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        print("Login with new password successful!")
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print(f"Login with new password failed: {response.status_code} - {response.text}")

    print("\n--- 6. Testing Account Deletion ---")
    response = requests.delete(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        print(f"Account deletion successful: {response.json().get('message')}")
    else:
        print(f"Account deletion failed: {response.status_code} - {response.text}")

    print("\n--- 7. Verify Account is Deleted ---")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 401:
        print("Correctly denied access to deleted account.")
    else:
        print(f"Unexpected response code for deleted account: {response.status_code}")

if __name__ == "__main__":
    test_new_features()
