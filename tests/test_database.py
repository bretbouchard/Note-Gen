import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.database.db import get_db_conn as get_database  # Fix import
from src.note_gen.database.db import init_db
from src.note_gen.core.constants import COLLECTION_NAMES

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection and initialization."""
    # Test connection
    db = await get_database()
    assert isinstance(db, AsyncIOMotorDatabase)
    
    # Initialize database
    await init_db(db)
    
    # Verify collections
    collections = await db.list_collection_names()
    for collection_name in COLLECTION_NAMES.values():
        assert collection_name in collections
        
        # Verify collection indexes
        indexes = await db[collection_name].index_information()
        assert len(indexes) > 0  # At least _id index should exist
        
    # Test basic operations
    test_collection = db[COLLECTION_NAMES['chord_progressions']]
    test_doc = {"test": "data"}
    
    # Insert
    result = await test_collection.insert_one(test_doc)
    assert result.inserted_id is not None
    
    # Find
    found = await test_collection.find_one({"test": "data"})
    assert found is not None
    assert found["test"] == "data"
    
    # Cleanup
    await test_collection.delete_one({"test": "data"})
