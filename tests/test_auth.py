import pytest

@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "Password123!"
        }
    )
    assert response.status_code == 201
    assert "email" in response.json()
    assert response.json()["email"] == "newuser@example.com"

@pytest.mark.asyncio
async def test_login_user(client, test_user):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_invalid_login(client):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_change_password(client, auth_headers):
    response = await client.put(
        "/api/auth/change-password",
        json={
            "current_password": "password123",
            "new_password": "newpassword123!"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
