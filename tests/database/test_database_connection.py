"""Tests for database connection management."""
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.note_gen.database.db import init_db, get_db_conn, close_mongo_connection


@pytest_asyncio.fixture
async def mock_client():
    """Create a mock AsyncIOMotorClient."""
    with patch('src.note_gen.database.db._client', None):
        client = MagicMock(spec=AsyncIOMotorClient)
        mock_db = MagicMock(spec=AsyncIOMotorDatabase)
        client.__getitem__.return_value = mock_db
        
        with patch('src.note_gen.database.db.AsyncIOMotorClient', return_value=client):
            yield client, mock_db


@pytest.mark.asyncio
async def test_init_db(mock_client):
    """Test initializing the database client."""
    client, _ = mock_client
    
    # Call init_db
    result = await init_db()
    
    # Verify the client was created with the correct URL
    assert result == client


@pytest.mark.asyncio
async def test_get_db_conn_with_existing_client():
    """Test getting database connection with existing client."""
    # Create a mock client
    mock_client = MagicMock(spec=AsyncIOMotorClient)
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)
    mock_client.__getitem__.return_value = mock_db
    
    # Set the global client
    with patch('src.note_gen.database.db._client', mock_client), \
         patch('src.note_gen.database.db.settings.database_name', 'test_db'):
        # Call get_db_conn
        result = await get_db_conn()
        
        # Verify the result
        assert result == mock_db
        mock_client.__getitem__.assert_called_once_with('test_db')


@pytest.mark.asyncio
async def test_get_db_conn_without_existing_client(mock_client):
    """Test getting database connection without existing client."""
    client, mock_db = mock_client
    
    with patch('src.note_gen.database.db.settings.database_name', 'test_db'):
        # Call get_db_conn
        result = await get_db_conn()
        
        # Verify the result
        assert result == mock_db
        client.__getitem__.assert_called_once_with('test_db')


@pytest.mark.asyncio
async def test_close_mongo_connection():
    """Test closing the MongoDB connection."""
    # Create a mock client
    mock_client = MagicMock(spec=AsyncIOMotorClient)
    
    # Set the global client
    with patch('src.note_gen.database.db._client', mock_client):
        # Call close_mongo_connection
        await close_mongo_connection()
        
        # Verify the client was closed
        mock_client.close.assert_called_once()
        
        # Verify the global client was set to None
        with patch('src.note_gen.database.db._client', None):
            assert True
