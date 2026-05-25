import pytest

@pytest.mark.asyncio
async def test_onboarding_start(client, auth_headers):
    response = await client.post(
        "/api/onboarding/start",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "onboarding_completed" in data
    # Current implementation of start_onboarding might set a flag or just return user
    # Based on the route: user = await start_onboarding(str(current_user["_id"]))

@pytest.mark.asyncio
async def test_onboarding_complete(client, auth_headers):
    response = await client.put(
        "/api/onboarding/complete",
        json={
            "profile": {
                "industry": "Technology",
                "company_size": "Medium",
                "location": "San Francisco"
            }
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["onboarding_completed"] is True
    assert data["profile"]["industry"] == "Technology"

@pytest.mark.asyncio
async def test_onboarding_start_unauthorized(client):
    response = await client.post("/api/onboarding/start")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_onboarding_complete_unauthorized(client):
    response = await client.put(
        "/api/onboarding/complete",
        json={"profile": {}}
    )
    assert response.status_code == 401
