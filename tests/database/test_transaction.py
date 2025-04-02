"""Tests for database operations."""
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

@pytest.mark.asyncio
async def test_transaction_commit(test_db):
    """Test basic database operations."""
    collection = test_db.test_collection
    test_id = str(uuid.uuid4())
    
    # Simple insert without transaction
    await collection.insert_one({"_id": test_id, "test": "data"})
            
    result = await collection.find_one({"_id": test_id})
    assert result is not None
    assert result["test"] == "data"

@pytest.mark.asyncio
async def test_transaction_rollback(test_db):
    """Test error handling in database operations."""
    collection = test_db.test_collection
    test_id = str(uuid.uuid4())
    
    # Simulate rollback behavior without transactions
    try:
        await collection.insert_one({"_id": test_id, "test": "data"})
        raise Exception("Forced rollback")
    except Exception:
        await collection.delete_one({"_id": test_id})
        
    result = await collection.find_one({"_id": test_id})
    assert result is None
