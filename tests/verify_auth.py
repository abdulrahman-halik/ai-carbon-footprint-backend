import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_auth():
    print("--- Testing Registration ---")
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            print("Registration successful!")
        elif response.status_code == 400:
            print(f"Registration failed (likely already exists): {response.json()}")
        else:
            print(f"Registration failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error during registration: {e}")

    print("\n--- Testing Login ---")
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword"
    }
    token = None
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("Login successful! Token received.")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"Error during login: {e}")
        return

    if token:
        print("\n--- Testing Protected Route (/users/me) ---")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{BASE_URL}/users/me", headers=headers)
            if response.status_code == 200:
                print(f"Successfully retrieved current user: {response.json()}")
            else:
                print(f"Failed to retrieve user: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during protected route test: {e}")

    print("\n--- Testing Protected Route without Token ---")
    try:
        response = requests.get(f"{BASE_URL}/users/me")
        if response.status_code == 401:
            print("Correctly denied access without token.")
        else:
            print(f"Unexpected response code without token: {response.status_code}")
    except Exception as e:
        print(f"Error during unauthorized access test: {e}")

if __name__ == "__main__":
    test_auth()
