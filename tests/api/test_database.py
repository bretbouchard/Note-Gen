"""Tests for API database connection management."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.note_gen.api.database import get_db, get_database


@pytest.mark.asyncio
async def test_get_db():
    """Test the get_db generator function."""
    # Create a mock database
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)
    
    # Patch the database object in the module
    with patch('src.note_gen.api.database.database', mock_db):
        # Call the generator function
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        # Verify the database was yielded
        assert db is mock_db
        
        # Verify the generator completes properly
        with pytest.raises(StopAsyncIteration):
            await db_gen.__anext__()


@pytest.mark.asyncio
async def test_get_database():
    """Test the get_database dependency function."""
    # Create a mock database
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)
    
    # Call the dependency function
    result = await get_database(mock_db)
    
    # Verify the database was returned
    assert result is mock_db
