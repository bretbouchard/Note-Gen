"""Simple tests for the chord progression repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.chord_progression_repository import ChordProgressionRepository
from note_gen.models.chord_progression import ChordProgression


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    return AsyncMock(spec=AsyncIOMotorCollection)


@pytest.fixture
def repository(mock_collection):
    """Create a repository instance."""
    return ChordProgressionRepository(mock_collection)


@pytest.fixture
def sample_progression():
    """Create a sample chord progression."""
    return ChordProgression(
        id="507f1f77bcf86cd799439011",
        name="Test Progression",
        key="C",
        scale_type="MAJOR",
        chords=[]
    )


def test_init(mock_collection):
    """Test repository initialization."""
    repo = ChordProgressionRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_name_not_found(repository, mock_collection):
    """Test finding a chord progression by name when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None
    
    # Call method
    result = await repository.find_by_name("Test Progression")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Progression"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_name_exception(repository, mock_collection):
    """Test finding a chord progression by name when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Test exception")
    
    # Call method
    result = await repository.find_by_name("Test Progression")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Progression"})
    assert result is None
