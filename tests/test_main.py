import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from main import app, startup_event, ensure_indexes, import_presets_if_empty
from note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from note_gen.import_presets import client, db

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    # Use a test database
    global db
    db = client["test_note_gen"]
    
    # Clear test database
    db.chord_progressions.delete_many({})
    db.note_patterns.delete_many({})
    db.rhythm_patterns.delete_many({})
    
    yield db
    
    # Cleanup
    client.drop_database('test_note_gen')

@pytest.mark.asyncio
async def test_startup_imports_presets_when_empty(setup_test_db):
    """Test that presets are imported when collections are empty."""
    # Run startup event with test database
    ensure_indexes(setup_test_db)
    await import_presets_if_empty(setup_test_db)

    # Verify presets were imported
    assert setup_test_db.chord_progressions.count_documents({}) == len(COMMON_PROGRESSIONS)
    assert setup_test_db.note_patterns.count_documents({}) == len(NOTE_PATTERNS)
    assert setup_test_db.rhythm_patterns.count_documents({}) == len(RHYTHM_PATTERNS)

@pytest.mark.asyncio
async def test_startup_skips_import_when_not_empty(setup_test_db):
    """Test that presets are not imported when collections have data."""
    # Add some test data
    setup_test_db.chord_progressions.insert_one({"name": "test", "progression": ["I", "IV", "V"]})
    setup_test_db.note_patterns.insert_one({"name": "test", "pattern": [0, 2, 4]})
    setup_test_db.rhythm_patterns.insert_one({
        "name": "test",
        "pattern": {
            "notes": [],
            "time_signature": "4/4",
            "swing_enabled": False
        }
    })
    
    # Get initial counts
    initial_chord_count = setup_test_db.chord_progressions.count_documents({})
    initial_note_count = setup_test_db.note_patterns.count_documents({})
    initial_rhythm_count = setup_test_db.rhythm_patterns.count_documents({})
    
    # Run startup event
    await startup_event()
    
    # Verify counts haven't changed
    assert setup_test_db.chord_progressions.count_documents({}) == initial_chord_count
    assert setup_test_db.note_patterns.count_documents({}) == initial_note_count
    assert setup_test_db.rhythm_patterns.count_documents({}) == initial_rhythm_count
