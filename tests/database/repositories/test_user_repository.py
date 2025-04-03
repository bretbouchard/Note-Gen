"""Tests for the user repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.user_repository import UserRepository
from note_gen.models.user import User


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    collection = AsyncMock(spec=AsyncIOMotorCollection)
    return collection


@pytest.fixture
def sample_user():
    """Create a sample user."""
    # Create a user directly
    return User(
        id="507f1f77bcf86cd799439011",
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123",
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
def sample_user_dict(sample_user):
    """Create a sample user dict as it would be stored in MongoDB."""
    user_dict = sample_user.model_dump()
    user_dict["_id"] = ObjectId(user_dict["id"])
    del user_dict["id"]
    return user_dict


@pytest.fixture
def repository(mock_collection):
    """Create a repository instance."""
    return UserRepository(mock_collection)


@pytest.mark.asyncio
async def test_init(mock_collection):
    """Test repository initialization."""
    repo = UserRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_username(repository, mock_collection, sample_user_dict, sample_user):
    """Test finding a user by username."""
    # Setup mock
    mock_collection.find_one.return_value = MagicMock()
    mock_collection.find_one.return_value = sample_user_dict

    # Call method
    result = await repository.find_by_username("testuser")

    # Verify
    mock_collection.find_one.assert_called_once_with({"username": "testuser"})
    assert isinstance(result, User)
    assert result.id == sample_user.id
    assert result.username == sample_user.username
    assert result.email == sample_user.email


@pytest.mark.asyncio
async def test_find_by_username_not_found(repository, mock_collection):
    """Test finding a user by username when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None

    # Call method
    result = await repository.find_by_username("nonexistent")

    # Verify
    mock_collection.find_one.assert_called_once_with({"username": "nonexistent"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_username_exception(repository, mock_collection):
    """Test finding a user by username when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Database error")

    # Call method
    result = await repository.find_by_username("testuser")

    # Verify
    mock_collection.find_one.assert_called_once_with({"username": "testuser"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_email(repository, mock_collection, sample_user_dict, sample_user):
    """Test finding a user by email."""
    # Setup mock
    mock_collection.find_one.return_value = MagicMock()
    mock_collection.find_one.return_value = sample_user_dict

    # Call method
    result = await repository.find_by_email("test@example.com")

    # Verify
    mock_collection.find_one.assert_called_once_with({"email": "test@example.com"})
    assert isinstance(result, User)
    assert result.id == sample_user.id
    assert result.username == sample_user.username
    assert result.email == sample_user.email


@pytest.mark.asyncio
async def test_find_active_users(repository, mock_collection, sample_user_dict, sample_user):
    """Test finding active users."""
    # Setup mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_user_dict]
    mock_collection.find.return_value = mock_cursor

    # Call method
    result = await repository.find_active_users()

    # Verify
    mock_collection.find.assert_called_once_with({"is_active": True})
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert len(result) == 1
    assert isinstance(result[0], User)
    assert result[0].id == sample_user.id
    assert result[0].username == sample_user.username
    assert result[0].is_active is True


@pytest.mark.asyncio
async def test_find_superusers(repository, mock_collection, sample_user_dict):
    """Test finding superusers."""
    # Modify the sample user to be a superuser
    sample_user_dict["is_superuser"] = True

    # Setup mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_user_dict]
    mock_collection.find.return_value = mock_cursor

    # Call method
    result = await repository.find_superusers()

    # Verify
    mock_collection.find.assert_called_once_with({"is_superuser": True})
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert len(result) == 1
    assert isinstance(result[0], User)
    assert result[0].is_superuser is True


@pytest.mark.asyncio
async def test_update_password(repository, mock_collection, sample_user_dict):
    """Test updating a user's password."""
    # Setup mocks
    mock_result = MagicMock()
    mock_result.matched_count = 1
    mock_collection.update_one.return_value = mock_result

    updated_dict = dict(sample_user_dict)
    updated_dict["hashed_password"] = "newhashed123"
    mock_collection.find_one.return_value = MagicMock()
    mock_collection.find_one.return_value = updated_dict

    # Call method
    result = await repository.update_password("507f1f77bcf86cd799439011", "newhashed123")

    # Verify
    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId("507f1f77bcf86cd799439011")},
        {"$set": {"hashed_password": "newhashed123"}}
    )
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId("507f1f77bcf86cd799439011")})
    assert isinstance(result, User)
    assert result.hashed_password == "newhashed123"


@pytest.mark.asyncio
async def test_update_password_not_found(repository, mock_collection):
    """Test updating a password for a non-existent user."""
    # Setup mock
    mock_result = AsyncMock()
    mock_result.matched_count = 0
    mock_collection.update_one.return_value = mock_result

    # Call method
    result = await repository.update_password("507f1f77bcf86cd799439099", "newhashed123")

    # Verify
    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId("507f1f77bcf86cd799439099")},
        {"$set": {"hashed_password": "newhashed123"}}
    )
    assert result is None


@pytest.mark.asyncio
async def test_update_password_exception(repository, mock_collection):
    """Test updating a password when an exception occurs."""
    # Setup mock
    mock_collection.update_one.side_effect = Exception("Database error")

    # Call method
    result = await repository.update_password("507f1f77bcf86cd799439011", "newhashed123")

    # Verify
    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId("507f1f77bcf86cd799439011")},
        {"$set": {"hashed_password": "newhashed123"}}
    )
    assert result is None
