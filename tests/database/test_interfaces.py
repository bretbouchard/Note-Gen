"""Tests for database interfaces."""
import pytest
from typing import Optional, List, Dict, Any
from note_gen.database.interfaces import Repository


# Create a concrete implementation of the Repository interface for testing
class MockTestRepository(Repository[str]):
    """Test implementation of Repository interface."""

    def __init__(self):
        self.data = {}  # Simple in-memory storage

    async def find_one(self, id: str) -> Optional[str]:
        """Retrieve a single document by ID."""
        return self.data.get(id)

    async def find_many(self, filter_dict: Dict[str, Any]) -> List[str]:
        """Retrieve multiple documents matching the filter."""
        # Simple implementation that checks if filter values are in the document
        results = []
        for id, value in self.data.items():
            match = True
            for k, v in filter_dict.items():
                if k == "id" and v != id:
                    match = False
                    break
                if k == "value" and v != value:
                    match = False
                    break
            if match:
                results.append(value)
        return results

    async def create(self, document: str) -> str:
        """Create a new document."""
        id = f"id_{len(self.data) + 1}"
        self.data[id] = document
        return document

    async def update(self, id: str, document: str) -> Optional[str]:
        """Update an existing document."""
        if id in self.data:
            self.data[id] = document
            return document
        return None

    async def delete(self, id: str) -> bool:
        """Delete a document by ID."""
        if id in self.data:
            del self.data[id]
            return True
        return False


@pytest.mark.asyncio
async def test_repository_interface():
    """Test the Repository interface with a concrete implementation."""
    repo = MockTestRepository()

    # Test create
    doc1 = await repo.create("Document 1")
    assert doc1 == "Document 1"

    doc2 = await repo.create("Document 2")
    assert doc2 == "Document 2"

    # Test find_one
    found = await repo.find_one("id_1")
    assert found == "Document 1"

    not_found = await repo.find_one("non_existent")
    assert not_found is None

    # Test find_many
    all_docs = await repo.find_many({})
    assert len(all_docs) == 2
    assert "Document 1" in all_docs
    assert "Document 2" in all_docs

    # Test update
    updated = await repo.update("id_1", "Updated Document 1")
    assert updated == "Updated Document 1"

    found_after_update = await repo.find_one("id_1")
    assert found_after_update == "Updated Document 1"

    update_non_existent = await repo.update("non_existent", "New Document")
    assert update_non_existent is None

    # Test delete
    deleted = await repo.delete("id_1")
    assert deleted is True

    found_after_delete = await repo.find_one("id_1")
    assert found_after_delete is None

    delete_non_existent = await repo.delete("non_existent")
    assert delete_non_existent is False
