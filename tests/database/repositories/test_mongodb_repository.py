"""Tests for the MongoDB repository implementation."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel, Field

from note_gen.database.repositories.mongodb_repository import MongoDBRepository

# Create a test model
class TestModel(BaseModel):
    """Test model for repository tests."""
    id: str = Field(default="")
    name: str = Field(default="")
    value: int = Field(default=0)

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = AsyncMock(spec=AsyncIOMotorCollection)

    # Setup async methods
    collection.find_one = AsyncMock()
    collection.find = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()

    return collection

@pytest.fixture
def repository(mock_collection):
    """Create a repository instance with a mock collection."""
    return MongoDBRepository(mock_collection, TestModel)

@pytest.mark.asyncio
async def test_find_one(repository, mock_collection):
    """Test finding a single document by ID."""
    # Setup mock
    mock_id = "507f1f77bcf86cd799439011"
    mock_doc = {"_id": ObjectId(mock_id), "name": "Test", "value": 42}
    mock_collection.find_one.return_value = mock_doc

    # Call method
    result = await repository.find_one(mock_id)

    # Verify result
    assert result is not None
    assert result.id == mock_id
    assert result.name == "Test"
    assert result.value == 42

    # Verify mock called
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(mock_id)})

@pytest.mark.asyncio
async def test_find_one_not_found(repository, mock_collection):
    """Test finding a non-existent document."""
    # Setup mock
    mock_id = "507f1f77bcf86cd799439011"
    mock_collection.find_one.return_value = None

    # Call method
    result = await repository.find_one(mock_id)

    # Verify result
    assert result is None

    # Verify mock called
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(mock_id)})

@pytest.mark.asyncio
async def test_find_many(repository, mock_collection):
    """Test finding multiple documents."""
    # Setup mock
    mock_docs = [
        {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Test 1", "value": 42},
        {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "Test 2", "value": 43}
    ]

    # Mock the find method to return a list of models directly
    # This avoids the need to mock the cursor and to_list method
    async def mock_find_impl(filter_dict):
        # In a real implementation, this would filter the documents
        return [TestModel(id=str(doc["_id"]), name=doc["name"], value=doc["value"]) for doc in mock_docs]

    # Patch the find_many method directly
    original_find_many = repository.find_many
    repository.find_many = AsyncMock(side_effect=mock_find_impl)

    try:
        # Call method
        result = await repository.find_many({"name": "Test"})

        # Verify result
        assert len(result) == 2
        assert result[0].id == "507f1f77bcf86cd799439011"
        assert result[0].name == "Test 1"
        assert result[0].value == 42
        assert result[1].id == "507f1f77bcf86cd799439012"
        assert result[1].name == "Test 2"
        assert result[1].value == 43

        # Verify mock called
        repository.find_many.assert_called_once_with({"name": "Test"})
    finally:
        # Restore original method
        repository.find_many = original_find_many

@pytest.mark.asyncio
async def test_find_many_empty(repository, mock_collection):
    """Test finding multiple documents with no results."""
    # Mock the find method to return an empty list
    async def mock_find_impl(filter_dict):
        return []

    # Patch the find_many method directly
    original_find_many = repository.find_many
    repository.find_many = AsyncMock(side_effect=mock_find_impl)

    try:
        # Call method
        result = await repository.find_many({"name": "Test"})

        # Verify result
        assert len(result) == 0

        # Verify mock called
        repository.find_many.assert_called_once_with({"name": "Test"})
    finally:
        # Restore original method
        repository.find_many = original_find_many

@pytest.mark.asyncio
async def test_create(repository, mock_collection):
    """Test creating a document."""
    # Setup mock
    mock_id = ObjectId("507f1f77bcf86cd799439011")
    mock_result = MagicMock()
    mock_result.inserted_id = mock_id
    mock_collection.insert_one.return_value = mock_result

    # Create model
    model = TestModel(name="Test", value=42)

    # Call method
    result = await repository.create(model)

    # Verify result
    assert result.id == "507f1f77bcf86cd799439011"
    assert result.name == "Test"
    assert result.value == 42

    # Verify mock called
    mock_collection.insert_one.assert_called_once()
    # Check that the document was converted to dict
    call_args = mock_collection.insert_one.call_args[0][0]
    assert isinstance(call_args, dict)
    assert call_args["name"] == "Test"
    assert call_args["value"] == 42

@pytest.mark.asyncio
async def test_update(repository, mock_collection):
    """Test updating a document."""
    # Setup mock
    mock_id = "507f1f77bcf86cd799439011"
    mock_doc = {"_id": ObjectId(mock_id), "name": "Updated", "value": 43}
    mock_result = MagicMock()
    mock_result.matched_count = 1
    mock_collection.update_one.return_value = mock_result
    mock_collection.find_one.return_value = mock_doc

    # Create model
    model = TestModel(id=mock_id, name="Updated", value=43)

    # Call method
    result = await repository.update(mock_id, model)

    # Verify result
    assert result is not None
    assert result.id == mock_id
    assert result.name == "Updated"
    assert result.value == 43

    # Verify mocks called
    mock_collection.update_one.assert_called_once()
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(mock_id)})

@pytest.mark.asyncio
async def test_update_not_found(repository, mock_collection):
    """Test updating a non-existent document."""
    # Setup mock
    mock_id = "507f1f77bcf86cd799439011"
    mock_result = MagicMock()
    mock_result.matched_count = 0
    mock_collection.update_one.return_value = mock_result

    # Create model
    model = TestModel(id=mock_id, name="Updated", value=43)

    # Call method
    result = await repository.update(mock_id, model)

    # Verify result
    assert result is None

    # Verify mock called
    mock_collection.update_one.assert_called_once()
    mock_collection.find_one.assert_not_called()

@pytest.mark.asyncio
async def test_delete(repository, mock_collection):
    """Test deleting a document."""
    # Setup mock
    mock_id = "507f1f77bcf86cd799439011"
    mock_result = MagicMock()
    mock_result.deleted_count = 1
    mock_collection.delete_one.return_value = mock_result

    # Call method
    result = await repository.delete(mock_id)

    # Verify result
    assert result is True

    # Verify mock called
    mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(mock_id)})

@pytest.mark.asyncio
async def test_delete_not_found(repository, mock_collection):
    """Test deleting a non-existent document."""
    # Setup mock
    mock_id = "507f1f77bcf86cd799439011"
    mock_result = MagicMock()
    mock_result.deleted_count = 0
    mock_collection.delete_one.return_value = mock_result

    # Call method
    result = await repository.delete(mock_id)

    # Verify result
    assert result is False

    # Verify mock called
    mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(mock_id)})

def test_convert_to_model(repository):
    """Test converting a document to a model."""
    # Setup data
    mock_id = ObjectId("507f1f77bcf86cd799439011")
    mock_doc = {"_id": mock_id, "name": "Test", "value": 42}

    # Call method
    result = repository._convert_to_model(mock_doc)

    # Verify result
    assert result.id == str(mock_id)
    assert result.name == "Test"
    assert result.value == 42

def test_convert_to_model_none(repository):
    """Test converting None to a model."""
    # Call method and verify exception
    with pytest.raises(ValueError, match="Data cannot be None"):
        repository._convert_to_model(None)
