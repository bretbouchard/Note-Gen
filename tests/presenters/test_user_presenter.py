"""Tests for the user presenter."""
import pytest
from bson import ObjectId
from datetime import datetime

from note_gen.presenters.user_presenter import UserPresenter
from note_gen.models.user import User


def test_present():
    """Test presenting a single user."""
    # Arrange
    now = datetime.now()
    user = User(
        id="5f9f1b9b9c9d1b9b9c9d1b9b",
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )

    # Act
    result = UserPresenter.present(user)

    # Assert
    assert result["id"] == str(user.id)
    assert result["username"] == user.username
    assert result["email"] == user.email
    assert result["is_active"] == user.is_active
    assert result["is_superuser"] == user.is_superuser


def test_present_without_id():
    """Test presenting a user without an ID."""
    # Arrange
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )

    # Act
    result = UserPresenter.present(user)

    # Assert
    assert result["id"] is None
    assert result["username"] == user.username
    assert result["email"] == user.email
    assert result["is_active"] is True
    assert result["is_superuser"] is False


def test_present_many():
    """Test presenting multiple users."""
    # Arrange
    users = [
        User(
            id="5f9f1b9b9c9d1b9b9c9d1b9b",
            username="user1",
            email="user1@example.com",
            hashed_password="hashed_password"
        ),
        User(
            id="5f9f1b9b9c9d1b9b9c9d1b9c",
            username="user2",
            email="user2@example.com",
            hashed_password="hashed_password"
        )
    ]

    # Act
    result = UserPresenter.present_many(users)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == str(users[0].id)
    assert result[0]["username"] == users[0].username
    assert result[0]["email"] == users[0].email
    assert result[1]["id"] == str(users[1].id)
    assert result[1]["username"] == users[1].username
    assert result[1]["email"] == users[1].email


def test_present_profile():
    """Test presenting a user profile."""
    # Arrange
    user = User(
        id="5f9f1b9b9c9d1b9b9c9d1b9b",
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        preferences={"theme": "dark", "language": "en"},
        settings={"notifications": True}
    )

    # Act
    result = UserPresenter.present_profile(user)

    # Assert
    assert result["id"] == str(user.id)
    assert result["username"] == user.username
    assert result["email"] == user.email
    assert result["preferences"] == user.preferences
    assert result["settings"] == user.settings


def test_present_profile_without_preferences():
    """Test presenting a user profile without preferences."""
    # Arrange
    user = User(
        id="5f9f1b9b9c9d1b9b9c9d1b9b",
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )

    # Act
    result = UserPresenter.present_profile(user)

    # Assert
    assert result["id"] == str(user.id)
    assert result["username"] == user.username
    assert result["email"] == user.email
    assert result["preferences"] == {}
