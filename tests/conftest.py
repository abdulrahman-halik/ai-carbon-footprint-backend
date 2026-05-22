import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

import app.db.mongodb as mongo_db
from app.main import app
from app.services.auth_service import create_user_token
from app.core.security import get_password_hash

@pytest.fixture(autouse=True)
def mock_mongo():
    test_client = AsyncMongoMockClient()
    mongo_db.client = test_client
    mongo_db.db = test_client["test_sustainability"]
    yield

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest_asyncio.fixture
async def test_user(mock_mongo):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": get_password_hash("password123")
    }
    result = await mongo_db.db["users"].insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data

@pytest_asyncio.fixture
async def user_token(test_user):
    token = await create_user_token(str(test_user["_id"]))
    return token.access_token

@pytest_asyncio.fixture
async def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}
