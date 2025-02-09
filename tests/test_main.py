import pytest
from fastapi.testclient import TestClient
from main import app
from src.note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.database.db import init_db, close_mongo_connection
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern
import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import uuid

logger = logging.getLogger(__name__)

async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create indexes for collections."""
    try:
        # Drop existing indexes first
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
    # Check if collections are empty
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

@pytest.fixture
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop

@pytest.fixture(autouse=True)
async def setup_test_db():
    """Setup test database with proper event loop handling."""
    # Initialize test database
    db = await init_db()
    
    # Clear test database
    await db.chord_progressions.delete_many({})
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    
    yield db
    
    # Cleanup
    await db.chord_progressions.delete_many({})
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    await close_mongo_connection()

@pytest.mark.asyncio
async def test_startup_imports_presets_when_empty(setup_test_db):
    """Test that presets are imported when collections are empty."""
    logger.info("Starting test: test_startup_imports_presets_when_empty")
    db = setup_test_db
    
    try:
        # Run startup event with test database
        await ensure_indexes(db)
        await import_presets_if_empty(db)

        # Verify presets were imported
        assert await db.chord_progressions.count_documents({}) == len(COMMON_PROGRESSIONS)
        assert await db.note_patterns.count_documents({}) == len(NOTE_PATTERNS)
        assert await db.rhythm_patterns.count_documents({}) == len(RHYTHM_PATTERNS)
        logger.info("Test completed successfully.")
    except Exception as e:
        logger.error(f"Error in test_startup_imports_presets_when_empty: {e}")
        raise

@pytest.mark.asyncio
async def test_startup_skips_import_when_not_empty(setup_test_db):
    """Test that presets are not imported when collections have data."""
    db = setup_test_db
    
    try:
        # Add a sample document to each collection
        await db.chord_progressions.insert_one({"name": "test"})
        await db.note_patterns.insert_one({"name": "test"})
        await db.rhythm_patterns.insert_one({"name": "test"})
        
        # Run startup event
        await ensure_indexes(db)
        await import_presets_if_empty(db)
        
        # Verify only our test documents exist
        assert await db.chord_progressions.count_documents({}) == 1
        assert await db.note_patterns.count_documents({}) == 1
        assert await db.rhythm_patterns.count_documents({}) == 1
    except Exception as e:
        logger.error(f"Error in test_startup_skips_import_when_not_empty: {e}")
        raise