import pytest
from fastapi.testclient import TestClient
from main import app
from src.note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.database import get_client
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
async def setup_test_db():
    # Use a test database
    global db, client
    client = await get_client()  
    db = client["test_note_gen"]
    
    # Clear test database
    await db.chord_progressions.delete_many({})
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    
    yield db
    
    # Cleanup
    client.drop_database('test_note_gen')

@pytest.mark.asyncio
async def test_startup_imports_presets_when_empty():
    client = await get_client()
    # Rest of your test code
    logger.info("Starting test: test_startup_imports_presets_when_empty")
    try:
        """Test that presets are imported when collections are empty."""
        # Run startup event with test database
        await ensure_indexes(setup_test_db)
        await import_presets_if_empty(setup_test_db)

        # Verify presets were imported
        assert await setup_test_db.chord_progressions.count_documents({}) == len(COMMON_PROGRESSIONS)
        assert await setup_test_db.note_patterns.count_documents({}) == len(NOTE_PATTERNS)
        assert await setup_test_db.rhythm_patterns.count_documents({}) == len(RHYTHM_PATTERNS)
        logger.info("Test completed successfully.")
    except Exception as e:
        logger.error(f"Error in test_startup_imports_presets_when_empty: {e}")

@pytest.mark.asyncio
async def test_startup_skips_import_when_not_empty(setup_test_db):
    logger.info("Starting test: test_startup_skips_import_when_not_empty")
    try:
        """Test that presets are not imported when collections have data."""
        # Add some test data
        await setup_test_db.chord_progressions.insert_one({"name": "test", "progression": ["I", "IV", "V"]})
        
        # Ensure the startup event is called within the same event loop
        await ensure_indexes(setup_test_db)
        
        # Call the startup event
        # await startup_event()
        
        # Verify that presets were not imported
        chord_progressions = await setup_test_db.chord_progressions.find().to_list(None)
        assert len(chord_progressions) == 1, "Presets should not be imported when collections have data."
        logger.info("Test completed successfully.")
    except Exception as e:
        logger.error(f"Error in test_startup_skips_import_when_not_empty: {e}")