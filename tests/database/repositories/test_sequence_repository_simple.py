"""Simple tests for the sequence repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.sequence_repository import SequenceRepository
from note_gen.models.sequence import Sequence
from note_gen.models.note_sequence import NoteSequence
from note_gen.models.note import Note


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    return AsyncMock(spec=AsyncIOMotorCollection)


@pytest.fixture
def repository(mock_collection):
    """Create a repository instance."""
    return SequenceRepository(mock_collection)


def test_init(mock_collection):
    """Test repository initialization."""
    repo = SequenceRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_name_not_found(repository, mock_collection):
    """Test finding a sequence by name when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None
    
    # Call method
    result = await repository.find_by_name("Test Sequence")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Sequence"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_name_exception(repository, mock_collection):
    """Test finding a sequence by name when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Test exception")
    
    # Call method
    result = await repository.find_by_name("Test Sequence")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Sequence"})
    assert result is None
