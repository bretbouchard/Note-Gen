"""Tests for MongoDB repository implementation."""

import pytest
from pydantic import BaseModel, ConfigDict
from src.note_gen.database.repositories.mongodb import MongoDBRepository
from src.note_gen.database.exceptions import DuplicateKeyError

# Add __test__ = False to indicate this is not a test class
class TestModel(BaseModel):
    """Test model for repository testing."""
    name: str
    value: int

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )
    
    __test__ = False  # Add this line to exclude from test collection

@pytest.fixture
def test_model():
    return TestModel(name="test", value=1)  # Initialize with values

@pytest.fixture
async def repo(mongodb_client):
    """Create a repository instance with the test collection."""
    return MongoDBRepository(
        client=mongodb_client,
        database="note_gen_db_dev_db",
        collection="test_collection"
    )

async def test_insert_and_find(repo):
    test_doc = TestModel(name="test", value=1)
    inserted = await repo.insert(test_doc.model_dump())
    assert inserted["name"] == "test"
    assert inserted["value"] == 1
    
    found = await repo.find_one({"name": "test"})
    assert found["value"] == 1

async def test_update(repo):
    test_doc = TestModel(name="test", value=1)
    inserted = await repo.insert(test_doc.model_dump())
    
    updated = await repo.update({"_id": inserted["_id"]}, {"value": 2})
    assert updated["value"] == 2

async def test_delete(repo):
    test_doc = TestModel(name="test", value=1)
    inserted = await repo.insert(test_doc.model_dump())
    
    deleted = await repo.delete({"_id": inserted["_id"]})
    assert deleted is True
    
    found = await repo.find_one({"_id": inserted["_id"]})
    assert found is None

async def test_duplicate_key_error(repo):
    test_doc = TestModel(name="test", value=1)
    doc_dict = test_doc.model_dump()
    doc_dict["_id"] = "test_id"
    
    await repo.insert(doc_dict)
    with pytest.raises(DuplicateKeyError):
        await repo.insert(doc_dict)
