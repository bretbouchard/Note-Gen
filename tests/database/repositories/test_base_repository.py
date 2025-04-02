"""Tests for base repository implementation."""
import pytest
import pytest_asyncio
from typing import Dict, Any, Optional, List
from unittest.mock import MagicMock, AsyncMock
from motor.motor_asyncio import AsyncIOMotorCollection
from src.note_gen.database.repositories.base import BaseRepository


# Create a concrete implementation of BaseRepository for testing
class MockTestRepository(BaseRepository[str]):
    """Test implementation of BaseRepository."""

    async def find_one(self, id: str) -> Optional[str]:
        """Find a single document by ID."""
        doc = await self.collection.find_one({"_id": id})
        return self._convert_to_model(doc) if doc else None

    async def find_many(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[str]:
        """Find multiple documents matching filter criteria."""
        return await super().find_many(filter_dict)

    async def create(self, document: str) -> str:
        """Create a new document."""
        result = await self.collection.insert_one({"value": document})
        return document

    async def update(self, id: str, document: str) -> Optional[str]:
        """Update an existing document."""
        result = await self.collection.update_one(
            {"_id": id},
            {"$set": {"value": document}}
        )
        if result.modified_count > 0:
            return document
        return None

    async def delete(self, id: str) -> bool:
        """Delete a document by ID."""
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0

    def _convert_to_model(self, data: Dict[str, Any]) -> str:
        """Convert dictionary data to model instance."""
        if data is None:
            raise ValueError("Document cannot be None")
        return data.get("value", "")


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
    return MockTestRepository(mock_collection)


@pytest.mark.asyncio
async def test_find_one(test_repository, mock_collection):
    """Test finding a single document by ID."""
    # Mock the find_one method to return a document
    mock_collection.find_one.return_value = {"_id": "123", "value": "test_value"}

    # Call the method
    result = await test_repository.find_one("123")

    # Verify the result
    assert result == "test_value"

    # Verify the find_one method was called with the correct arguments
    mock_collection.find_one.assert_called_once_with({"_id": "123"})

    # Test with non-existent ID
    mock_collection.find_one.reset_mock()
    mock_collection.find_one.return_value = None

    result = await test_repository.find_one("456")
    assert result is None


@pytest.mark.asyncio
async def test_find_many(test_repository, mock_collection):
    """Test finding multiple documents."""
    # Mock the cursor.to_list method to return documents
    mock_cursor = mock_collection.find.return_value
    mock_cursor.to_list.return_value = [
        {"_id": "123", "value": "value1"},
        {"_id": "456", "value": "value2"}
    ]

    # Call the method with a filter
    results = await test_repository.find_many({"status": "active"})

    # Verify the results
    assert len(results) == 2
    assert "value1" in results
    assert "value2" in results

    # Verify the find method was called with the correct arguments
    mock_collection.find.assert_called_once_with({"status": "active"})
    mock_cursor.to_list.assert_called_once_with(length=None)

    # Call the method without a filter
    mock_collection.find.reset_mock()
    mock_cursor.to_list.reset_mock()

    results = await test_repository.find_many()

    # Verify the find method was called with an empty filter
    mock_collection.find.assert_called_once_with({})


@pytest.mark.asyncio
async def test_create(test_repository, mock_collection):
    """Test creating a document."""
    # Mock the insert_one method to return a result with inserted_id
    mock_collection.insert_one.return_value = MagicMock(inserted_id="123")

    # Call the method
    result = await test_repository.create("test_document")

    # Verify the result
    assert result == "test_document"

    # Verify the insert_one method was called with the correct arguments
    mock_collection.insert_one.assert_called_once_with({"value": "test_document"})


@pytest.mark.asyncio
async def test_update(test_repository, mock_collection):
    """Test updating a document."""
    # Mock the update_one method to return a result with modified_count
    mock_collection.update_one.return_value = MagicMock(modified_count=1)

    # Call the method
    result = await test_repository.update("123", "updated_document")

    # Verify the result
    assert result == "updated_document"

    # Verify the update_one method was called with the correct arguments
    mock_collection.update_one.assert_called_once_with(
        {"_id": "123"},
        {"$set": {"value": "updated_document"}}
    )

    # Test unsuccessful update
    mock_collection.update_one.reset_mock()
    mock_collection.update_one.return_value = MagicMock(modified_count=0)

    result = await test_repository.update("456", "updated_document")
    assert result is None


@pytest.mark.asyncio
async def test_delete(test_repository, mock_collection):
    """Test deleting a document."""
    # Mock the delete_one method to return a result with deleted_count
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)

    # Call the method
    result = await test_repository.delete("123")

    # Verify the result
    assert result is True

    # Verify the delete_one method was called with the correct arguments
    mock_collection.delete_one.assert_called_once_with({"_id": "123"})

    # Test unsuccessful delete
    mock_collection.delete_one.reset_mock()
    mock_collection.delete_one.return_value = MagicMock(deleted_count=0)

    result = await test_repository.delete("456")
    assert result is False


def test_convert_to_model(test_repository):
    """Test converting dictionary to model."""
    # Test with valid document
    doc = {"_id": "123", "value": "test_value"}
    result = test_repository._convert_to_model(doc)
    assert result == "test_value"

    # Test with document missing value
    doc = {"_id": "123"}
    result = test_repository._convert_to_model(doc)
    assert result == ""

    # Test with None document
    with pytest.raises(ValueError, match="Document cannot be None"):
        test_repository._convert_to_model(None)
