"""Tests for repository operations."""
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


@pytest.mark.asyncio
async def test_insert_many(test_repository: MongoDBRepository[DBTestModel]):
    """Test inserting multiple documents."""
    models = [
        DBTestModel(name="test1", value=1),
        DBTestModel(name="test2", value=2),
        DBTestModel(name="test3", value=3)
    ]
    
    result = await test_repository.insert_many(models)
    assert len(result) == 3
    
    # Verify all documents were inserted
    count = await test_repository.collection.count_documents({})
    assert count == 3
    
    # Verify we can find each document
    for model in models:
        found = await test_repository.find_one({"name": model.name})
        assert found is not None
        assert found.name == model.name
        assert found.value == model.value


@pytest.mark.asyncio
async def test_find_many(test_repository: MongoDBRepository[DBTestModel]):
    """Test finding multiple documents."""
    # Insert test data
    models = [
        DBTestModel(name="test1", value=1),
        DBTestModel(name="test2", value=2),
        DBTestModel(name="test3", value=3),
        DBTestModel(name="other", value=4)
    ]
    await test_repository.insert_many(models)
    
    # Find documents with name starting with "test"
    results = await test_repository.find_many({"name": {"$regex": "^test"}})
    assert len(results) == 3
    
    # Verify the results
    names = [model.name for model in results]
    assert "test1" in names
    assert "test2" in names
    assert "test3" in names
    assert "other" not in names


@pytest.mark.asyncio
async def test_update_one(test_repository: MongoDBRepository[DBTestModel]):
    """Test updating a document."""
    # Insert test data
    model = DBTestModel(name="test", value=1)
    await test_repository.insert_one(model)
    
    # Update the document
    result = await test_repository.update_one(
        {"name": "test"},
        {"$set": {"value": 2}}
    )
    assert result.modified_count == 1
    
    # Verify the update
    updated = await test_repository.find_one({"name": "test"})
    assert updated is not None
    assert updated.name == "test"
    assert updated.value == 2


@pytest.mark.asyncio
async def test_update_many(test_repository: MongoDBRepository[DBTestModel]):
    """Test updating multiple documents."""
    # Insert test data
    models = [
        DBTestModel(name="test1", value=1),
        DBTestModel(name="test2", value=2),
        DBTestModel(name="other", value=3)
    ]
    await test_repository.insert_many(models)
    
    # Update documents with name starting with "test"
    result = await test_repository.update_many(
        {"name": {"$regex": "^test"}},
        {"$inc": {"value": 10}}
    )
    assert result.modified_count == 2
    
    # Verify the updates
    test1 = await test_repository.find_one({"name": "test1"})
    assert test1 is not None
    assert test1.value == 11
    
    test2 = await test_repository.find_one({"name": "test2"})
    assert test2 is not None
    assert test2.value == 12
    
    other = await test_repository.find_one({"name": "other"})
    assert other is not None
    assert other.value == 3  # Not modified


@pytest.mark.asyncio
async def test_delete_one(test_repository: MongoDBRepository[DBTestModel]):
    """Test deleting a document."""
    # Insert test data
    models = [
        DBTestModel(name="test1", value=1),
        DBTestModel(name="test2", value=2)
    ]
    await test_repository.insert_many(models)
    
    # Delete one document
    result = await test_repository.delete_one({"name": "test1"})
    assert result.deleted_count == 1
    
    # Verify the deletion
    count = await test_repository.collection.count_documents({})
    assert count == 1
    
    remaining = await test_repository.find_one({})
    assert remaining is not None
    assert remaining.name == "test2"


@pytest.mark.asyncio
async def test_delete_many(test_repository: MongoDBRepository[DBTestModel]):
    """Test deleting multiple documents."""
    # Insert test data
    models = [
        DBTestModel(name="test1", value=1),
        DBTestModel(name="test2", value=2),
        DBTestModel(name="other", value=3)
    ]
    await test_repository.insert_many(models)
    
    # Delete documents with name starting with "test"
    result = await test_repository.delete_many({"name": {"$regex": "^test"}})
    assert result.deleted_count == 2
    
    # Verify the deletion
    count = await test_repository.collection.count_documents({})
    assert count == 1
    
    remaining = await test_repository.find_one({})
    assert remaining is not None
    assert remaining.name == "other"


@pytest.mark.asyncio
async def test_count_documents(test_repository: MongoDBRepository[DBTestModel]):
    """Test counting documents."""
    # Insert test data
    models = [
        DBTestModel(name="test1", value=1),
        DBTestModel(name="test2", value=2),
        DBTestModel(name="other", value=3)
    ]
    await test_repository.insert_many(models)
    
    # Count all documents
    count_all = await test_repository.count_documents({})
    assert count_all == 3
    
    # Count documents with name starting with "test"
    count_test = await test_repository.count_documents({"name": {"$regex": "^test"}})
    assert count_test == 2
    
    # Count documents with value > 1
    count_value = await test_repository.count_documents({"value": {"$gt": 1}})
    assert count_value == 2
