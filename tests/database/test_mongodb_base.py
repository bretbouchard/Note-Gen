"""Tests for MongoDB base repository."""
import pytest
import pytest_asyncio
from typing import Dict, Any, Optional
from unittest.mock import MagicMock, AsyncMock
from bson import ObjectId
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection
from src.note_gen.database.mongodb import MongoDBRepository


# Define a test model
class MockTestModel(BaseModel):
    """Test model for MongoDB repository tests."""
    name: str
    value: int


@pytest_asyncio.fixture
async def mock_collection():
    """Create a mock MongoDB collection."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    # Mock find_one method
    collection.find_one = AsyncMock()

    # Mock find method
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock()
    collection.find = MagicMock(return_value=mock_cursor)

    # Mock insert_one method
    collection.insert_one = AsyncMock()

    # Mock update_one method
    collection.update_one = AsyncMock()

    # Mock delete_one method
    collection.delete_one = AsyncMock()

    return collection


@pytest.fixture
def test_repository(mock_collection):
    """Create a test repository."""
    repo = MongoDBRepository(mock_collection)
    repo._model_class = MockTestModel
    return repo


@pytest.mark.asyncio
async def test_convert_to_model(test_repository):
    """Test converting MongoDB document to model."""
    # Test with valid document
    doc = {"name": "test", "value": 42}
    model = test_repository._convert_to_model(doc)
    assert isinstance(model, MockTestModel)
    assert model.name == "test"
    assert model.value == 42

    # Test with None document
    with pytest.raises(ValueError, match="Document cannot be None"):
        test_repository._convert_to_model(None)


@pytest.mark.asyncio
async def test_find_by_id(test_repository, mock_collection):
    """Test finding document by ID."""
    # Mock the find_one method to return a document
    doc_id = "507f1f77bcf86cd799439011"
    mock_collection.find_one.return_value = {"_id": ObjectId(doc_id), "name": "test", "value": 42}

    # Call the method
    result = await test_repository.find_by_id(doc_id)

    # Verify the result
    assert isinstance(result, MockTestModel)
    assert result.name == "test"
    assert result.value == 42

    # Verify the find_one method was called with the correct arguments
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(doc_id)})

    # Test with non-existent ID
    mock_collection.find_one.reset_mock()
    mock_collection.find_one.return_value = None

    result = await test_repository.find_by_id(doc_id)
    assert result is None


@pytest.mark.asyncio
async def test_find_all(test_repository, mock_collection):
    """Test finding all documents."""
    # Mock the cursor.to_list method to return documents
    mock_cursor = mock_collection.find.return_value
    mock_cursor.to_list.return_value = [
        {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "test1", "value": 1},
        {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "test2", "value": 2}
    ]

    # Call the method
    results = await test_repository.find_all()

    # Verify the results
    assert len(results) == 2
    assert all(isinstance(result, MockTestModel) for result in results)
    assert results[0].name == "test1"
    assert results[0].value == 1
    assert results[1].name == "test2"
    assert results[1].value == 2

    # Verify the find method was called with no arguments
    mock_collection.find.assert_called_once_with()
    mock_cursor.to_list.assert_called_once_with(None)


@pytest.mark.asyncio
async def test_insert(test_repository, mock_collection):
    """Test inserting a document."""
    # Mock the insert_one method to return a result with inserted_id
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId("507f1f77bcf86cd799439011"))

    # Create a model to insert
    model = MockTestModel(name="test", value=42)

    # Call the method
    result = await test_repository.insert(model)

    # Verify the result
    assert result == "507f1f77bcf86cd799439011"

    # Verify the insert_one method was called with the correct arguments
    mock_collection.insert_one.assert_called_once()
    call_args = mock_collection.insert_one.call_args[0][0]
    assert call_args["name"] == "test"
    assert call_args["value"] == 42


@pytest.mark.asyncio
async def test_update(test_repository, mock_collection):
    """Test updating a document."""
    # Mock the update_one method to return a result with modified_count
    doc_id = "507f1f77bcf86cd799439011"

    # Test successful update
    mock_collection.update_one.return_value = MagicMock(modified_count=1)

    # Create a model to update
    model = MockTestModel(name="updated", value=99)

    # Call the method
    result = await test_repository.update(doc_id, model)

    # Verify the result
    assert result is True

    # Verify the update_one method was called with the correct arguments
    mock_collection.update_one.assert_called_once()
    filter_arg = mock_collection.update_one.call_args[0][0]
    update_arg = mock_collection.update_one.call_args[0][1]
    assert filter_arg == {"_id": ObjectId(doc_id)}
    assert update_arg["$set"]["name"] == "updated"
    assert update_arg["$set"]["value"] == 99

    # Test unsuccessful update
    mock_collection.update_one.reset_mock()
    mock_collection.update_one.return_value = MagicMock(modified_count=0)

    result = await test_repository.update(doc_id, model)
    assert result is False


@pytest.mark.asyncio
async def test_delete(test_repository, mock_collection):
    """Test deleting a document."""
    # Mock the delete_one method to return a result with deleted_count
    doc_id = "507f1f77bcf86cd799439011"

    # Test successful delete
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)

    # Call the method
    result = await test_repository.delete(doc_id)

    # Verify the result
    assert result is True

    # Verify the delete_one method was called with the correct arguments
    mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(doc_id)})

    # Test unsuccessful delete
    mock_collection.delete_one.reset_mock()
    mock_collection.delete_one.return_value = MagicMock(deleted_count=0)

    result = await test_repository.delete(doc_id)
    assert result is False
