"""Tests for database connection."""
import pytest
from unittest.mock import patch, MagicMock
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from note_gen.database.connection import get_database_connection


@pytest.mark.asyncio
async def test_get_database_connection_default_values():
    """Test database connection with default values."""
    # Mock the AsyncIOMotorClient to avoid actual connection
    with patch('note_gen.database.connection.AsyncIOMotorClient') as mock_client:
        # Setup the mock
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_db = MagicMock(spec=AsyncIOMotorDatabase)
        mock_instance.__getitem__.return_value = mock_db

        # Call the function
        db = await get_database_connection()

        # Verify the client was created with correct parameters
        mock_client.assert_called_once_with(
            "mongodb://localhost:27017",
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )

        # Verify the database was accessed
        mock_instance.__getitem__.assert_called_once_with("note_gen")

        # Verify the return value
        assert db == mock_db


@pytest.mark.asyncio
async def test_get_database_connection_custom_values():
    """Test database connection with custom values."""
    # Mock the DATABASE constant
    custom_db_config = {
        "uri": "mongodb://customhost:27018",
        "name": "custom_db",
        "timeout_ms": 10000,
        "pool": {
            "max_size": 20,
            "min_size": 5
        }
    }

    # Mock the AsyncIOMotorClient to avoid actual connection
    with patch('note_gen.database.connection.AsyncIOMotorClient') as mock_client, \
         patch('note_gen.database.connection.DATABASE', custom_db_config):
        # Setup the mock
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_db = MagicMock(spec=AsyncIOMotorDatabase)
        mock_instance.__getitem__.return_value = mock_db

        # Call the function
        db = await get_database_connection()

        # Verify the client was created with correct parameters
        mock_client.assert_called_once_with(
            "mongodb://customhost:27018",
            serverSelectionTimeoutMS=10000,
            maxPoolSize=20,
            minPoolSize=5
        )

        # Verify the database was accessed
        mock_instance.__getitem__.assert_called_once_with("custom_db")

        # Verify the return value
        assert db == mock_db
