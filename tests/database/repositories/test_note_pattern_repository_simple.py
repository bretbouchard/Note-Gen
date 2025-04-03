"""Simple tests for the note pattern repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.note_pattern_repository import NotePatternRepository
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.note import Note
from note_gen.core.enums import ScaleType, PatternDirection


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    return AsyncMock(spec=AsyncIOMotorCollection)


@pytest.fixture
def repository(mock_collection):
    """Create a repository instance."""
    return NotePatternRepository(mock_collection)


def test_init(mock_collection):
    """Test repository initialization."""
    repo = NotePatternRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_name_not_found(repository, mock_collection):
    """Test finding a note pattern by name when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None
    
    # Call method
    result = await repository.find_by_name("Test Pattern")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Pattern"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_name_exception(repository, mock_collection):
    """Test finding a note pattern by name when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Test exception")
    
    # Call method
    result = await repository.find_by_name("Test Pattern")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Pattern"})
    assert result is None
