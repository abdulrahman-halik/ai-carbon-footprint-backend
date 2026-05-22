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
