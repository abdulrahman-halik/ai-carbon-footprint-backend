"""
Shared pytest fixtures for the test suite.

MongoDB is replaced with an in-memory mongomock instance so no real database
is required.  The patching happens at module import time *before* app.main is
imported, which prevents the lifespan from connecting to a real MongoDB.
"""

import mongomock
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# ── 1. Patch the db module ────────────────────────────────────────────────────
# Must happen before app.main (and transitively all routes) is imported so
# every model that calls mongodb.db gets the in-memory instance.
import app.db.mongodb as _mongo_module  # noqa: E402

_fake_client = mongomock.MongoClient()
_fake_db = _fake_client["test_sustainability_db"]

_mongo_module.db = _fake_db

# ── 2. Pre-import app.main so patch() can resolve "app.main.*" ───────────────
# unittest.mock.patch resolves "app.main.X" by importing "app.main" and looking
# up attribute X.  If app.main is not yet in sys.modules the resolution fails
# with AttributeError.  Importing it here (after the db mock is in place) is
# safe because the lifespan body is never executed at import time.
import app.main as _app_main  # noqa: F401, E402

# ── Constants shared by auth-related tests ────────────────────────────────────
TEST_EMAIL    = "testuser@example.com"
TEST_PASSWORD = "SecurePass!99"
TEST_NAME     = "Test User"


# ── Core fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture()
def client():
    """
    Provide a TestClient that uses the mongomock database.

    connect_to_mongo / close_mongo_connection are patched as no-ops so the
    lifespan never overwrites the in-memory db set above.
    """
    with (
        patch("app.main.connect_to_mongo"),
        patch("app.main.close_mongo_connection"),
    ):
        with TestClient(_app_main.app, raise_server_exceptions=True) as tc:
            yield tc

    # ── Teardown: wipe all collections so each test is fully isolated ─────────
    for col_name in _fake_db.list_collection_names():
        _fake_db[col_name].drop()


# ── Auth helper ───────────────────────────────────────────────────────────────

def _register_and_login(tc: TestClient, email: str, password: str, name: str) -> dict:
    """Register *email* (ignore 400 if already exists) then log in.

    Returns ``{"access_token": <str>, "headers": {"Authorization": "Bearer <str>"}}``
    """
    tc.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": name},
    )
    res = tc.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    return {
        "access_token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture()
def auth(client: TestClient) -> dict:
    """Register + login with the default test user.  Returns the auth dict."""
    return _register_and_login(client, TEST_EMAIL, TEST_PASSWORD, TEST_NAME)
