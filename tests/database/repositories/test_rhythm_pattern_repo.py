"""Tests for RhythmPatternRepository."""
import pytest
import pytest_asyncio
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from src.note_gen.database.repositories.rhythm_pattern import RhythmPatternRepository
from src.note_gen.models.patterns import RhythmPattern


@pytest_asyncio.fixture
async def mock_database():
    """Create a mock MongoDB database."""
    database = MagicMock(spec=AsyncIOMotorDatabase)

    # Mock collection access
    mock_collection = MagicMock(spec=AsyncIOMotorCollection)
    database.__getitem__.return_value = mock_collection

    # Mock find method
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock()
    mock_collection.find = MagicMock(return_value=mock_cursor)

    return database, mock_collection


@pytest.fixture
def test_repository(mock_database):
    """Create a test repository."""
    database, _ = mock_database
    repo = RhythmPatternRepository(
        database=database,
        collection_name="rhythm_patterns"
    )
    return repo


@pytest.mark.asyncio
async def test_init(mock_database):
    """Test repository initialization."""
    database, _ = mock_database
    repo = RhythmPatternRepository(
        database=database,
        collection_name="rhythm_patterns"
    )

    assert repo.database == database
    assert repo.collection == database["rhythm_patterns"]
    assert repo.model_class == RhythmPattern


@pytest.mark.asyncio
async def test_find_by_time_signature(test_repository, mock_database):
    """Test finding rhythm patterns by time signature."""
    _, mock_collection = mock_database

    # Mock the cursor.to_list method to return documents
    mock_cursor = mock_collection.find.return_value
    mock_cursor.to_list.return_value = [
        {
            "name": "4/4 Pattern 1",
            "time_signature": [4, 4],
            "pattern": [{"position": 0.0, "duration": 1.0}],
            "total_duration": 4.0
        },
        {
            "name": "4/4 Pattern 2",
            "time_signature": [4, 4],
            "pattern": [{"position": 0.0, "duration": 1.0}],
            "total_duration": 4.0
        }
    ]

    # Call the method
    results = await test_repository.find_by_time_signature("4/4")

    # Verify the results
    assert len(results) == 2
    assert all(isinstance(result, RhythmPattern) for result in results)
    assert results[0].name == "4/4 Pattern 1"
    assert results[0].time_signature == (4, 4)  # Time signature is a tuple
    assert results[1].name == "4/4 Pattern 2"
    assert results[1].time_signature == (4, 4)  # Time signature is a tuple

    # Verify the find method was called with the correct arguments
    mock_collection.find.assert_called_once_with({"time_signature": "4/4"})
    mock_cursor.to_list.assert_called_once_with(None)
