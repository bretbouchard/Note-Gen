"""Simple tests for the user repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.user_repository import UserRepository
from note_gen.models.user import User


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    return AsyncMock(spec=AsyncIOMotorCollection)


@pytest.fixture
def repository(mock_collection):
    """Create a repository instance."""
    return UserRepository(mock_collection)


def test_init(mock_collection):
    """Test repository initialization."""
    repo = UserRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_username_not_found(repository, mock_collection):
    """Test finding a user by username when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None
    
    # Call method
    result = await repository.find_by_username("testuser")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"username": "testuser"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_username_exception(repository, mock_collection):
    """Test finding a user by username when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Test exception")
    
    # Call method
    result = await repository.find_by_username("testuser")
    
    # Verify
    mock_collection.find_one.assert_called_once_with({"username": "testuser"})
    assert result is None
