"""Tests for database configuration."""
import pytest
from src.note_gen.database.config import DatabaseConfig


def test_database_config_defaults():
    """Test default values for DatabaseConfig."""
    config = DatabaseConfig()
    assert config.host == "localhost"
    assert config.port == 27017
    assert config.database == "note_gen_db_dev"
    assert config.username is None
    assert config.password is None


def test_database_config_custom_values():
    """Test custom values for DatabaseConfig."""
    config = DatabaseConfig(
        host="testhost",
        port=12345,
        database="testdb",
        username="testuser",
        password="testpass"
    )
    assert config.host == "testhost"
    assert config.port == 12345
    assert config.database == "testdb"
    assert config.username == "testuser"
    assert config.password == "testpass"


def test_get_connection_url_without_auth():
    """Test connection URL generation without authentication."""
    config = DatabaseConfig(host="testhost", port=12345)
    url = config.get_connection_url()
    assert url == "mongodb://testhost:12345"


def test_get_connection_url_with_auth():
    """Test connection URL generation with authentication."""
    config = DatabaseConfig(
        host="testhost",
        port=12345,
        username="testuser",
        password="testpass"
    )
    url = config.get_connection_url()
    assert url == "mongodb://testuser:testpass@testhost:12345"
