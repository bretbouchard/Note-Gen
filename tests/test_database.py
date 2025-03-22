import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.database import get_database
from src.note_gen.database.db import init_db
from src.note_gen.core.constants import COLLECTION_NAMES

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection and initialization."""
    async for db in get_database():
        assert isinstance(db, AsyncIOMotorDatabase)
        await init_db(db)
        
        # Verify all collections exist
        collections = await db.list_collection_names()
        for collection_name in COLLECTION_NAMES.values():
            assert collection_name in collections

        # Verify indexes
        chord_prog_indexes = await db[COLLECTION_NAMES["chord_progressions"]].index_information()
        assert "name_1" in chord_prog_indexes
        
        note_pattern_indexes = await db[COLLECTION_NAMES["note_patterns"]].index_information()
        assert "name_1" in note_pattern_indexes
        
        rhythm_pattern_indexes = await db[COLLECTION_NAMES["rhythm_patterns"]].index_information()
        assert "name_1" in rhythm_pattern_indexes