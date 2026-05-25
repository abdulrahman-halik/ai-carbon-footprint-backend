import pytest

@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "Password123!"
        }
    )
    assert response.status_code == 201
    assert "email" in response.json()
    assert response.json()["email"] == "newuser@example.com"

@pytest.mark.asyncio
async def test_login_user(client, test_user):
    # Test JSON login with 'email'
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_user_with_username_alias(client, test_user):
    # Test JSON login with 'username' alias
    response = await client.post(
        "/api/auth/login",
        json={
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
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_change_password(client, auth_headers):
    response = await client.post(
        "/api/auth/change-password",
        json={
            "current_password": "password123",
            "new_password": "newpassword123!"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully."

@pytest.mark.asyncio
async def test_change_password_same_password(client, auth_headers):
    # Should fail if new password is same as current
    response = await client.post(
        "/api/auth/change-password",
        json={
            "current_password": "password123",
            "new_password": "password123"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "New password must be different" in response.json()["detail"]
