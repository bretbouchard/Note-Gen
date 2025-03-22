import pytest
import pytest_asyncio
import asyncio
from typing import Generator, AsyncGenerator, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from httpx import AsyncClient
try:
    from main import app
except ImportError:
    app = None  # This will be used as a fallback if main.py is not available

@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def db_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create a MongoDB client for the session."""
    client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://localhost:27017")
    yield client
    client.close()  # This is synchronous, not awaitable

@pytest_asyncio.fixture
async def test_db(db_client: AsyncIOMotorClient) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create a test database that will be cleared after the test."""
    db = db_client.test_db
    yield db
    await db_client.drop_database("test_db")

@pytest_asyncio.fixture
async def test_db_with_data(test_db: AsyncIOMotorDatabase) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create a test database with sample data."""
    # Add code to insert sample data if needed
    yield test_db

@pytest_asyncio.fixture
async def app_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing the API."""
    if app is None:
        pytest.skip("main.py app not available")
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
