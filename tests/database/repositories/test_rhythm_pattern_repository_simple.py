"""Simple tests for the rhythm pattern repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.rhythm_pattern_repository import RhythmPatternRepository
from note_gen.models.patterns import RhythmPattern, RhythmNote


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    return AsyncMock(spec=AsyncIOMotorCollection)


@pytest.fixture
def repository(mock_collection):
    """Create a repository instance."""
    return RhythmPatternRepository(mock_collection)


def test_init(mock_collection):
    """Test repository initialization."""
    repo = RhythmPatternRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_name_not_found(repository, mock_collection):
    """Test finding a rhythm pattern by name when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None
    
    # Call method
    result = await repository.find_by_name("Test Rhythm")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Rhythm"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_name_exception(repository, mock_collection):
    """Test finding a rhythm pattern by name when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Test exception")
    
    # Call method
    result = await repository.find_by_name("Test Rhythm")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Rhythm"})
    assert result is None
