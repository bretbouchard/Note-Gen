import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from src.note_gen.database.db import get_db_conn, MONGODB_URI

_clients = set()  # Add this at the top level

@pytest.fixture
async def mongodb_client():
    client = AsyncIOMotorClient(MONGODB_URI)
    _clients.add(client)  # Track the client
    yield client
    client.close()
    _clients.remove(client)  # Clean up

@pytest.mark.asyncio
async def test_connection(mongodb_client):
    try:
        await mongodb_client.admin.command('ping')
        assert True
    except Exception as e:
        assert False, f"Database connection failed: {str(e)}"
