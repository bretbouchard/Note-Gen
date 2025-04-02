"""Tests for database models."""
import pytest
from unittest.mock import patch, MagicMock
from src.note_gen.models.database import DatabaseConfig
from src.note_gen.core.enums import ValidationLevel
from src.note_gen.validation.base_validation import ValidationResult


def test_database_config_init():
    """Test DatabaseConfig initialization with valid data."""
    # Create a valid config
    config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection"
    )

    # Verify fields
    assert config.host == "localhost"
    assert config.port == 27017
    assert config.database == "test_db"
    assert config.collection == "test_collection"
    assert config.username is None
    assert config.password is None
    assert config.timeout_ms == 5000  # Default value
    assert config.max_pool_size == 10  # Default value
    assert config.min_pool_size == 1   # Default value
    assert config.ssl_enabled is False
    assert config.ssl_ca_file is None


def test_database_config_with_auth():
    """Test DatabaseConfig with authentication."""
    # Create a config with auth
    config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        username="testuser",
        password="testpass"
    )

    # Verify auth fields
    assert config.username == "testuser"
    assert config.password == "testpass"


def test_database_config_with_ssl():
    """Test DatabaseConfig with SSL."""
    # Create a config with SSL
    config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        ssl_enabled=True,
        ssl_ca_file="/path/to/ca.pem"
    )

    # Verify SSL fields
    assert config.ssl_enabled is True
    assert config.ssl_ca_file == "/path/to/ca.pem"


def test_database_config_custom_pool_size():
    """Test DatabaseConfig with custom pool size."""
    # Create a config with custom pool size
    config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        min_pool_size=5,
        max_pool_size=20
    )

    # Verify pool size fields
    assert config.min_pool_size == 5
    assert config.max_pool_size == 20


def test_database_config_custom_timeout():
    """Test DatabaseConfig with custom timeout."""
    # Create a config with custom timeout
    config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        timeout_ms=10000
    )

    # Verify timeout field
    assert config.timeout_ms == 10000


def test_database_config_validation_level():
    """Test DatabaseConfig validation level."""
    # Verify class-level validation level
    assert DatabaseConfig.validation_level == ValidationLevel.NORMAL


def test_database_config_validate_config_valid():
    """Test validate_config with valid configuration."""
    # Create a valid config
    config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        min_pool_size=5,
        max_pool_size=20
    )

    # Validate the config
    result = config.validate_config()

    # Verify the result
    assert result.is_valid is True
    assert len(result.violations) == 0


def test_database_config_validate_config_invalid_pool_size():
    """Test validate_config with invalid pool size."""
    # Create a config with invalid pool size (min > max)
    config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        min_pool_size=10,
        max_pool_size=5
    )

    # Validate the config
    result = config.validate_config()

    # Verify the result
    assert result.is_valid is False
    assert len(result.violations) == 1
    assert result.violations[0].path == "pool_size"
    assert "min_pool_size cannot be greater than max_pool_size" in result.violations[0].message


def test_database_config_validate_config_invalid_ssl():
    """Test validate_config with invalid SSL configuration."""
    # Create a config with invalid SSL (enabled but no CA file)
    config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        ssl_enabled=True,
        ssl_ca_file=None
    )

    # Validate the config
    result = config.validate_config()

    # Verify the result
    assert result.is_valid is False
    assert len(result.violations) >= 1
    # Check for SSL-related violation
    ssl_violation = next((v for v in result.violations if "ssl" in v.path.lower()), None)
    assert ssl_violation is not None
