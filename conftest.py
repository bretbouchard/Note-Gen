import pytest
import pytest_asyncio
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from main import app
from src.note_gen.database.db import init_db, close_mongo_connection, get_db_conn

@pytest_asyncio.fixture
async def test_db():
    """Fixture to provide a test database."""
    await init_db()
    db = await get_db_conn()
    
    # Clear all collections before each test
    # collections = await db.list_collection_names()
    # for collection in collections:
    #     await db[collection].delete_many({})
    
    yield db
    
    # Clean up after test
    await close_mongo_connection()

@pytest_asyncio.fixture
async def async_test_client():
    """Async test client fixture."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        yield client

@pytest.fixture
def test_client():
    """Sync test client fixture."""
    with TestClient(app=app) as client:
        yield client