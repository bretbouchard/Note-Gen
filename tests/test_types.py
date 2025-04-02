import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase

@pytest.mark.asyncio
async def test_db_connection_types(test_db):
    """Test database connection types."""
    assert isinstance(test_db, AsyncIOMotorDatabase)
    
    # Test basic operations
    collection = test_db["test_collection"]
    await collection.insert_one({"test": "data"})
    result = await collection.find_one({"test": "data"})
    assert result is not None
    assert result["test"] == "data"
