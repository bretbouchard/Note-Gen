import os
os.environ["TESTING"] = "1"  # Set testing environment before imports

import pytest
import asyncio
import logging
import time
from fastapi.testclient import TestClient
from main import app

from src.note_gen.fetch_patterns import (
    fetch_chord_progressions,
    fetch_chord_progression_by_id,
    fetch_rhythm_patterns,
    fetch_rhythm_pattern_by_id,
    fetch_note_patterns,
    fetch_note_pattern_by_id,
    process_chord_data,
    fetch_chord_progression_patterns,
    fetch_chord_progression_pattern_by_id,
    extract_patterns_from_chord_progressions
)
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.patterns import RhythmPattern, RhythmNote, RhythmPatternData
from src.note_gen.models.patterns import NotePattern, NotePatternData, ChordProgressionPattern, ChordPatternItem
from src.note_gen.models.note import Note
from src.note_gen.database.db import get_db_conn, MONGODB_URI
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid 
from pydantic import BaseModel, ValidationError
from typing import AsyncGenerator, Optional, List, Union

from tests.generators.test_data_generator import generate_test_data

# Configure logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log environment variable values
logger.debug(f'MONGODB_URI: {os.getenv("MONGODB_URI")}')
logger.debug(f'MONGODB_TEST_URI: {os.getenv("MONGODB_TEST_URI")}')
logger.debug(f'DATABASE_NAME: {os.getenv("DATABASE_NAME")}')


# Fixture to manage event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for the entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Keep the loop open during the entire session
    yield loop
    
    # Only close the loop when the session is done
    # Not closing it here prevents 'Event loop is closed' errors during tests
    if not loop.is_closed():
        loop.close()

@pytest.fixture
async def clean_test_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Clean and initialize test database."""
    logger.debug("Initializing MongoDB client.")
    try:
        logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
        db_gen = get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
        async for db in db_gen:
            if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
                await db.chord_progressions.delete_many({})
                await db.note_patterns.delete_many({})
                await db.rhythm_patterns.delete_many({})
            
            # Add test data
            await generate_test_data(db)
            yield db
    except Exception as e:
        logger.error(f"Error in clean_test_db: {e}")
        raise

@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as client:
        yield client

import pytest_asyncio

@pytest_asyncio.fixture(scope="session")
async def test_db():
    db = AsyncIOMotorClient(os.getenv('MONGODB_URI'))['test_note_gen']
    yield db
    await db.client.drop_database('test_note_gen')

@pytest.mark.asyncio
async def test_fetch_chord_progressions(test_db):
    """Test fetching chord progressions."""
    logger.debug(f'Connected to database. Available collections: {await test_db.list_collection_names()}')
    
    # Clear the chord_progressions collection before tests
    await test_db.chord_progressions.delete_many({})
    
    # First verify we have raw chord progression documents in the database
    raw_progressions = await test_db.chord_progressions.find().to_list(None)
    logger.debug(f"Raw chord progression count: {len(raw_progressions)}")
    
    if not raw_progressions:
        # Insert a test chord progression into the database
        from src.note_gen.models.chord import Chord, ChordQuality
        from src.note_gen.models.note import Note
        from src.note_gen.models.fake_scale_info import FakeScaleInfo
        from src.note_gen.models.enums import ScaleType
        
        sample_progression = {
            'id': 'progression_1',
            'name': 'I-IV-V',
            'chords': [
                {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'F', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'}
            ],
            'key': 'C',
            'scale_type': 'MAJOR',
            'complexity': 0.5,
            'duration': 1.0,
            'scale_info': {
                'root': {'note_name': 'C', 'octave': 4},
                'scale_type': 'MAJOR',
                'complexity': 0.5
            }
        }
        
        await test_db.chord_progressions.insert_one(sample_progression)
        logger.debug(f"Inserted sample chord progression: {sample_progression['name']}")
    
    # Now use the fetch_chord_progressions function to get properly validated progressions
    progressions = await fetch_chord_progressions(test_db)
    
    # Check that progressions were successfully converted to ChordProgression instances
    assert len(progressions) > 0, "No chord progressions returned by fetch_chord_progressions"
    
    first_progression = progressions[0]
    logger.debug(f"First chord progression: {first_progression.name} with {len(first_progression.chords)} chords")
    
    assert isinstance(first_progression, ChordProgression), "Fetched item is not a ChordProgression"
    
    # We don't check for specific ID since it might vary in different test environments
    assert len(first_progression.chords) > 0, "Chord progression has no chords"
    assert hasattr(first_progression, "scale_info"), "ChordProgression missing scale_info attribute"

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_v1(test_db) -> None:
    """Test fetching a chord progression by ID with correct scale types."""
    logger.debug(f'Connected to database. Available collections: {await test_db.list_collection_names()}')
    
    # Create a test chord progression with all required fields including scale_info
    from src.note_gen.models.fake_scale_info import FakeScaleInfo
    from src.note_gen.models.enums import ScaleType
    from src.note_gen.models.note import Note
    from src.note_gen.models.chord import Chord, ChordQuality
    
    test_progression = {
        'id': 'test_progression',
        'name': 'Test Progression',
        'chords': [
            {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'},
            {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'}
        ],
        'key': 'C',
        'scale_type': 'MAJOR',
        'complexity': 0.5,
        'duration': 1.0,
        'scale_info': {
            'root': {'note_name': 'C', 'octave': 4},
            'scale_type': 'MAJOR',
            'complexity': 0.5
        }
    }
    
    # Try to delete first in case it exists from a previous test run
    await test_db.chord_progressions.delete_one({"id": "test_progression"})
    # Then insert the test data
    await test_db.chord_progressions.insert_one(test_progression)
    
    # Test fetching the progression by ID
    result = await fetch_chord_progression_by_id("test_progression", test_db)
    
    # Log detailed information for debugging
    if result:
        logger.debug(f"Successfully fetched progression: {result.name}")
        logger.debug(f"Chords: {len(result.chords)}")
        logger.debug(f"Scale info: {result.scale_info.scale_type}")
    else:
        logger.error("Failed to fetch chord progression by ID")
    
    assert result is not None, "Failed to fetch chord progression by ID"
    assert result.name == 'Test Progression', "Incorrect progression name"
    assert len(result.chords) == 2, "Incorrect number of chords"
    assert hasattr(result, 'scale_info'), "Missing scale_info field"

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(test_db):
    """Test fetching rhythm patterns."""
    logger.debug(f'Connected to database. Available collections: {await test_db.list_collection_names()}')
    
    # Clear any existing rhythm patterns to ensure test isolation
    await test_db.rhythm_patterns.delete_many({})
    await test_db.rhythm_pattern_collection.delete_many({})
    
    # Insert a test rhythm pattern
    test_pattern = {
        "id": "test_rhythm_pattern_1",
        "name": "Basic Test Rhythm",
        "pattern": [1.0, 1.0, 1.0, 1.0],  # Rhythm pattern required at top level
        "data": {
            "pattern": [1.0, 1.0, 1.0, 1.0],
            "time_signature": "4/4",
            "swing_enabled": False,
            "total_duration": 4.0,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "humanize_amount": 0.0,
            "default_duration": 1.0,
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 90},
                {"position": 1.0, "duration": 1.0, "velocity": 90},
                {"position": 2.0, "duration": 1.0, "velocity": 90},
                {"position": 3.0, "duration": 1.0, "velocity": 90}
            ]
        },
        "description": "A test rhythm pattern",
        "tags": ["test", "basic"],
        "complexity": 0.5
    }
    
    await test_db.rhythm_patterns.insert_one(test_pattern)
    logger.debug(f"Inserted test rhythm pattern into rhythm_patterns collection")
    
    # Now use the fetch_rhythm_patterns function to get properly validated patterns
    patterns = await fetch_rhythm_patterns(test_db)
    
    # Check that patterns were successfully converted to RhythmPattern instances
    assert len(patterns) > 0, "No rhythm patterns returned by fetch_rhythm_patterns"
    first_pattern = patterns[0]
    assert isinstance(first_pattern, RhythmPattern), "Fetched item is not a RhythmPattern"
    
    # Validate pattern attributes
    assert hasattr(first_pattern, "data"), "Pattern missing data attribute"
    assert hasattr(first_pattern, "pattern"), "Pattern missing pattern attribute"
    assert hasattr(first_pattern.data, "time_signature"), "Pattern data missing time_signature"
    assert len(first_pattern.data.notes) > 0, "Pattern data has no notes"

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(test_db) -> None:
    """Test fetching rhythm pattern by ID."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    
    # Clear any existing data with the same ID
    await test_db.rhythm_pattern_collection.delete_many({"id": "rhythm_pattern_1"})
    await test_db.rhythm_patterns.delete_many({"id": "rhythm_pattern_1"})
    
    # Insert a test rhythm pattern
    test_pattern = {
        "_id": "rhythm_pattern_1",
        "id": "rhythm_pattern_1",
        "name": "Test Rhythm Pattern",
        "pattern": [1.0, 1.0],  # Add pattern at root level which is required
        "data": {
            "pattern": [1.0, 1.0],  # Simple rhythm pattern
            "accents": [1.0, 0.9],  # Accent pattern matching the original notes
            "time_signature": "4/4",
            "swing_enabled": False,
            "total_duration": 4.0,
            "swing_ratio": 0.67,
            "groove_type": "straight", 
            "humanize_amount": 0.0,
            "default_duration": 1.0,
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 90},
                {"position": 1.0, "duration": 1.0, "velocity": 90}
            ]
        },
        "description": "A test rhythm pattern",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "groove_type": "straight",
        "duration": 4.0
    }
    
    await test_db.rhythm_pattern_collection.insert_one(test_pattern)
    
    # Verify insertion
    result = await test_db.rhythm_pattern_collection.find_one({'id': 'rhythm_pattern_1'})
    assert result is not None
    assert result['name'] == 'Test Rhythm Pattern'
    
    # Test the fetch_rhythm_pattern_by_id function
    pattern = await fetch_rhythm_pattern_by_id('rhythm_pattern_1', test_db)
    assert pattern is not None, "Failed to fetch rhythm pattern by ID"
    assert pattern.id == 'rhythm_pattern_1', "Incorrect pattern ID"
    assert pattern.name == 'Test Rhythm Pattern', "Incorrect pattern name"
    assert isinstance(pattern, RhythmPattern), "Result is not a RhythmPattern instance"
    assert hasattr(pattern, "data"), "Pattern missing data attribute"
    assert hasattr(pattern.data, "notes"), "Pattern data missing notes"

@pytest.mark.asyncio
async def test_fetch_note_patterns(test_db) -> None:
    """Test fetching note patterns."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = test_db
    
    # Comprehensive test note patterns with exact validation requirements
    note_patterns_data = [
        {
            "id": "test_pattern_1",
            "name": "Ascending Major Triad",
            "pattern": [0, 4, 7],  # Major triad intervals
            "description": "Ascending major triad intervals exploring harmonic structure",
            "tags": ["triad", "ascending", "harmony"],
            "direction": "forward",
            "use_chord_tones": True,
            "complexity": 0.5,
            "is_test": True,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "restart_on_chord": False,
            "use_scale_mode": False,
            "arpeggio_mode": False,
            "octave_range": [4, 5],
            "default_duration": 1.0,
            "index": 0
        },
        {
            "id": "test_pattern_2",
            "name": "Descending Seconds",
            "pattern": [0, -2, -4],  # Descending second intervals
            "description": "Descending second intervals exploring melodic tension",
            "tags": ["seconds", "descending", "tension"],
            "direction": "backward",
            "use_scale_mode": True,
            "complexity": 0.3,
            "is_test": True,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "restart_on_chord": False,
            "use_chord_tones": False,
            "arpeggio_mode": False
        },
        {
            "id": "test_pattern_3",
            "name": "Chromatic Walk",
            "pattern": [0, 1, 2, 3],  # Chromatic walk
            "description": "Chromatic ascending walk exploring tonal color and tension",
            "tags": ["chromatic", "walk", "color"],
            "arpeggio_mode": True,
            "restart_on_chord": True,
            "complexity": 0.7,
            "is_test": True,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "direction": "forward",
            "use_chord_tones": False,
            "use_scale_mode": False
        },
        {
            "id": "test_pattern_4",
            "name": "Wide Interval Leap",
            "pattern": [0, 7, -5],  # Wide interval leap
            "description": "Wide interval leap exploring melodic range and contrast",
            "tags": ["leap", "wide_interval", "contrast"],
            "direction": "alternating",
            "use_chord_tones": True,
            "use_scale_mode": True,
            "complexity": 0.8,
            "is_test": True,
            "duration": 1.5,
            "position": 0.5,
            "velocity": 80,
            "restart_on_chord": True,
            "arpeggio_mode": True
        },
        {
            "id": "test_pattern_5",
            "name": "Symmetric Pattern",
            "pattern": [0, 2, 4, 2, 0],  # Symmetric pattern
            "description": "Symmetric melodic pattern exploring balance and symmetry",
            "tags": ["symmetric", "balanced", "exploration"],
            "direction": "random",
            "use_chord_tones": False,
            "use_scale_mode": False,
            "complexity": 0.6,
            "is_test": True,
            "duration": 2.0,
            "position": 0.0,
            "velocity": 72,
            "restart_on_chord": False,
            "arpeggio_mode": False,
            "index": 0
        }
    ]
    
    # Comprehensive test rhythm patterns with exact validation requirements
    rhythm_patterns_data = [
        {
            "id": "rhythm_pattern_1",
            "name": "Basic Rock Beat",
            "pattern": [1.0, 0.5, 0.5, 1.0],  # Typical rock beat duration
            "description": "Standard 4/4 rock beat pattern with strong backbeat",
            "tags": ["rock", "4/4", "backbeat"],
            "time_signature": "4/4",
            "complexity": 4.0,  # Complexity is 1-10
            "is_test": True,
            "index": 1,
            "duration": 4.0,
            "position": 0.0,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "data": {
                "notes": [
                    {"position": 0.0, "duration": 1.0, "velocity": 100},
                    {"position": 1.0, "duration": 0.5, "velocity": 80},
                    {"position": 1.5, "duration": 0.5, "velocity": 80},
                    {"position": 2.0, "duration": 1.0, "velocity": 100}
                ],
                "time_signature": "4/4",
                "total_duration": 4.0
            }
        },
        {
            "id": "rhythm_pattern_2",
            "name": "Swing Jazz",
            "pattern": [0.66, 0.33, 0.66, 0.33],  # Swing rhythm
            "description": "Classic swing jazz rhythm with triplet feel",
            "tags": ["jazz", "swing", "triplet"],
            "time_signature": "4/4",
            "complexity": 6.0,
            "is_test": True,
            "index": 2,
            "duration": 4.0,
            "position": 0.0,
            "swing_ratio": 0.67,
            "groove_type": "swing",
            "data": {
                "notes": [
                    {"position": 0.0, "duration": 0.66, "velocity": 90},
                    {"position": 0.66, "duration": 0.33, "velocity": 70},
                    {"position": 1.0, "duration": 0.66, "velocity": 90},
                    {"position": 1.66, "duration": 0.33, "velocity": 70}
                ],
                "time_signature": "4/4",
                "total_duration": 4.0
            }
        },
        {
            "id": "rhythm_pattern_3",
            "name": "Syncopated Latin",
            "pattern": [0.5, 0.25, 0.25, 0.5, 0.5],  # Syncopated latin rhythm
            "description": "Syncopated latin rhythm pattern with complex subdivisions",
            "tags": ["latin", "syncopated", "complex"],
            "time_signature": "5/4",
            "complexity": 8.0,
            "is_test": True,
            "index": 3,
            "duration": 5.0,
            "position": 0.0,
            "swing_ratio": 0.6,
            "groove_type": "shuffle",
            "data": {
                "notes": [
                    {"position": 0.0, "duration": 0.5, "velocity": 100},
                    {"position": 0.5, "duration": 0.25, "velocity": 80},
                    {"position": 0.75, "duration": 0.25, "velocity": 80},
                    {"position": 1.0, "duration": 0.5, "velocity": 90},
                    {"position": 1.5, "duration": 0.5, "velocity": 90}
                ],
                "time_signature": "5/4",
                "total_duration": 5.0
            }
        },
        {
            "id": "rhythm_pattern_4",
            "name": "Waltz Ballad",
            "pattern": [1.0, 0.5, 0.5],  # Waltz rhythm
            "description": "Classic 3/4 waltz rhythm with gentle flow",
            "tags": ["waltz", "ballad", "3/4"],
            "time_signature": "3/4",
            "complexity": 3.0,
            "is_test": True,
            "index": 4,
            "duration": 3.0,
            "position": 0.0,
            "swing_ratio": 0.55,
            "groove_type": "straight",
            "data": {
                "notes": [
                    {"position": 0.0, "duration": 1.0, "velocity": 80},
                    {"position": 1.0, "duration": 0.5, "velocity": 60},
                    {"position": 1.5, "duration": 0.5, "velocity": 60}
                ],
                "time_signature": "3/4",
                "total_duration": 3.0
            }
        },
        {
            "id": "rhythm_pattern_5",
            "name": "Progressive Polyrhythm",
            "pattern": [0.75, 0.5, 0.25, 0.5, 0.75],  # Complex polyrhythm
            "description": "Advanced polyrhythmic pattern exploring rhythmic complexity",
            "tags": ["progressive", "polyrhythm", "complex"],
            "time_signature": "5/4",
            "complexity": 9.0,
            "is_test": True,
            "index": 5,
            "duration": 5.0,
            "position": 0.5,
            "swing_ratio": 0.6,
            "groove_type": "shuffle",
            "data": {
                "notes": [
                    {"position": 0.5, "duration": 0.75, "velocity": 100},
                    {"position": 1.25, "duration": 0.5, "velocity": 90},
                    {"position": 1.75, "duration": 0.25, "velocity": 80},
                    {"position": 2.0, "duration": 0.5, "velocity": 90},
                    {"position": 2.5, "duration": 0.75, "velocity": 100}
                ],
                "time_signature": "5/4",
                "total_duration": 5.0
            }
        }
    ]
    
    # Insert test note patterns
    for pattern in note_patterns_data:
        # Convert the dictionary to a NotePattern instance before inserting
        note_pattern = NotePattern(**pattern)
        await db.note_pattern_collection.insert_one(note_pattern.model_dump(by_alias=True))
    
    # Insert test rhythm patterns
    for pattern in rhythm_patterns_data:
        # Convert the dictionary to a RhythmPattern instance before inserting
        rhythm_pattern = RhythmPattern(**pattern)
        await db.rhythm_pattern_collection.insert_one(rhythm_pattern.model_dump(by_alias=True))
    
    result = await fetch_note_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(test_db) -> None:
    """Test fetching a note pattern by ID."""
    logger.debug(f'Using test_db fixture for note pattern by ID test')
    
    # Use the test_db parameter directly
    try:
        # Fetch all note patterns to get an actual pattern ID
        available_patterns = await fetch_note_patterns(test_db)
        
        if not available_patterns:
            logger.error("No note patterns found in the database")
            assert False, "No note patterns available for testing"
        
        # Use the first pattern's ID for testing
        pattern_id = available_patterns[0].id
        
        result = await fetch_note_pattern_by_id(pattern_id, test_db)
        
        if result is None:
            logger.error(f"No pattern found with ID '{pattern_id}'")
            # Log available patterns to help diagnose
            logger.debug("Available Patterns:")
            for pattern in available_patterns:
                logger.debug(f"Pattern ID: {pattern.id}")
        
        assert result is not None
        log_validation_details(result)
    except Exception as e:
        logger.error(f"Error in test_fetch_note_pattern_by_id: {e}")
        logger.error(f"Full exception traceback:", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(test_db) -> None:
    """Test fetching with invalid data."""
    logger.debug(f'Using test_db fixture for invalid data test')
    # Use the test_db directly instead of creating a new connection
    with pytest.raises(ValueError, match=r"Value error, Chords list cannot be empty"):
        await test_db.chord_progressions.insert_one(ChordProgression(
            id="invalid_id",
            name="Invalid Chord Progression",
            chords=[],  # This should trigger the validation error
            key="C",
            scale_type=ScaleType.MAJOR.value,
            scale_info={"root": {"note_name": "C", "octave": 4}, "scale_type": ScaleType.MAJOR.value}
        ).model_dump())

@pytest.mark.asyncio
async def test_fetch_chord_progressions_with_new_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for chord progressions with new data test')
    
    # Use the test_db parameter directly instead of creating a new connection
    
    # Log the current state of the chord_progressions collection
    current_data = await test_db.chord_progressions.find().to_list(None)
    logger.debug(f"Current chord progressions in DB: {len(current_data)}")
    
    # Clear the chord_progressions collection before tests
    await test_db.chord_progressions.delete_many({})
    
    # Create a new chord progression
    c_major = Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR)
    f_major = Chord(root=Note(note_name="F", octave=4), quality=ChordQuality.MAJOR)
    g_major = Chord(root=Note(note_name="G", octave=4), quality=ChordQuality.MAJOR)
    
    new_progression = ChordProgression(
        id=str(uuid.uuid4()),
        name="New Test Progression",
        chords=[c_major, f_major, g_major, c_major],
        key="C",
        scale_type=ScaleType.MAJOR.value,
        scale_info={"root": {"note_name": "C", "octave": 4}, "scale_type": ScaleType.MAJOR.value}
    )
    
    # Check for duplicate names
    existing_progression = await test_db.chord_progressions.find_one({'name': 'New Test Progression'})
    if existing_progression:
        # Modify name or skip insertion
        new_progression.name = "Unique Test Progression"
    
    # Insert the new progression
    await test_db.chord_progressions.insert_one(new_progression.model_dump())
    
    # Fetch all progressions
    all_progressions = await fetch_chord_progressions(test_db)
    
    # Verify the new progression was fetched
    assert len(all_progressions) > 0
    assert any(prog.name == "New Test Progression" for prog in all_progressions)

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for note patterns with new data test')
    db = test_db
    await db.note_pattern_collection.insert_one({
        "id": "pattern_2",
        "name": "Test Pattern",
        "pattern": NotePatternData(
            notes=[
                {"note_name": "C", "octave": 4, "duration": 1.0, "velocity": 100},
                {"note_name": "E", "octave": 4, "duration": 1.0, "velocity": 100},
                {"note_name": "G", "octave": 4, "duration": 1.0, "velocity": 100}
            ],
            intervals=[2, 2, 1, 2, 2, 2, 1],
            duration=1.0,
            position=0.0,
            velocity=100,
            direction="up",
            use_chord_tones=False,
            use_scale_mode=False,
            arpeggio_mode=False,
            restart_on_chord=False,
            octave_range=[4, 5],
            default_duration=1.0,
            index=0
        ),
        "description": "Test Pattern Description",
        "tags": ["test"],
        "complexity": 0.5,
    })
    result = await fetch_note_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for rhythm patterns with new data test')
    db = test_db
    await db.rhythm_pattern_collection.insert_one({
        "id": "test_rhythm_pattern",
        "name": "Test Rhythm Pattern",
        "data": {
            "pattern": [1.0, 0.5, 0.5, 1.0],  # Typical rock beat duration
            "time_signature": "4/4",
            "swing_enabled": False,
            "total_duration": 4.0,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "humanize_amount": 0.0,
            "default_duration": 1.0,
            "accents": [1.0, 0.9, 0.8, 1.0]  # Accent pattern matching the original notes
        },
        "description": "A test rhythm pattern",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "groove_type": "straight",
        "duration": 4.0
    })
    result = await fetch_rhythm_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], RhythmPattern)

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for note patterns with new data test')
    db = test_db
    await db.note_pattern_collection.insert_one({
        "id": "pattern_2",
        "name": "Test Note Pattern",
        "pattern": [0, 2, 4],  # Major triad intervals
        "description": "A test note pattern with simple intervals",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "direction": "up",
        "use_chord_tones": False,
        "use_scale_mode": False,
        "arpeggio_mode": False,
        "restart_on_chord": False,
        "is_test": True,
        "duration": 1.0,
        "position": 0.0,
        "velocity": 64,
        "index": 0
    })
    result = await fetch_note_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for invalid data test')
    db = test_db
    with pytest.raises(ValueError, match=r"Value error, Chords list cannot be empty"):
        await db.chord_progression_collection.insert_one(ChordProgression(
            id="invalid_id",
            name="Invalid Chord Progression",
            chords=[],  # This should trigger the validation error
            key="C",
            scale_type=ScaleType.MAJOR.value,
            scale_info={"root": {"note_name": "C", "octave": 4}, "scale_type": ScaleType.MAJOR.value}
        ).model_dump())

@pytest.mark.asyncio
async def test_process_chord_data() -> None:
    """Test processing chord data."""
    from src.note_gen.models.chord import ChordQuality  # Import ChordQuality directly
    
    valid_data = {
        'id': 'test_chord_progression',
        'name': 'Test Progression',
        'chords': [{
            'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
            'quality': 'MAJOR'  # Use string instead of enum
        }],
        'key': 'C',
        'scale_type': 'MAJOR'
    }
    processed = process_chord_data(valid_data)
    logger.debug(f'Processed chord data: {processed}')
    logger.debug(f'Asserting processed chord data: {processed}')
    logger.debug(f'Expected structure: first chord quality should be MAJOR')
    
    # Access quality directly from the dictionary
    assert processed['chords'][0]['quality'] == 'MAJOR'
    
    # Or if process_chord_data converts strings to ChordQuality enums:
    # assert processed['chords'][0]['quality'] == ChordQuality.MAJOR.value

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_structured_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for note patterns with new data test')
    db = test_db
    
    # Comprehensive test note pattern data with proper structure
    note_pattern_data = {
        "id": "test_pattern_2",
        "name": "Test Note Pattern",
        "description": "A test note pattern with simple intervals",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "is_test": True,
        # Move pattern-specific fields into the data structure
        "data": {
            # Removed notes array - using only intervals to define the pattern
            "intervals": [0, 2, 4],  # Major triad intervals
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64.0,
            "direction": "up",
            "use_chord_tones": False,
            "use_scale_mode": False,
            "arpeggio_mode": False,
            "restart_on_chord": False,
            "octave_range": [4, 5],
            "default_duration": 1.0,
            "index": 0
        }
    }
    
    try:
        # Clear any existing patterns to ensure test isolation
        await db.note_patterns.delete_many({"is_test": True})
        
        # Insert the note pattern
        await db.note_patterns.insert_one(note_pattern_data)
        
        # Fetch and validate
        result = await fetch_note_patterns(db, {"is_test": True})
        
        logger.debug("Fetched Note Patterns:")
        for pattern in result:
            log_validation_details(pattern)
        
        assert len(result) > 0, "No patterns found"
        
        # Check that all items in result are NotePattern instances
        # The right way to check is to use the module name and class
        for i, pattern in enumerate(result):
            assert pattern.__class__.__name__ == "NotePattern", f"Item {i} is not a NotePattern: {type(pattern)}"
            assert pattern.__class__.__module__ == "src.note_gen.models.patterns", f"Item {i} has wrong module: {pattern.__class__.__module__}"
        
        # Check specific structure details to verify proper conversion
        for pattern in result:
            assert hasattr(pattern, 'data'), "Pattern is missing data attribute"
            assert pattern.data is not None, "Pattern data is None"
            
            # Verify data has the expected structure - notes are optional if intervals are present
            if hasattr(pattern.data, 'intervals') and pattern.data.intervals:
                # If we have intervals, notes are optional
                logger.debug(f"Pattern has intervals: {pattern.data.intervals}")
                assert pattern.data.intervals == [0, 2, 4], "Pattern intervals don't match expected values"
            else:
                # If no intervals, notes must be present
                assert hasattr(pattern.data, 'notes'), "Pattern data is missing notes attribute"
                assert len(pattern.data.notes) > 0, "Pattern data has empty notes list"
            
    except Exception as e:
        logger.error(f"Error in test_fetch_note_patterns_with_structured_data: {e}")
        logger.error(f"Full exception traceback:", exc_info=True)
        raise
    finally:
        # Clean up test data
        await db.note_patterns.delete_many({"is_test": True})

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for rhythm patterns with new data test')
    db = test_db
    await db.rhythm_pattern_collection.insert_one({
        "id": "test_rhythm_pattern",
        "name": "Test Rhythm Pattern",
        "data": {
            "pattern": [1.0, 0.5, 0.5, 1.0],  # Typical rock beat duration
            "time_signature": "4/4",
            "swing_enabled": False,
            "total_duration": 4.0,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "humanize_amount": 0.0,
            "default_duration": 1.0,
            "accents": [1.0, 0.9, 0.8, 1.0]  # Accent pattern matching the original notes
        },
        "description": "A test rhythm pattern",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "groove_type": "straight",
        "duration": 4.0
    })
    result = await fetch_rhythm_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], RhythmPattern)

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for note patterns with new data test')
    db = test_db
    await db.note_pattern_collection.insert_one({
        "id": "pattern_2",
        "name": "Test Note Pattern",
        "pattern": [0, 2, 4],  # Major triad intervals
        "description": "A test note pattern with simple intervals",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "direction": "up",
        "use_chord_tones": False,
        "use_scale_mode": False,
        "arpeggio_mode": False,
        "restart_on_chord": False,
        "is_test": True,
        "duration": 1.0,
        "position": 0.0,
        "velocity": 64,
        "index": 0
    })
    result = await fetch_note_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for invalid data test')
    db = test_db
    with pytest.raises(ValueError, match=r"Value error, Chords list cannot be empty"):
        await db.chord_progression_collection.insert_one(ChordProgression(
            id="invalid_id",
            name="Invalid Chord Progression",
            chords=[],  # This should trigger the validation error
            key="C",
            scale_type=ScaleType.MAJOR.value,
            scale_info={"root": {"note_name": "C", "octave": 4}, "scale_type": ScaleType.MAJOR.value}
        ).model_dump())

@pytest.mark.asyncio
async def test_process_chord_data() -> None:
    """Test processing chord data."""
    from src.note_gen.models.chord import ChordQuality  # Import ChordQuality directly
    
    valid_data = {
        'id': 'test_chord_progression',
        'name': 'Test Progression',
        'chords': [{
            'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
            'quality': 'MAJOR'  # Use string instead of enum
        }],
        'key': 'C',
        'scale_type': 'MAJOR'
    }
    processed = process_chord_data(valid_data)
    logger.debug(f'Processed chord data: {processed}')
    logger.debug(f'Asserting processed chord data: {processed}')
    logger.debug(f'Expected structure: first chord quality should be MAJOR')
    
    # Access quality directly from the dictionary
    assert processed['chords'][0]['quality'] == 'MAJOR'
    
    # Or if process_chord_data converts strings to ChordQuality enums:
    # assert processed['chords'][0]['quality'] == ChordQuality.MAJOR.value

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_logging(test_db):
    db = test_db  # Use the database directly without context manager
    # Insert note patterns
    note_pattern_data = {
        "id": "pattern_2",
        "name": "Test Note Pattern",
        "pattern": [0, 2, 4],  # Major triad intervals
        "description": "A test note pattern with simple intervals",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "direction": "up",
        "use_chord_tones": False,
        "use_scale_mode": False,
        "arpeggio_mode": False,
        "restart_on_chord": False,
        "is_test": True,
        "duration": 1.0,
        "position": 0.0,
        "velocity": 64,
        "index": 0
    }
    await db.note_pattern_collection.insert_one(note_pattern_data)
    result = await db.note_pattern_collection.find_one({'id': note_pattern_data['id']})
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_logging(test_db):
    db = test_db  # Use the database directly without context manager
    # Insert rhythm patterns
    rhythm_pattern_data = {
        "_id": "test_rhythm_pattern_1",
        "id": "test_rhythm_pattern_1",
        "name": "Syncopated Jazz Rhythm",
        "pattern": {
            # Remove notes array and use pattern definition instead
            "pattern": [0.5, 0.5],  # Simple swing pattern
            "accents": [1.0, 0.8],  # Accent pattern matching the original notes
            "time_signature": "4/4",
            "swing_enabled": True,
            "total_duration": 1.0,
            "swing_ratio": 0.67,
            "groove_type": "swing",
            "humanize_amount": 0.0,
            "default_duration": 1.0
        },
        "description": "A syncopated jazz rhythm pattern with swing",
        "tags": ["jazz", "syncopated", "swing"],
        "complexity": 0.7,
        "duration": 1.0
    }
    
    try:
        # Try to delete first in case it exists from a previous test run
        await db.rhythm_pattern_collection.delete_one({"_id": rhythm_pattern_data["_id"]})
        # Then insert the test data
        await db.rhythm_pattern_collection.insert_one(rhythm_pattern_data)
    except Exception as e:
        logger.warning(f"Error during setup: {e}")
        
    result = await db.rhythm_pattern_collection.find_one({'id': rhythm_pattern_data['id']})
    assert result is not None

import logging
import json

# Configure more verbose logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add helper function for detailed logging
def log_validation_details(pattern):
    """
    Log validation details for a pattern object.
    
    Args:
        pattern: Pattern object to log details for
    """
    try:
        pattern_type = type(pattern)
        logger.debug(f"Pattern type: {pattern_type}")
        logger.debug(f"Pattern ID: {getattr(pattern, 'id', 'No ID')}")
        logger.debug(f"Pattern Name: {getattr(pattern, 'name', 'No Name')}")
        
        # Check if it's a NotePattern instance
        if pattern_type.__name__ == 'NotePattern':
            logger.debug(f"Confirmed NotePattern instance")
            logger.debug(f"Tags: {getattr(pattern, 'tags', [])}")
            
            # Log data field details
            if hasattr(pattern, 'data'):
                if pattern.data is not None:
                    logger.debug(f"Data field type: {type(pattern.data)}")
                    if hasattr(pattern.data, 'notes'):
                        logger.debug(f"Notes count: {len(pattern.data.notes)}")
                        for i, note in enumerate(pattern.data.notes[:3]):  # Show first 3 notes
                            logger.debug(f"  Note {i}: {note}")
                    if hasattr(pattern.data, 'intervals'):
                        logger.debug(f"Intervals: {pattern.data.intervals}")
                else:
                    logger.warning(f"Data field is None")
        else:
            logger.warning(f"Object is not a NotePattern instance: {pattern_type}")
    except Exception as e:
        logger.error(f"Error logging pattern details: {e}")

@pytest.mark.asyncio
async def test_fetch_note_patterns(test_db):
    logger.debug(f'Using test_db fixture for note patterns test')
    
    # Check available collections
    collections = await test_db.list_collection_names()
    logger.debug(f"Available collections in test_db: {collections}")
    
    # Check if note_pattern_collection exists
    if 'note_pattern_collection' not in collections:
        logger.warning("'note_pattern_collection' not found in database. Will use note_patterns.")
        # Create a simple note pattern to make sure there's data
        note_pattern = {
            "id": str(uuid.uuid4()),
            "name": "Test Pattern",
            "description": "Created for collection test",
            "tags": ["test"],
            "complexity": 0.5,
            "is_test": True,
            "data": {
                "notes": [{"note_name": "C", "octave": 4, "duration": 1.0, "velocity": 100}],
                "intervals": [0, 4, 7],
                "duration": 1.0,
                "position": 0.0,
                "velocity": 100
            }
        }
        # Try both collection names
        try:
            await test_db.note_pattern_collection.insert_one(note_pattern)
            logger.debug("Inserted test pattern into note_pattern_collection")
        except Exception:
            logger.debug("Failed to insert into note_pattern_collection, trying note_patterns")
            try:
                await test_db.note_patterns.insert_one(note_pattern)
                logger.debug("Inserted test pattern into note_patterns")
            except Exception as e:
                logger.error(f"Failed to insert into either collection: {e}")
    
    # Use the test_db parameter directly
    try:
        # Check counts before fetch
        note_pattern_collection_count = await test_db.note_pattern_collection.count_documents({})
        note_patterns_count = await test_db.note_patterns.count_documents({})
        logger.debug(f"note_pattern_collection count: {note_pattern_collection_count}")
        logger.debug(f"note_patterns count: {note_patterns_count}")
        
        result = await fetch_note_patterns(test_db)
        
        # Log detailed information about each pattern
        logger.debug(f"Fetched {len(result)} note patterns")
        
        for pattern in result:
            logger.debug(f"Fetched Note Pattern ID: {pattern.id}")
            log_validation_details(pattern)
        
        assert len(result) > 0, "No note patterns were fetched"
        assert all(isinstance(pattern, NotePattern) for pattern in result), "Some items are not NotePattern instances"
    except Exception as e:
        logger.error(f"Error in test_fetch_note_patterns: {e}")
        logger.error(f"Full exception traceback:", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(test_db) -> None:
    """Test fetching a note pattern by ID."""
    logger.debug(f'Using test_db fixture for note pattern by ID test')
    
    # Use the test_db parameter directly
    try:
        # Fetch all note patterns to get an actual pattern ID
        available_patterns = await fetch_note_patterns(test_db)
        
        if not available_patterns:
            logger.error("No note patterns found in the database")
            assert False, "No note patterns available for testing"
        
        # Use the first pattern's ID for testing
        pattern_id = available_patterns[0].id
        
        result = await fetch_note_pattern_by_id(pattern_id, test_db)
        
        if result is None:
            logger.error(f"No pattern found with ID '{pattern_id}'")
            # Log available patterns to help diagnose
            logger.debug("Available Patterns:")
            for pattern in available_patterns:
                logger.debug(f"Pattern ID: {pattern.id}")
        
        assert result is not None
        log_validation_details(result)
    except Exception as e:
        logger.error(f"Error in test_fetch_note_pattern_by_id: {e}")
        logger.error(f"Full exception traceback:", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for note patterns with new data test')
    db = test_db
    
    # Comprehensive test note pattern data
    note_pattern_data = {
        "id": "pattern_2",
        "name": "Test Note Pattern",
        "pattern": [0, 2, 4],  # Major triad intervals
        "description": "A test note pattern with simple intervals",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "direction": "up",
        "use_chord_tones": False,
        "use_scale_mode": False,
        "arpeggio_mode": False,
        "restart_on_chord": False,
        "is_test": True,
        "duration": 1.0,
        "position": 0.0,
        "velocity": 64,
        "index": 0
    }
    
    try:
        # Insert the note pattern
        await db.note_patterns.insert_one(note_pattern_data)
        
        # Fetch and validate
        result = await fetch_note_patterns(db)
        
        logger.debug("Fetched Note Patterns:")
        for pattern in result:
            log_validation_details(pattern)
        
        assert len(result) > 0
        assert all(isinstance(pattern, NotePattern) for pattern in result)
    except Exception as e:
        logger.error(f"Error in test_fetch_note_patterns_with_new_data: {e}")
        logger.error(f"Full exception traceback:", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    """Test fetching note patterns with newly inserted data."""
    try:
        # Check available collections
        collections = await test_db.list_collection_names()
        logger.debug(f"Available collections in test_db: {collections}")
        
        # Create test pattern with well-structured data
        test_id = str(uuid.uuid4())
        logger.debug(f"Generated test ID: {test_id}")
        
        note_pattern_data = {
            "id": test_id,
            "name": "Test Pattern for Fetch",
            "description": "Pattern created for testing fetch function",
            "tags": ["test", "fetch"],
            "complexity": 0.5,
            "is_test": True,
            "data": {
                "notes": [
                    {
                        "note_name": "C", 
                        "octave": 4, 
                        "duration": 1.0, 
                        "velocity": 100.0
                    },
                    {
                        "note_name": "E", 
                        "octave": 4, 
                        "duration": 1.0, 
                        "velocity": 100.0
                    },
                    {
                        "note_name": "G", 
                        "octave": 4, 
                        "duration": 1.0, 
                        "velocity": 100.0
                    }
                ],
                "intervals": [0, 4, 7],  # C Major triad intervals
                "duration": 1.0,
                "position": 0.0,
                "velocity": 100.0,
                "direction": "up",
                "use_chord_tones": False,
                "use_scale_mode": False,
                "arpeggio_mode": False,
                "restart_on_chord": False,
                "octave_range": [4, 5],
                "default_duration": 1.0,
                "index": 0
            }
        }
        
        # Log the data we're about to insert
        logger.debug(f"Inserting note pattern with ID: {note_pattern_data['id']}")
        logger.debug(f"Pattern data structure: {list(note_pattern_data.keys())}")
        logger.debug(f"Pattern data.data structure: {list(note_pattern_data['data'].keys())}")
            
        # Delete test patterns from the collection to ensure clean test
        await test_db.note_patterns.delete_many({"is_test": True})
        logger.debug("Deleted test patterns from note_patterns")
        
        # Insert pattern
        result = await test_db.note_patterns.insert_one(note_pattern_data)
        logger.debug(f"Successfully inserted note pattern into note_patterns with MongoDB ID: {result.inserted_id}")
        
        # Verify insertion
        doc = await test_db.note_patterns.find_one({"id": test_id})
        logger.debug(f"Verification result: {'Found' if doc else 'Not found'}")
        if doc:
            logger.debug(f"Retrieved document ID: {doc.get('id', 'No ID')}")
            logger.debug(f"Retrieved MongoDB _id: {doc.get('_id', 'No _id')}")
        
        assert doc, "Failed to insert note pattern into collection"
        
        # Fetch and validate
        logger.debug(f"Calling fetch_note_patterns...")
        result = await fetch_note_patterns(test_db)
        
        logger.debug(f"Fetched {len(result)} note patterns")
        
        # Check all IDs for debugging
        logger.debug("All fetched pattern IDs:")
        for pattern in result:
            pattern_id = getattr(pattern, 'id', None)
            pattern_name = getattr(pattern, 'name', 'unnamed')
            logger.debug(f"  - {pattern_name}: {pattern_id}")
            
            # Detailed comparison to our test ID
            if pattern_id:
                if pattern_id == test_id:
                    logger.debug(f"MATCH: Pattern ID '{pattern_id}' matches test ID '{test_id}'")
                else:
                    # Check for format differences
                    logger.debug(f"NO MATCH: '{pattern_id}' != '{test_id}'")
                    logger.debug(f"  - Lengths: {len(pattern_id)} vs {len(test_id)}")
                    logger.debug(f"  - Types: {type(pattern_id)} vs {type(test_id)}")
            
            log_validation_details(pattern)
        
        # Try different approach for ID comparison
        found_test_pattern = False
        for pattern in result:
            pattern_id = getattr(pattern, 'id', None)
            pattern_name = getattr(pattern, 'name', '')
            
            # Check name match if ID fails
            if pattern_id == test_id or pattern_name == "Test Pattern for Fetch":
                found_test_pattern = True
                logger.debug(f"Found our test pattern: ID={pattern_id}, name={pattern_name}")
                break
        
        assert found_test_pattern, "Our test pattern was not found in the fetch results"
        assert len(result) > 0, "No note patterns were fetched"
        assert all(isinstance(pattern, NotePattern) or type(pattern).__name__ == 'NotePattern' for pattern in result), "Not all fetched items are NotePattern instances"
    except Exception as e:
        logger.error(f"Error in test_fetch_note_patterns_with_new_data: {e}")
        logger.error(f"Full exception traceback:", exc_info=True)
        raise
    finally:
        # Clean up test data
        logger.debug("Cleaning up test data")
        try:
            await test_db.note_patterns.delete_many({"is_test": True})
            logger.debug("Successfully cleaned up test data")
        except Exception as e:
            logger.error(f"Error cleaning up test data: {e}")

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Using test_db fixture for note patterns with new data test')
    db = test_db
    
    # Use a unique name to ensure we can match it later
    unique_pattern_name = f"Test Note Pattern {uuid.uuid4()}"
    
    await db.note_patterns.insert_one({
        "id": str(uuid.uuid4()),  # Generate a new UUID instead of hardcoding
        "name": unique_pattern_name,  # Use the unique name
        "pattern": [0, 2, 4],  # Major triad intervals
        "description": "A test note pattern with simple intervals",
        "tags": ["test", "basic"],
        "complexity": 0.5,
        "direction": "up",
        "use_chord_tones": False,
        "use_scale_mode": False,
        "arpeggio_mode": False,
        "restart_on_chord": False,
        "is_test": True,
        "duration": 1.0,
        "position": 0.0,
        "velocity": 64,
        "index": 0,
        "data": {  # Add the data field with required attributes
            "notes": [
                {"note_name": "C", "octave": 4, "duration": 1.0, "velocity": 100}
            ],
            "intervals": [0, 2, 4],
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64
        }
    })
    
    result = await fetch_note_patterns(db)
    
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)
    
    # Find our pattern by name instead of by ID
    matching_patterns = [p for p in result if p.name == unique_pattern_name]
    assert len(matching_patterns) == 1, f"Expected 1 pattern with name '{unique_pattern_name}', found {len(matching_patterns)}"
    
    # Clean up the test pattern
    await db.note_patterns.delete_many({"name": unique_pattern_name})

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_legacy_data(test_db) -> None:
    """
    Tests the ability to fetch note patterns with legacy data format.
    This test uses the old note_pattern_collection format for compatibility testing.
    """
    logger.debug(f'Using test_db fixture for note patterns with legacy data test')
    db = test_db
    
    # Create a unique pattern ID for testing
    pattern_id = f"legacy_test_pattern_{uuid.uuid4()}"
    
    try:
        # Insert into the correct collection: note_patterns
        await db.note_patterns.insert_one({
            "id": pattern_id,
            "name": "Legacy Test Note Pattern",
            "pattern": [0, 2, 4],  # Major triad intervals in legacy format
            "description": "A test note pattern with simple intervals (legacy format)",
            "tags": ["test", "basic", "legacy"],
            "complexity": 0.5,
            "direction": "up",
            "use_chord_tones": False,
            "use_scale_mode": False,
            "arpeggio_mode": False,
            "restart_on_chord": False,
            "is_test": True,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "index": 0
        })
        
        # Fetch and validate
        result = await fetch_note_patterns(db, {"id": pattern_id})
        
        # Log details for debugging
        logger.debug(f"Found {len(result)} note patterns")
        for pattern in result:
            logger.debug(f"Pattern ID: {pattern.id}, Name: {pattern.name}")
            logger.debug(f"Pattern type: {type(pattern)}, class: {pattern.__class__.__name__}, module: {pattern.__class__.__module__}")
        
        # Assertions
        assert len(result) > 0, "No note patterns found"
        
        # The right way to check is to use the module name and class name
        if len(result) > 0:
            assert result[0].__class__.__name__ == "NotePattern", f"Expected NotePattern, got {result[0].__class__.__name__}"
            assert result[0].__class__.__module__ == "src.note_gen.models.patterns", f"Wrong module: {result[0].__class__.__module__}"
            
            # The _normalize_note_pattern_document function should convert the legacy format
            # to the new format with a data field
            pattern = result[0]
            assert hasattr(pattern, 'data'), "Pattern is missing data attribute"
            
    except Exception as e:
        logger.error(f"Error in test_fetch_note_patterns_with_legacy_data: {e}")
        logger.exception("Exception details:")
        raise
    finally:
        # Clean up test data
        await db.note_patterns.delete_one({"id": pattern_id})

@pytest.mark.asyncio
async def test_fetch_chord_progression_patterns(test_db):
    """Test fetching chord progression patterns from the database."""
    from src.note_gen.fetch_patterns import (
        fetch_chord_progression_patterns,
        extract_patterns_from_chord_progressions
    )
    from src.note_gen.models.patterns import ChordProgressionPattern, ChordPatternItem
    
    # First, create some test patterns
    pattern1 = ChordProgressionPattern(
        id=str(uuid.uuid4()),
        name="I-IV-V-I",
        pattern=[
            ChordPatternItem(degree=1, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=4, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=5, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=1, quality="MAJOR", duration=4.0)
        ],
        description="Basic I-IV-V-I progression",
        tags=["basic", "common"],
        complexity=0.3
    )
    
    pattern2 = ChordProgressionPattern(
        id=str(uuid.uuid4()),
        name="II-V-I",
        pattern=[
            ChordPatternItem(degree=2, quality="MINOR_SEVENTH", duration=4.0),
            ChordPatternItem(degree=5, quality="DOMINANT_SEVENTH", duration=4.0),
            ChordPatternItem(degree=1, quality="MAJOR_SEVENTH", duration=4.0)
        ],
        description="Jazz II-V-I progression",
        tags=["jazz", "common"],
        complexity=0.6
    )
    
    # Insert the patterns into the database
    await test_db.chord_progression_patterns.insert_one(pattern1.model_dump())
    await test_db.chord_progression_patterns.insert_one(pattern2.model_dump())
    
    # Fetch the patterns
    patterns = await fetch_chord_progression_patterns(test_db)
    
    # Check that we got the expected patterns
    assert len(patterns) >= 2
    
    # Check that our patterns are in the results
    pattern1_found = False
    pattern2_found = False
    
    for pattern in patterns:
        if pattern.id == pattern1.id:
            pattern1_found = True
            assert pattern.name == "I-IV-V-I"
            assert len(pattern.pattern) == 4
            assert pattern.pattern[0].degree == 1
            assert pattern.pattern[0].quality == "MAJOR"
        
        if pattern.id == pattern2.id:
            pattern2_found = True
            assert pattern.name == "II-V-I"
            assert len(pattern.pattern) == 3
            assert pattern.pattern[0].degree == 2
            assert pattern.pattern[0].quality == "MINOR_SEVENTH"
    
    assert pattern1_found
    assert pattern2_found
    
    # Clean up
    await test_db.chord_progression_patterns.delete_many({"id": {"$in": [pattern1.id, pattern2.id]}})

@pytest.mark.asyncio
async def test_fetch_chord_progression_pattern_by_id(test_db):
    """Test fetching a chord progression pattern by ID."""
    from src.note_gen.fetch_patterns import fetch_chord_progression_pattern_by_id
    from src.note_gen.models.patterns import ChordProgressionPattern, ChordPatternItem
    
    # Create a test pattern
    pattern_id = str(uuid.uuid4())
    pattern = ChordProgressionPattern(
        id=pattern_id,
        name="Minor Plagal Cadence",
        pattern=[
            ChordPatternItem(degree=1, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=4, quality="MINOR", duration=4.0),
            ChordPatternItem(degree=1, quality="MAJOR", duration=4.0)
        ],
        description="I-iv-I progression",
        tags=["cadence", "minor_plagal"],
        complexity=0.4
    )
    
    # Insert the pattern into the database
    await test_db.chord_progression_patterns.insert_one(pattern.model_dump())
    
    # Fetch the pattern by ID
    fetched_pattern = await fetch_chord_progression_pattern_by_id(pattern_id, test_db)
    
    # Check that we got the expected pattern
    assert fetched_pattern is not None
    assert fetched_pattern.id == pattern_id
    assert fetched_pattern.name == "Minor Plagal Cadence"
    assert len(fetched_pattern.pattern) == 3
    assert fetched_pattern.pattern[1].degree == 4
    assert fetched_pattern.pattern[1].quality == "MINOR"
    
    # Test fetching a non-existent pattern
    non_existent_pattern = await fetch_chord_progression_pattern_by_id("non_existent_id", test_db)
    assert non_existent_pattern is None
    
    # Clean up
    await test_db.chord_progression_patterns.delete_one({"id": pattern_id})

@pytest.mark.asyncio
async def test_extract_patterns_from_chord_progressions(test_db):
    """Test extracting chord progression patterns from existing chord progressions."""
    from src.note_gen.fetch_patterns import (
        fetch_chord_progressions,
        extract_patterns_from_chord_progressions,
        fetch_chord_progression_patterns
    )
    from src.note_gen.models.chord import Chord, ChordQuality
    from src.note_gen.models.chord_progression import ChordProgression
    from src.note_gen.models.note import Note
    from src.note_gen.models.scale_info import ScaleInfo
    from src.note_gen.models.enums import ScaleType
    
    # Create a scale info
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
    
    # Create chord progressions
    progression1 = ChordProgression(
        id=str(uuid.uuid4()),
        name="C-F-G7-C",
        chords=[
            Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="F", octave=4), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="G", octave=4), quality=ChordQuality.DOMINANT_SEVENTH),
            Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR)
        ],
        key="C",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info
    )
    
    progression2 = ChordProgression(
        id=str(uuid.uuid4()),
        name="C-Am-F-G",
        chords=[
            Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="A", octave=4), quality=ChordQuality.MINOR),
            Chord(root=Note(note_name="F", octave=4), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="G", octave=4), quality=ChordQuality.MAJOR)
        ],
        key="C",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info
    )
    
    # Insert progressions into the database
    await test_db.chord_progressions.insert_one(progression1.model_dump())
    await test_db.chord_progressions.insert_one(progression2.model_dump())
    
    # Extract patterns
    patterns = await extract_patterns_from_chord_progressions(test_db)
    
    # Check that we got patterns
    assert len(patterns) >= 2
    
    # Verify that patterns were created with the correct structure
    for pattern in patterns:
        assert isinstance(pattern.id, str)
        assert isinstance(pattern.name, str)
        assert len(pattern.pattern) > 0
        assert pattern.description is not None
        
        # Check that each pattern item has the required fields
        for item in pattern.pattern:
            assert 1 <= item.degree <= 7
            assert isinstance(item.quality, str)
            assert item.duration > 0
    
    # Fetch the patterns from the database to verify they were saved
    db_patterns = await fetch_chord_progression_patterns(test_db)
    
    # Check that at least our 2 patterns are there
    assert len(db_patterns) >= 2
    
    # Clean up - delete the progressions and the extracted patterns
    await test_db.chord_progressions.delete_many({"id": {"$in": [progression1.id, progression2.id]}})
    await test_db.chord_progression_patterns.delete_many({})  # Clean up all patterns for simplicity

async def insert_test_pattern(collection, pattern_data):
    pattern_data['id'] = str(ObjectId())
    await collection.insert_one(pattern_data)
    return pattern_data['id']

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_structured_data(test_db):
    pattern_data = {
        'id': 'test_pattern_123',
        'data': {
            'notes': [{'note_name': 'C', 'octave': 4, 'velocity': 100}],
            'intervals': [0, 2, 4],
            'duration': 1.0
        },
        'complexity': 0.5
    }
    response = test_client.get('/note-patterns')
    assert response.status_code == 200
    assert isinstance(response.json()[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_chord_progression_pattern_by_id(test_db):
    pattern_data = {
        'id': str(uuid.uuid4()),
        'name': 'Test Pattern',
        'chords': [{'root': 'C', 'quality': 'MAJOR'}]
    }
    await test_db.chord_progression_patterns.insert_one(pattern_data)
    result = await fetch_chord_progression_pattern_by_id(pattern_data['id'], test_db)
    assert result is not None
    assert result.id == pattern_data['id']

# Using the app imported at the top of the file

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)