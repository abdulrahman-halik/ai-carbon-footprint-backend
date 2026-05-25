import pytest

@pytest.mark.asyncio
async def test_create_emission(client, auth_headers):
    response = await client.post(
        "/api/emissions/",
        json={
            "category": "transport",
            "value": 15.5,
            "unit": "km",
            "date": "2026-05-23"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["category"] == "transport"

@pytest.mark.asyncio
async def test_list_emissions(client, auth_headers):
    # First create an emission
    await client.post(
        "/api/emissions/",
        json={"category": "transport", "value": 15.5, "unit": "km", "date": "2026-05-23T00:00:00"},
        headers=auth_headers
    )

    response = await client.get("/api/emissions/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_emission(client, auth_headers):
    create_response = await client.post(
        "/api/emissions/",
        json={"category": "transport", "value": 15.5, "unit": "km", "date": "2026-05-23T00:00:00"},
        headers=auth_headers
    )
    record_id = create_response.json()["_id"]

    response = await client.get(f"/api/emissions/{record_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["_id"] == record_id

@pytest.mark.asyncio
async def test_emission_stats(client, auth_headers):
    # Retrieve stats
    response = await client.get("/api/emissions/stats", headers=auth_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_emission(client, auth_headers):
    create_response = await client.post(
        "/api/emissions/",
        json={"category": "transport", "value": 15.5, "unit": "km"},
        headers=auth_headers
    )
    record_id = create_response.json()["_id"]

    update_response = await client.put(
        f"/api/emissions/{record_id}",
        json={"value": 20.0},
        headers=auth_headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["value"] == 20.0

@pytest.mark.asyncio
async def test_delete_emission(client, auth_headers):
    create_response = await client.post(
        "/api/emissions/",
        json={"category": "transport", "value": 15.5, "unit": "km"},
        headers=auth_headers
    )
    record_id = create_response.json()["_id"]

    delete_response = await client.delete(
        f"/api/emissions/{record_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 200

    # Ensure it's deleted
    get_response = await client.get("/api/emissions/", headers=auth_headers)
    emissions = get_response.json()
    assert all(em["_id"] != record_id for em in emissions)


@pytest.mark.asyncio
async def test_emission_ownership(client, auth_headers):
    # 1. User A creates an emission
    create_response = await client.post(
        "/api/emissions/",
        json={"category": "transport", "value": 10.0, "unit": "km"},
        headers=auth_headers
    )
    record_id = create_response.json()["_id"]

    # 2. User B tries to access User A's emission
    # Assuming we can get another user's headers. 
    # For simplicity, let's use a dummy token or register a new user if possible.
    # But usually, the 'client' fixture can be used with different headers.
    
    # Registering User B
    user_b_payload = {
        "full_name": "User B",
        "email": "userb@example.com",
        "password": "password123"
    }
    await client.post("/api/auth/register", json=user_b_payload)
    login_response = await client.post("/api/auth/login", json={"email": "userb@example.com", "password": "password123"})
    token_b = login_response.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B tries to GET User A's record
    get_resp = await client.get(f"/api/emissions/{record_id}", headers=headers_b)
    assert get_resp.status_code == 404

    # User B tries to UPDATE User A's record
    put_resp = await client.put(f"/api/emissions/{record_id}", json={"value": 100.0}, headers=headers_b)
    assert put_resp.status_code == 404

    # User B tries to DELETE User A's record
    del_resp = await client.delete(f"/api/emissions/{record_id}", headers=headers_b)
    assert del_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_non_existent_emission(client, auth_headers):
    fake_id = "60a2c8e0b6b2c2b3e4f5a6b7" # Valid ObjectId string but non-existent
    response = await client.get(f"/api/emissions/{fake_id}", headers=auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_invalid_object_id(client, auth_headers):
    invalid_id = "invalid-id"
    response = await client.get(f"/api/emissions/{invalid_id}", headers=auth_headers)
    assert response.status_code == 404
