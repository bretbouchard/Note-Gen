"""Tests for database dependencies."""
import pytest
from unittest.mock import AsyncMock, patch
from motor.motor_asyncio import AsyncIOMotorDatabase
from note_gen.dependencies.database import get_db


@pytest.mark.asyncio
async def test_get_db():
    """Test the get_db dependency."""
    # Mock the get_db_conn function
    mock_db = AsyncMock(spec=AsyncIOMotorDatabase)
    
    with patch('note_gen.dependencies.database.get_db_conn', return_value=mock_db):
        # Use the dependency as an async generator
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        # Check that we got the expected database
        assert db is mock_db
        
        # Test that we can close the generator without errors
        try:
            await db_gen.aclose()
        except StopAsyncIteration:
            pass  # This is expected
