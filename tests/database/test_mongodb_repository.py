"""Test MongoDB repository implementation."""
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from src.note_gen.database.repository import MongoDBRepository

class TestModel(BaseModel):
    """Test model for repository tests."""
    name: str
    value: int

    model_config = {
        "arbitrary_types_allowed": True
    }

@pytest_asyncio.fixture
async def test_repository(test_db: AsyncIOMotorDatabase) -> MongoDBRepository[TestModel]:
    """Create a test repository."""
    repo = MongoDBRepository[TestModel](test_db, "test_collection", model_type=TestModel)
    await repo.collection.drop()  # Ensure clean state
    return repo

async def test_insert_and_find(test_repository: MongoDBRepository[TestModel]):
    """Test inserting and finding a document."""
    model = TestModel(name="test", value=1)
    await test_repository.insert_one(model)
    found = await test_repository.find_one({"name": "test"})
    assert found is not None
    assert found.name == "test"
    assert found.value == 1
