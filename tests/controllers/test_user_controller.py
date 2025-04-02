"""Tests for the user controller."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.note_gen.controllers.user_controller import UserController
from src.note_gen.models.user import User


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository for testing."""
    repository = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.find_all = AsyncMock(return_value=[])
    repository.create = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock(return_value=True)
    repository.find = AsyncMock(return_value=[])
    return repository


@pytest.fixture
def controller(mock_user_repository):
    """Create a controller instance for testing."""
    return UserController(mock_user_repository)


@pytest.mark.asyncio
async def test_get_user(controller, mock_user_repository):
    """Test getting a user by ID."""
    # Arrange
    user_id = "test_id"
    expected_user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    mock_user_repository.find_by_id.return_value = expected_user

    # Act
    result = await controller.get_user(user_id)

    # Assert
    assert result == expected_user
    mock_user_repository.find_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_all_users(controller, mock_user_repository):
    """Test getting all users."""
    # Arrange
    expected_users = [
        User(
            username="user1",
            email="user1@example.com",
            full_name="User One"
        ),
        User(
            username="user2",
            email="user2@example.com",
            full_name="User Two"
        )
    ]
    mock_user_repository.find_all.return_value = expected_users

    # Act
    result = await controller.get_all_users()

    # Assert
    assert result == expected_users
    mock_user_repository.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_create_user(controller, mock_user_repository):
    """Test creating a user."""
    # Arrange
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "full_name": "New User"
    }
    expected_user = User(**user_data)
    mock_user_repository.create.return_value = expected_user
    mock_user_repository.find.return_value = []  # No existing user with the same username

    # Act
    result = await controller.create_user(user_data)

    # Assert
    assert result == expected_user
    mock_user_repository.find.assert_called_once_with({"username": user_data["username"]})
    mock_user_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_username_exists(controller, mock_user_repository):
    """Test creating a user with an existing username."""
    # Arrange
    user_data = {
        "username": "existinguser",
        "email": "existing@example.com",
        "full_name": "Existing User"
    }
    existing_user = User(**user_data)
    mock_user_repository.find.return_value = [existing_user]  # Existing user with the same username

    # Act & Assert
    with pytest.raises(ValueError, match="Username already exists"):
        await controller.create_user(user_data)
    
    mock_user_repository.find.assert_called_once_with({"username": user_data["username"]})
    mock_user_repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_update_user(controller, mock_user_repository):
    """Test updating a user."""
    # Arrange
    user_id = "test_id"
    user_data = {
        "email": "updated@example.com",
        "full_name": "Updated User"
    }
    existing_user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    updated_user = User(
        username="testuser",
        email="updated@example.com",
        full_name="Updated User"
    )
    mock_user_repository.find_by_id.return_value = existing_user
    mock_user_repository.update.return_value = updated_user

    # Act
    result = await controller.update_user(user_id, user_data)

    # Assert
    assert result == updated_user
    mock_user_repository.find_by_id.assert_called_once_with(user_id)
    mock_user_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_not_found(controller, mock_user_repository):
    """Test updating a non-existent user."""
    # Arrange
    user_id = "nonexistent_id"
    user_data = {
        "email": "updated@example.com",
        "full_name": "Updated User"
    }
    mock_user_repository.find_by_id.return_value = None

    # Act
    result = await controller.update_user(user_id, user_data)

    # Assert
    assert result is None
    mock_user_repository.find_by_id.assert_called_once_with(user_id)
    mock_user_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_user(controller, mock_user_repository):
    """Test deleting a user."""
    # Arrange
    user_id = "test_id"
    mock_user_repository.delete.return_value = True

    # Act
    result = await controller.delete_user(user_id)

    # Assert
    assert result is True
    mock_user_repository.delete.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_current_user(controller):
    """Test getting the current user."""
    # Act
    result = await controller.get_current_user()

    # Assert
    assert result.username == "current_user"
    assert result.email == "current@example.com"
    assert result.full_name == "Current User"


@pytest.mark.asyncio
async def test_get_user_by_username(controller, mock_user_repository):
    """Test getting a user by username."""
    # Arrange
    username = "testuser"
    expected_user = User(
        username=username,
        email="test@example.com",
        full_name="Test User"
    )
    mock_user_repository.find.return_value = [expected_user]

    # Act
    result = await controller.get_user_by_username(username)

    # Assert
    assert result == expected_user
    mock_user_repository.find.assert_called_once_with({"username": username})
