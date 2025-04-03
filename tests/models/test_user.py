"""Tests for user model."""
import pytest
from pydantic import ValidationError
from note_gen.models.user import User


def test_user_init_valid():
    """Test User initialization with valid data."""
    # Create a valid user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123"
    )
    
    # Verify fields
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashedpassword123"
    assert user.is_active is True  # Default value
    assert user.is_superuser is False  # Default value


def test_user_init_with_id():
    """Test User initialization with an ID."""
    # Create a user with an ID
    user = User(
        id="user123",
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123"
    )
    
    # Verify ID field
    assert user.id == "user123"


def test_user_init_with_custom_flags():
    """Test User initialization with custom active and superuser flags."""
    # Create a user with custom flags
    user = User(
        username="adminuser",
        email="admin@example.com",
        hashed_password="hashedpassword123",
        is_active=False,
        is_superuser=True
    )
    
    # Verify flags
    assert user.is_active is False
    assert user.is_superuser is True


def test_user_username_validation():
    """Test username validation."""
    # Test username too short
    with pytest.raises(ValidationError):
        User(
            username="ab",  # Too short (min_length=3)
            email="test@example.com",
            hashed_password="hashedpassword123"
        )
    
    # Test username too long
    with pytest.raises(ValidationError):
        User(
            username="a" * 51,  # Too long (max_length=50)
            email="test@example.com",
            hashed_password="hashedpassword123"
        )


def test_user_email_validation():
    """Test email validation."""
    # Test invalid email format
    with pytest.raises(ValidationError):
        User(
            username="testuser",
            email="invalid-email",  # Invalid format
            hashed_password="hashedpassword123"
        )


def test_user_whitespace_stripping():
    """Test that whitespace is stripped from fields."""
    # Create a user with whitespace in fields
    user = User(
        username="  testuser  ",
        email="  test@example.com  ",
        hashed_password="hashedpassword123"
    )
    
    # Verify whitespace was stripped
    assert user.username == "testuser"
    assert user.email == "test@example.com"
