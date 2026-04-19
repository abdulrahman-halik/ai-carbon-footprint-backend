import requests


BASE_URL = "http://127.0.0.1:8000/api"


def login_user(email: str, password: str):
    response = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    response.raise_for_status()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_phase7_endpoints():
    headers = login_user("test@example.com", "testpassword")

    post_response = requests.post(
        f"{BASE_URL}/community/post",
        json={
            "content": "Reached a 5 day eco streak and cut my transport emissions this week.",
            "post_type": "milestone",
            "milestone_label": "5 day streak",
        },
        headers=headers,
    )
    assert post_response.status_code in {200, 201}, post_response.text

    feed_response = requests.get(f"{BASE_URL}/community/feed", headers=headers)
    assert feed_response.status_code == 200, feed_response.text
    assert isinstance(feed_response.json(), list)

    csv_response = requests.get(f"{BASE_URL}/reports/download/monthly?format=csv", headers=headers)
    assert csv_response.status_code == 200, csv_response.text
    assert "text/csv" in csv_response.headers.get("content-type", "")

    pdf_response = requests.get(f"{BASE_URL}/reports/download/yearly?format=pdf", headers=headers)
    assert pdf_response.status_code == 200, pdf_response.text
    assert "application/pdf" in pdf_response.headers.get("content-type", "")