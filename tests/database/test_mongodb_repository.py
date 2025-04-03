"""Test MongoDB repository implementation."""
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from note_gen.database.repository import MongoDBRepository
from tests.database.test_models import DBTestModel

@pytest_asyncio.fixture
async def test_repository(test_db: AsyncIOMotorDatabase) -> MongoDBRepository[DBTestModel]:
    """Create a test repository."""
    repo = MongoDBRepository[DBTestModel](test_db, "test_collection", model_type=DBTestModel)
    await repo.collection.drop()  # Ensure clean state
    return repo

async def test_insert_and_find(test_repository: MongoDBRepository[DBTestModel]):
    """Test inserting and finding a document."""
    model = DBTestModel(name="test", value=1)
    await test_repository.insert_one(model)
    found = await test_repository.find_one({"name": "test"})
    assert found is not None
    assert found.name == "test"
    assert found.value == 1
