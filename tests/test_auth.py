"""
Integration tests for Auth routes.

Coverage:
  POST /api/auth/register        – success, duplicate email, validation error
  POST /api/auth/login           – success (access token + refresh cookie),
                                   wrong password, unknown email
  POST /api/auth/refresh         – with valid cookie, without cookie
  POST /api/auth/logout          – clears cookie
  POST /api/auth/forgot-password – stub endpoint
"""

import pytest
from fastapi.testclient import TestClient

# ── Fixtures come from tests/conftest.py automatically ───────────────────────

_EMAIL    = "auth_test@example.com"
_PASSWORD = "GoodPass!77"
_NAME     = "Auth Tester"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _register(tc: TestClient, email: str = _EMAIL, password: str = _PASSWORD, name: str = _NAME):
    return tc.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": name},
    )


def _login(tc: TestClient, email: str = _EMAIL, password: str = _PASSWORD):
    return tc.post("/api/auth/login", data={"username": email, "password": password})


# ── /register ─────────────────────────────────────────────────────────────────

class TestRegister:
    def test_register_success(self, client: TestClient):
        res = _register(client)
        assert res.status_code == 201
        body = res.json()
        # UserOut must not expose the password hash
        assert "password" not in body
        assert body["email"] == _EMAIL

    def test_register_duplicate_email(self, client: TestClient):
        _register(client)  # first registration
        res = _register(client)  # second – same email
        assert res.status_code == 400
        assert "already exists" in res.json()["detail"].lower()

    def test_register_missing_email(self, client: TestClient):
        res = client.post(
            "/api/auth/register",
            json={"password": _PASSWORD},
        )
        assert res.status_code == 422  # Pydantic validation error

    def test_register_missing_password(self, client: TestClient):
        res = client.post(
            "/api/auth/register",
            json={"email": _EMAIL},
        )
        assert res.status_code == 422

    def test_register_invalid_email_format(self, client: TestClient):
        res = client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": _PASSWORD},
        )
        assert res.status_code == 422


# ── /login ────────────────────────────────────────────────────────────────────

class TestLogin:
    def test_login_success_returns_access_token(self, client: TestClient):
        _register(client)
        res = _login(client)
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_sets_refresh_cookie(self, client: TestClient):
        _register(client)
        res = _login(client)
        assert res.status_code == 200
        # The refresh_token cookie must be present and must not be empty
        assert "refresh_token" in res.cookies
        assert len(res.cookies["refresh_token"]) > 0

    def test_login_wrong_password(self, client: TestClient):
        _register(client)
        res = client.post(
            "/api/auth/login",
            data={"username": _EMAIL, "password": "WrongPass!"},
        )
        assert res.status_code == 401

    def test_login_unknown_email(self, client: TestClient):
        res = client.post(
            "/api/auth/login",
            data={"username": "nobody@nowhere.com", "password": _PASSWORD},
        )
        assert res.status_code == 401

    def test_login_missing_credentials(self, client: TestClient):
        res = client.post("/api/auth/login", data={})
        assert res.status_code == 422


# ── /refresh ──────────────────────────────────────────────────────────────────

class TestRefresh:
    def test_refresh_with_valid_cookie(self, client: TestClient):
        _register(client)
        _login(client)  # client now holds the refresh_token cookie
        res = client.post("/api/auth/refresh")
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_refresh_rotates_cookie(self, client: TestClient):
        _register(client)
        login_res = _login(client)
        original_cookie = login_res.cookies.get("refresh_token")

        refresh_res = client.post("/api/auth/refresh")
        assert refresh_res.status_code == 200
        # The new cookie should differ from the original
        new_cookie = refresh_res.cookies.get("refresh_token")
        assert new_cookie is not None
        assert new_cookie != original_cookie

    def test_refresh_without_cookie(self, client: TestClient):
        # No prior login → no cookie in jar
        res = client.post("/api/auth/refresh")
        assert res.status_code == 401


# ── /logout ───────────────────────────────────────────────────────────────────

class TestLogout:
    def test_logout_returns_204(self, client: TestClient):
        _register(client)
        _login(client)
        res = client.post("/api/auth/logout")
        assert res.status_code == 204

    def test_logout_clears_refresh_cookie(self, client: TestClient):
        _register(client)
        _login(client)
        res = client.post("/api/auth/logout")
        # After logout the cookie should be deleted (empty value or absent)
        cookie_value = res.cookies.get("refresh_token", "")
        assert cookie_value == ""


# ── /forgot-password ──────────────────────────────────────────────────────────

class TestForgotPassword:
    def test_forgot_password_returns_message(self, client: TestClient):
        res = client.post("/api/auth/forgot-password")
        assert res.status_code == 200
        assert "message" in res.json()
