"""Tests for MongoDB repository implementation."""
import pytest
import pytest_asyncio
from typing import Dict, Any, Optional, List
from unittest.mock import MagicMock, AsyncMock
from bson import ObjectId
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from src.note_gen.database.repositories.mongodb import MongoDBRepository


# Define a test model
class MockTestModel(BaseModel):
    """Test model for MongoDB repository tests."""
    name: str
    value: int


@pytest_asyncio.fixture
async def mock_database():
    """Create a mock MongoDB database."""
    database = MagicMock(spec=AsyncIOMotorDatabase)

    # Mock collection access
    mock_collection = MagicMock(spec=AsyncIOMotorCollection)
    database.__getitem__.return_value = mock_collection

    # Mock find_one method
    mock_collection.find_one = AsyncMock()

    # Mock find method
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock()
    mock_collection.find = MagicMock(return_value=mock_cursor)

    return database, mock_collection


@pytest.fixture
def test_repository(mock_database):
    """Create a test repository."""
    database, _ = mock_database
    repo = MongoDBRepository[MockTestModel](
        database=database,
        collection_name="test_collection",
        model_class=MockTestModel
    )
    return repo


@pytest.mark.asyncio
async def test_init(mock_database):
    """Test repository initialization."""
    database, _ = mock_database
    repo = MongoDBRepository[MockTestModel](
        database=database,
        collection_name="test_collection",
        model_class=MockTestModel
    )

    assert repo.database == database
    assert repo.collection == database["test_collection"]
    assert repo.model_class == MockTestModel


@pytest.mark.asyncio
async def test_find_one(test_repository, mock_database):
    """Test finding a single document."""
    _, mock_collection = mock_database

    # Mock the find_one method to return a document
    mock_collection.find_one.return_value = {"name": "test", "value": 42}

    # Call the method
    result = await test_repository.find_one({"name": "test"})

    # Verify the result
    assert isinstance(result, MockTestModel)
    assert result.name == "test"
    assert result.value == 42

    # Verify the find_one method was called with the correct arguments
    mock_collection.find_one.assert_called_once_with({"name": "test"})

    # Test with non-existent document
    mock_collection.find_one.reset_mock()
    mock_collection.find_one.return_value = None

    result = await test_repository.find_one({"name": "nonexistent"})
    assert result is None


@pytest.mark.asyncio
async def test_find_many(test_repository, mock_database):
    """Test finding multiple documents."""
    _, mock_collection = mock_database

    # Mock the cursor.to_list method to return documents
    mock_cursor = mock_collection.find.return_value
    mock_cursor.to_list.return_value = [
        {"name": "test1", "value": 1},
        {"name": "test2", "value": 2}
    ]

    # Call the method
    results = await test_repository.find_many({"name": {"$regex": "test"}})

    # Verify the results
    assert len(results) == 2
    assert all(isinstance(result, MockTestModel) for result in results)
    assert results[0].name == "test1"
    assert results[0].value == 1
    assert results[1].name == "test2"
    assert results[1].value == 2

    # Verify the find method was called with the correct arguments
    mock_collection.find.assert_called_once_with({"name": {"$regex": "test"}})
    mock_cursor.to_list.assert_called_once_with(None)


@pytest.mark.asyncio
async def test_convert_to_model(test_repository):
    """Test converting dictionary to model."""
    # Test with valid document
    doc = {"name": "test", "value": 42}
    model = test_repository._convert_to_model(doc)

    assert isinstance(model, MockTestModel)
    assert model.name == "test"
    assert model.value == 42
