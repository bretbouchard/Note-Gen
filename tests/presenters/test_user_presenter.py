"""Tests for the user presenter."""
import pytest
from bson import ObjectId
from datetime import datetime

from src.note_gen.presenters.user_presenter import UserPresenter
from src.note_gen.models.user import User


def test_present():
    """Test presenting a single user."""
    # Arrange
    now = datetime.now()
    user = User(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        disabled=False,
        created_at=now,
        updated_at=now
    )

    # Act
    result = UserPresenter.present(user)

    # Assert
    assert result["id"] == str(user.id)
    assert result["username"] == user.username
    assert result["email"] == user.email
    assert result["full_name"] == user.full_name
    assert result["disabled"] == user.disabled
    assert result["created_at"] == now.isoformat()
    assert result["updated_at"] == now.isoformat()


def test_present_without_id():
    """Test presenting a user without an ID."""
    # Arrange
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )

    # Act
    result = UserPresenter.present(user)

    # Assert
    assert result["id"] is None
    assert result["username"] == user.username
    assert result["email"] == user.email
    assert result["full_name"] == user.full_name
    assert result["disabled"] is False
    assert result["created_at"] is None
    assert result["updated_at"] is None


def test_present_many():
    """Test presenting multiple users."""
    # Arrange
    users = [
        User(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
            username="user1",
            email="user1@example.com",
            full_name="User One"
        ),
        User(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9c"),
            username="user2",
            email="user2@example.com",
            full_name="User Two"
        )
    ]

    # Act
    result = UserPresenter.present_many(users)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == str(users[0].id)
    assert result[0]["username"] == users[0].username
    assert result[0]["email"] == users[0].email
    assert result[0]["full_name"] == users[0].full_name
    assert result[1]["id"] == str(users[1].id)
    assert result[1]["username"] == users[1].username
    assert result[1]["email"] == users[1].email
    assert result[1]["full_name"] == users[1].full_name


def test_present_profile():
    """Test presenting a user profile."""
    # Arrange
    user = User(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        preferences={"theme": "dark", "language": "en"},
        settings={"notifications": True}
    )

    # Act
    result = UserPresenter.present_profile(user)

    # Assert
    assert result["id"] == str(user.id)
    assert result["username"] == user.username
    assert result["email"] == user.email
    assert result["full_name"] == user.full_name
    assert result["preferences"] == user.preferences
    assert result["settings"] == user.settings


def test_present_profile_without_preferences():
    """Test presenting a user profile without preferences."""
    # Arrange
    user = User(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )

    # Act
    result = UserPresenter.present_profile(user)

    # Assert
    assert result["id"] == str(user.id)
    assert result["username"] == user.username
    assert result["email"] == user.email
    assert result["full_name"] == user.full_name
    assert result["preferences"] == {}
