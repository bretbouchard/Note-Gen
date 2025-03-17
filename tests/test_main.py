import pytest
from fastapi.testclient import TestClient
from main import app
from src.note_gen.models.presets import Patterns
from src.note_gen.database.db import init_db, get_db_conn
from src.note_gen.models.patterns import ChordProgression , NotePattern, RhythmPattern, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.roman_numeral import RomanNumeral
import os

import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

import uuid

logger = logging.getLogger(__name__)

async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create indexes for collections."""
    try:
        # Drop existing indexes first
        if os.getenv("CLEAR_DB_AFTER_TESTS", "1") == "1":
            await db.chord_progressions.drop_indexes()
            await db.note_patterns.drop_indexes()
            await db.rhythm_patterns.drop_indexes()

        # Create new indexes
        await db.chord_progressions.create_index("name", unique=True)
        await db.note_patterns.create_index("name", unique=True)
        await db.rhythm_patterns.create_index("name", unique=True)
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error ensuring indexes: {str(e)}")
        raise

async def import_presets_if_empty(db: AsyncIOMotorDatabase) -> None:
    """Import presets if collections are empty."""
    from src.note_gen.models.presets import Patterns
    COMMON_PROGRESSIONS = Patterns.common_progressions
    # Check if collections are empty
    if os.getenv("CLEAR_DB_AFTER_TESTS", "1") == "1":
        await db.chord_progressions.delete_many({})
        await db.note_patterns.delete_many({})
        await db.rhythm_patterns.delete_many({})

    if await db.chord_progressions.count_documents({}) == 0:
        # Convert chord progressions to model objects
        chord_progressions = []
        for name, progression in COMMON_PROGRESSIONS.items():
            chord_prog = {
                "id": str(uuid.uuid4()),
                "name": name,
                "chords": progression,  # This is already a list of roman numerals
                "key": "C",  # Default key
                "scale_type": "MAJOR",  # Default scale type
                "complexity": 0.5  # Default complexity
            }
            chord_progressions.append(chord_prog)
        await db.chord_progressions.insert_many(chord_progressions)
        
    if await db.note_patterns.count_documents({}) == 0:
        # Convert note patterns to model objects
        note_patterns = []
        for name, pattern_data in NOTE_PATTERNS.items():
            note_pattern = {
                "id": str(uuid.uuid4()),
                "name": name,
                "pattern_type": "scale",  # Default type
                "description": pattern_data["description"],
                "tags": pattern_data["tags"],
                "complexity": pattern_data["complexity"],
                "data": pattern_data["pattern"]
            }
            note_patterns.append(note_pattern)
        await db.note_patterns.insert_many(note_patterns)
        
    if await db.rhythm_patterns.count_documents({}) == 0:
        # Convert rhythm patterns to model objects
        rhythm_patterns = []
        for name, pattern_data in RHYTHM_PATTERNS.items():
            rhythm_pattern = {
                "id": str(uuid.uuid4()),
                "name": name,
                "pattern_type": "basic",  # Default type
                "description": pattern_data["description"],
                "tags": pattern_data["tags"],
                "complexity": pattern_data["complexity"],
                "data": pattern_data["pattern"],
                "notes": pattern_data["notes"]
            }
            rhythm_patterns.append(rhythm_pattern)
        await db.rhythm_patterns.insert_many(rhythm_patterns)

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
async def setup_test_db():
    """Set up test database."""
    await init_db()
    db = await get_db_conn()
    
    # Clear all collections
    collections = await db.list_collection_names()
    for collection in collections:
        if os.getenv("CLEAR_DB_AFTER_TESTS", "1") == "1":
            await db.get_collection(collection).delete_many({})
    
    # Create indexes
    await ensure_indexes(db)
    
    yield db

@pytest.mark.asyncio
async def test_startup_imports_presets_when_empty(setup_test_db):
    """Test that presets are imported when collections are empty."""
    db = await setup_test_db()
    
    # Import presets
    await import_presets_if_empty(db)
    
    # Verify that collections are not empty
    assert await db.chord_progressions.count_documents({}) > 0
    assert await db.note_patterns.count_documents({}) > 0
    assert await db.rhythm_patterns.count_documents({}) > 0

@pytest.mark.asyncio
async def test_startup_skips_import_when_not_empty(setup_test_db):
    """Test that presets are not imported when collections are not empty."""
    db = await setup_test_db()
    
    # Add a test document to each collection
    test_doc = {"name": "test", "data": "test"}
    await db.chord_progressions.insert_one(test_doc.copy())
    await db.note_patterns.insert_one(test_doc.copy())
    await db.rhythm_patterns.insert_one(test_doc.copy())
    
    # Import presets
    await import_presets_if_empty(db)
    
    # Verify that only our test documents are present
    assert await db.chord_progressions.count_documents({}) == 1
    assert await db.note_patterns.count_documents({}) == 1
    assert await db.rhythm_patterns.count_documents({}) == 1