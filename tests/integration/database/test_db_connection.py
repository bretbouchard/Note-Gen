import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from src.note_gen.core.database import get_db_conn
from src.note_gen.core.constants import DATABASE, DEFAULT_DB_NAME

pytestmark = pytest.mark.asyncio

async def test_connection():
    """Test database connection."""
    try:
        # Connect to database
        db = await get_db_conn()
        
        # Verify connection
        assert isinstance(db, AsyncIOMotorDatabase)
        assert db.name == DEFAULT_DB_NAME
        
        # Test connection with simple operation
        await db.command('ping')
        
        # Clean up
        client = db.client
        client.close()
        
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        pytest.skip(f"MongoDB not available: {str(e)}")
