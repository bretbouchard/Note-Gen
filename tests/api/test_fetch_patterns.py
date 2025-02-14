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
    process_chord_data
)
from src.note_gen.models.enums import ScaleType, ChordQualityType

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote, RhythmPatternData
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.patterns import NotePatternData
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.database.db import get_db_conn, MONGODB_URI
import motor.motor_asyncio
import uuid 
from pydantic import BaseModel, ValidationError
from typing import AsyncGenerator, Optional, List, Union

from tests.test_data_generator import generate_test_data

# Configure logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log environment variable values
logger.debug(f'MONGODB_URI: {os.getenv("MONGODB_URI")}')
logger.debug(f'MONGODB_TEST_URI: {os.getenv("MONGODB_TEST_URI")}')
logger.debug(f'DATABASE_NAME: {os.getenv("DATABASE_NAME")}')


# Fixture to manage event loop
@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def clean_test_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Clean and initialize test database."""
    logger.debug("Initializing MongoDB client.")
    try:
        logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
        db_gen = get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
        async for db in db_gen:
            # Clear all collections
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

@pytest.fixture
async def test_db():
    """Fixture to provide a test database connection."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    async with get_db_conn() as db:
        yield db

@pytest.mark.asyncio
async def test_fetch_chord_progressions(test_db):
    """Test fetching chord progressions."""
    logger.debug(f'Connected to database. Available collections: {await test_db.list_collection_names()}')
    progressions = await fetch_chord_progressions(test_db)
    assert len(progressions) > 0, "No chord progressions found"
    first_progression = progressions[0]
    assert isinstance(first_progression, ChordProgression), "Fetched item is not a ChordProgression"
    assert first_progression.id == "progression_1", "Incorrect progression ID"
    assert first_progression.name == "I-IV-V", "Incorrect progression name"
    assert len(first_progression.chords) == 3, "Incorrect number of chords"

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_v1(test_db) -> None:
    """Test fetching a chord progression by ID with correct scale types."""
    logger.debug(f'Connected to database. Available collections: {await test_db.list_collection_names()}')
    await test_db.chord_progression_collection.insert_one({
        'id': 'test_progression',
        'index': 0,
        'name': 'Test Progression',
        'pattern': [],  # No notes included
        'tags': ['test'],
        'complexity': 0.5,
        'description': 'A test chord progression without notes.'
    })
    result = await test_db.chord_progression_collection.find_one({'id': 'test_progression'})
    assert result is not None
    assert result['name'] == 'Test Progression'

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(test_db):
    """Test fetching rhythm patterns."""
    logger.debug(f'Connected to database. Available collections: {await test_db.list_collection_names()}')
    rhythm_patterns = await test_db.rhythm_patterns.find().to_list(None)
    assert len(rhythm_patterns) > 0, "No rhythm patterns found"
    first_pattern = rhythm_patterns[0]
    assert isinstance(first_pattern, RhythmPattern), "Fetched item is not a RhythmPattern"
    assert first_pattern.id == "pattern_2", "Incorrect pattern ID"
    assert first_pattern.name == "Test Swing Pattern", "Incorrect pattern name"
    assert len(first_pattern.data.notes) == 3, "Incorrect number of notes"

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(test_db) -> None:
    """Test fetching rhythm pattern by ID."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    
    # Insert a test rhythm pattern without notes
    await test_db.rhythm_pattern_collection.insert_one({
        'id': 'test_rhythm_pattern',
        'index': 0,
        'name': 'Test Rhythm Pattern',
        'pattern': [],  # No notes included
        'tags': ['test'],
        'complexity': 0.5,
        'description': 'A test rhythm pattern without notes.'
    })
    result = await test_db.rhythm_pattern_collection.find_one({'id': 'test_rhythm_pattern'})
    assert result is not None
    assert result['name'] == 'Test Rhythm Pattern'

@pytest.mark.asyncio
async def test_fetch_note_patterns(test_db) -> None:
    """Test fetching note patterns."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
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
            "index": 1,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "restart_on_chord": False,
            "use_scale_mode": False,
            "arpeggio_mode": False
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
            "index": 2,
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
            "index": 3,
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
            "index": 4,
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
            "index": 5,
            "duration": 2.0,
            "position": 0.0,
            "velocity": 72,
            "restart_on_chord": False,
            "arpeggio_mode": False
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    try:
        # Fetch all note patterns to get an actual pattern ID
        available_patterns = await fetch_note_patterns(db)
        
        if not available_patterns:
            logger.error("No note patterns found in the database")
            assert False, "No note patterns available for testing"
        
        # Use the first pattern's ID for testing
        pattern_id = available_patterns[0].id
        
        result = await fetch_note_pattern_by_id(db, pattern_id)
        
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    async with get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen') as db:
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
async def test_fetch_chord_progressions_with_new_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    # Log the current state of the chord_progressions collection
    current_data = await db.chord_progression_collection.find().to_list(None)
    logger.debug(f"Current chord progressions in the database: {current_data}")
    result = await fetch_chord_progressions(db)
    logger.debug(f'Fetched chord progressions with new data: {result}')
    logger.debug(f'Asserting fetched chord progressions with new data: {result}')
    logger.debug(f'Expected structure: list of ChordProgression objects')
    logger.debug(f'Fetched progression: {result[0]}')
    assert len(result) > 0
    logger.debug(f'Asserting fetched chord progressions with new data: {result}')
    logger.debug(f'Expected structure: list of ChordProgression objects')
    logger.debug(f'Fetched progression: {result[0]}')
    assert isinstance(result[0], ChordProgression)

async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    await db.rhythm_pattern_collection.insert_one({
        "id": "test_rhythm_pattern",
        "name": "Test Rhythm Pattern",
        "data": {
            "notes": [
                {
                    "position": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "is_rest": False,
                    "pitch": 60,
                    "swing_ratio": 0.67
                },
                {
                    "position": 1.0,
                    "duration": 1.0,
                    "velocity": 90,
                    "is_rest": False,
                    "pitch": 62,
                    "swing_ratio": 0.67
                }
            ],
            "time_signature": "4/4",
            "swing_enabled": False,
            "total_duration": 4.0,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "humanize_amount": 0.0,
            "default_duration": 1.0
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    await db.note_pattern_collection.insert_one({
        "id": "pattern_2",
        "index": 0,
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
        "velocity": 64
    })
    result = await fetch_note_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    async with get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen') as db:
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
    valid_data = {
        'id': 'test_chord_progression',
        'name': 'Test Progression',
        'chords': [{
            'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
            'quality': "MAJOR"
        }],
        'key': 'C',
        'scale_type': 'MAJOR'
    }
    processed = process_chord_data(valid_data)
    logger.debug(f'Processed chord data: {processed}')
    logger.debug(f'Asserting processed chord data: {processed}')
    logger.debug(f'Expected structure: first chord with quality as ChordQualityType.MAJOR.value')
    logger.debug(f'Processed data: {processed}')
    assert processed['chords'][0].quality == ChordQualityType.MAJOR  # Compare with enumeration value

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_logging(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
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
            "index": 1,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "restart_on_chord": False,
            "use_scale_mode": False,
            "arpeggio_mode": False
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
            "index": 2,
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
            "index": 3,
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
            "index": 4,
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
            "index": 5,
            "duration": 2.0,
            "position": 0.0,
            "velocity": 72,
            "restart_on_chord": False,
            "arpeggio_mode": False
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    try:
        # Fetch all note patterns to get an actual pattern ID
        available_patterns = await fetch_note_patterns(db)
        
        if not available_patterns:
            logger.error("No note patterns found in the database")
            assert False, "No note patterns available for testing"
        
        # Use the first pattern's ID for testing
        pattern_id = available_patterns[0].id
        
        result = await fetch_note_pattern_by_id(db, pattern_id)
        
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
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
        await db.note_pattern_collection.insert_one(note_pattern_data)
        
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
async def test_fetch_rhythm_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    await db.rhythm_pattern_collection.insert_one({
        "id": "test_rhythm_pattern",
        "name": "Test Rhythm Pattern",
        "data": {
            "notes": [
                {
                    "position": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "is_rest": False,
                    "pitch": 60,
                    "swing_ratio": 0.67
                },
                {
                    "position": 1.0,
                    "duration": 1.0,
                    "velocity": 90,
                    "is_rest": False,
                    "pitch": 62,
                    "swing_ratio": 0.67
                }
            ],
            "time_signature": "4/4",
            "swing_enabled": False,
            "total_duration": 4.0,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "humanize_amount": 0.0,
            "default_duration": 1.0
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    await db.note_pattern_collection.insert_one({
        "id": "pattern_2",
        "index": 0,
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
        "velocity": 64
    })
    result = await fetch_note_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    async with get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen') as db:
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
async def test_fetch_chord_progression(test_db):
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    # Insert the test chord progression
    await db.chord_progression_collection.insert_one({
        "id": "test_i_iv_v",
        "name": "test_i_iv_v",
        "index": 1,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["test", "popular", "progression"],
        "complexity": 0.5,
        "description": "A common chord progression in popular music."
    })

    chord_progression = await db.chord_progression_collection.find_one({"id": "test_i_iv_v"})
    assert chord_progression is not None
    assert chord_progression["description"] == "A common chord progression in popular music."
    logger.debug(f"Asserting fetched chord progression: {chord_progression}")
    logger.debug(f"Expected structure: dictionary")
    logger.debug(f"Fetched progression: {chord_progression}")
    assert isinstance(chord_progression, dict)
    assert chord_progression["id"] == "test_i_iv_v"
    assert chord_progression["name"] == "test_i_iv_v"
    assert chord_progression["key"] == "C"
    assert chord_progression["scale_type"] == "MAJOR"
    assert len(chord_progression["chords"]) > 0
    for chord in chord_progression["chords"]:
        assert isinstance(chord, dict)
        assert chord["quality"] == "MAJOR"

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_v2(test_db) -> None:
    """Test fetching a chord progression by ID with correct scale types."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    # Insert a test chord progression without notes
    await db.chord_progression_collection.insert_one({
        'id': 'test_progression',
        'index': 0,
        'name': 'Test Progression',
        'pattern': [],  # No notes included
        'tags': ['test'],
        'complexity': 0.5,
        'description': 'A test chord progression without notes.'
    })
    result = await db.chord_progression_collection.find_one({'id': 'test_progression'})
    assert result is not None
    assert result['name'] == 'Test Progression'

@pytest.mark.asyncio
async def test_fetch_chord_progression_v2(test_db):
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    # Insert the test chord progression
    await db.chord_progression_collection.insert_one({
        "id": "test_i_iv_v",
        "name": "test_i_iv_v",
        "index": 1,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["test", "popular", "progression"],
        "complexity": 0.5,
        "description": "A common chord progression in popular music."
    })

    chord_progression = await db.chord_progression_collection.find_one({"id": "test_i_iv_v"})
    assert chord_progression is not None
    assert chord_progression["description"] == "A common chord progression in popular music."
    logger.debug(f"Asserting fetched chord progression: {chord_progression}")
    logger.debug(f"Expected structure: dictionary")
    logger.debug(f"Fetched progression: {chord_progression}")
    assert isinstance(chord_progression, dict)
    assert chord_progression["id"] == "test_i_iv_v"
    assert chord_progression["name"] == "test_i_iv_v"
    assert chord_progression["key"] == "C"
    assert chord_progression["scale_type"] == "MAJOR"
    assert len(chord_progression["chords"]) > 0
    for chord in chord_progression["chords"]:
        assert isinstance(chord, dict)
        assert chord["quality"] == "MAJOR"

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_v3(test_db) -> None:
    """Test fetching a chord progression by ID with correct scale types."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    async with get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen') as db:
        # Insert a test chord progression without notes
        await db.chord_progression_collection.insert_one({
            'id': 'test_progression',
            'index': 0,
            'name': 'Test Progression',
            'pattern': [],  # No notes included
            'tags': ['test'],
            'complexity': 0.5,
            'description': 'A test chord progression without notes.'
        })
        result = await db.chord_progression_collection.find_one({'id': 'test_progression'})
        assert result is not None
        assert result['name'] == 'Test Progression'

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    rhythm_pattern_data = {
        "_id": "test_rhythm_pattern_1",
        "id": "test_rhythm_pattern_1",
        "name": "Syncopated Jazz Rhythm",
        "pattern": {
            "notes": [
                {
                    "position": 0.0,
                    "duration": 0.5,
                    "velocity": 100,
                    "is_rest": False,
                    "pitch": 60,
                    "swing_ratio": 0.67,
                    "accent": 1.0
                },
                {
                    "position": 0.5,
                    "duration": 0.5,
                    "velocity": 90,
                    "is_rest": False,
                    "pitch": 62,
                    "swing_ratio": 0.67,
                    "accent": 0.8
                }
            ],
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
    await db.rhythm_pattern_collection.insert_one(rhythm_pattern_data)
    
    result = await fetch_rhythm_patterns(db)
    assert len(result) > 0, "No rhythm patterns found"
    assert isinstance(result[0], RhythmPattern), "Result is not a RhythmPattern instance"

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    note_pattern_data = {
        "_id": "pattern_2",
        "id": "pattern_2",
        "index": 1,
        "name": "Major Scale Ascending Pattern",
        "pattern": [0, 2, 4, 5, 7, 9, 11],  # Major scale intervals
        "description": "An ascending pattern exploring major scale intervals",
        "tags": ["major", "scale", "ascending"],
        "complexity": 0.6,
        "direction": "forward",
        "use_chord_tones": True,
        "use_scale_mode": True,
        "arpeggio_mode": False,
        "restart_on_chord": False,
        "is_test": True,
        "duration": 1.0,
        "position": 0.0,
        "velocity": 64
    }
    await db.note_pattern_collection.insert_one(note_pattern_data)
    
    result = await fetch_note_patterns(db)
    assert len(result) > 0, "No note patterns found"
    assert isinstance(result[0], NotePattern), "Result is not a NotePattern instance"

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_logging(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    # Comprehensive test note patterns with exact validation requirements
    note_patterns_data = [
        {
            "_id": "test_pattern_1",
            "id": "test_pattern_1",
            "name": "Ascending Major Triad",
            "pattern": [0, 4, 7],  # Major triad intervals
            "description": "Ascending major triad intervals exploring harmonic structure",
            "tags": ["triad", "ascending", "harmony"],
            "direction": "forward",
            "use_chord_tones": True,
            "complexity": 0.5,
            "is_test": True,
            "index": 1,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "restart_on_chord": False,
            "use_scale_mode": False,
            "arpeggio_mode": False
        },
        {
            "_id": "test_pattern_2",
            "id": "test_pattern_2",
            "name": "Descending Seconds",
            "pattern": [0, -2, -4],  # Descending second intervals
            "description": "Descending second intervals exploring melodic tension",
            "tags": ["seconds", "descending", "tension"],
            "direction": "backward",
            "use_scale_mode": True,
            "complexity": 0.3,
            "is_test": True,
            "index": 2,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "restart_on_chord": False,
            "use_chord_tones": False,
            "arpeggio_mode": False
        }
    ]
    
    # Insert test note patterns
    for pattern in note_patterns_data:
        await db.note_pattern_collection.insert_one(pattern)
    
    logger.debug(f'Current note patterns in the database before fetching: {await db.note_pattern_collection.find().to_list(None)}')
    logger.debug(f'Fetching note patterns from the database...')
    
    result = await fetch_note_patterns(db)
    logger.debug(f'Fetched note patterns: {result}')
    
    assert len(result) > 0, "No note patterns found"
    assert all(isinstance(pattern, NotePattern) for pattern in result), "All patterns should be NotePattern instances"

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(test_db) -> None:
    """Test fetching a note pattern by ID."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    try:
        # Fetch all note patterns to get an actual pattern ID
        available_patterns = await fetch_note_patterns(db)
        
        if not available_patterns:
            logger.error("No note patterns found in the database")
            assert False, "No note patterns available for testing"
        
        # Use the first pattern's ID for testing
        pattern_id = available_patterns[0].id
        
        result = await fetch_note_pattern_by_id(db, pattern_id)
        
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
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
        await db.note_pattern_collection.insert_one(note_pattern_data)
        
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
async def test_fetch_rhythm_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    await db.rhythm_pattern_collection.insert_one({
        "id": "test_rhythm_pattern",
        "name": "Test Rhythm Pattern",
        "data": {
            "notes": [
                {
                    "position": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "is_rest": False,
                    "pitch": 60,
                    "swing_ratio": 0.67
                },
                {
                    "position": 1.0,
                    "duration": 1.0,
                    "velocity": 90,
                    "is_rest": False,
                    "pitch": 62,
                    "swing_ratio": 0.67
                }
            ],
            "time_signature": "4/4",
            "swing_enabled": False,
            "total_duration": 4.0,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "humanize_amount": 0.0,
            "default_duration": 1.0
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    await db.note_pattern_collection.insert_one({
        "id": "pattern_2",
        "index": 0,
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
        "velocity": 64
    })
    result = await fetch_note_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    async with get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen') as db:
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
async def test_fetch_chord_progression(test_db):
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    # Insert the test chord progression
    await db.chord_progression_collection.insert_one({
        "id": "test_i_iv_v",
        "name": "test_i_iv_v",
        "index": 1,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["test", "popular", "progression"],
        "complexity": 0.5,
        "description": "A common chord progression in popular music."
    })

    chord_progression = await db.chord_progression_collection.find_one({"id": "test_i_iv_v"})
    assert chord_progression is not None
    assert chord_progression["description"] == "A common chord progression in popular music."
    logger.debug(f"Asserting fetched chord progression: {chord_progression}")
    logger.debug(f"Expected structure: dictionary")
    logger.debug(f"Fetched progression: {chord_progression}")
    assert isinstance(chord_progression, dict)
    assert chord_progression["id"] == "test_i_iv_v"
    assert chord_progression["name"] == "test_i_iv_v"
    assert chord_progression["key"] == "C"
    assert chord_progression["scale_type"] == "MAJOR"
    assert len(chord_progression["chords"]) > 0
    for chord in chord_progression["chords"]:
        assert isinstance(chord, dict)
        assert chord["quality"] == "MAJOR"

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_v2(test_db) -> None:
    """Test fetching a chord progression by ID with correct scale types."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    # Insert a test chord progression without notes
    await db.chord_progression_collection.insert_one({
        'id': 'test_progression',
        'index': 0,
        'name': 'Test Progression',
        'pattern': [],  # No notes included
        'tags': ['test'],
        'complexity': 0.5,
        'description': 'A test chord progression without notes.'
    })
    result = await db.chord_progression_collection.find_one({'id': 'test_progression'})
    assert result is not None
    assert result['name'] == 'Test Progression'

@pytest.mark.asyncio
async def test_fetch_chord_progression_v2(test_db):
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    # Insert the test chord progression
    await db.chord_progression_collection.insert_one({
        "id": "test_i_iv_v",
        "name": "test_i_iv_v",
        "index": 1,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["test", "popular", "progression"],
        "complexity": 0.5,
        "description": "A common chord progression in popular music."
    })

    chord_progression = await db.chord_progression_collection.find_one({"id": "test_i_iv_v"})
    assert chord_progression is not None
    assert chord_progression["description"] == "A common chord progression in popular music."
    logger.debug(f"Asserting fetched chord progression: {chord_progression}")
    logger.debug(f"Expected structure: dictionary")
    logger.debug(f"Fetched progression: {chord_progression}")
    assert isinstance(chord_progression, dict)
    assert chord_progression["id"] == "test_i_iv_v"
    assert chord_progression["name"] == "test_i_iv_v"
    assert chord_progression["key"] == "C"
    assert chord_progression["scale_type"] == "MAJOR"
    assert len(chord_progression["chords"]) > 0
    for chord in chord_progression["chords"]:
        assert isinstance(chord, dict)
        assert chord["quality"] == "MAJOR"

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_v3(test_db) -> None:
    """Test fetching a chord progression by ID with correct scale types."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    async with get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen') as db:
        # Insert a test chord progression without notes
        await db.chord_progression_collection.insert_one({
            'id': 'test_progression',
            'index': 0,
            'name': 'Test Progression',
            'pattern': [],  # No notes included
            'tags': ['test'],
            'complexity': 0.5,
            'description': 'A test chord progression without notes.'
        })
        result = await db.chord_progression_collection.find_one({'id': 'test_progression'})
        assert result is not None
        assert result['name'] == 'Test Progression'

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    rhythm_pattern_data = {
        "_id": "test_rhythm_pattern_1",
        "id": "test_rhythm_pattern_1",
        "name": "Syncopated Jazz Rhythm",
        "pattern": {
            "notes": [
                {
                    "position": 0.0,
                    "duration": 0.5,
                    "velocity": 100,
                    "is_rest": False,
                    "pitch": 60,
                    "swing_ratio": 0.67,
                    "accent": 1.0
                },
                {
                    "position": 0.5,
                    "duration": 0.5,
                    "velocity": 90,
                    "is_rest": False,
                    "pitch": 62,
                    "swing_ratio": 0.67,
                    "accent": 0.8
                }
            ],
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
    await db.rhythm_pattern_collection.insert_one(rhythm_pattern_data)
    
    result = await fetch_rhythm_patterns(db)
    assert len(result) > 0, "No rhythm patterns found"
    assert isinstance(result[0], RhythmPattern), "Result is not a RhythmPattern instance"

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    note_pattern_data = {
        "_id": "pattern_2",
        "id": "pattern_2",
        "index": 1,
        "name": "Major Scale Ascending Pattern",
        "pattern": [0, 2, 4, 5, 7, 9, 11],  # Major scale intervals
        "description": "An ascending pattern exploring major scale intervals",
        "tags": ["major", "scale", "ascending"],
        "complexity": 0.6,
        "direction": "forward",
        "use_chord_tones": True,
        "use_scale_mode": True,
        "arpeggio_mode": False,
        "restart_on_chord": False,
        "is_test": True,
        "duration": 1.0,
        "position": 0.0,
        "velocity": 64
    }
    await db.note_pattern_collection.insert_one(note_pattern_data)
    
    result = await fetch_note_patterns(db)
    assert len(result) > 0, "No note patterns found"
    assert isinstance(result[0], NotePattern), "Result is not a NotePattern instance"

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_logging(test_db) -> None:
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    # Comprehensive test note patterns with exact validation requirements
    note_patterns_data = [
        {
            "_id": "test_pattern_1",
            "id": "test_pattern_1",
            "name": "Ascending Major Triad",
            "pattern": [0, 4, 7],  # Major triad intervals
            "description": "Ascending major triad intervals exploring harmonic structure",
            "tags": ["triad", "ascending", "harmony"],
            "direction": "forward",
            "use_chord_tones": True,
            "complexity": 0.5,
            "is_test": True,
            "index": 1,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "restart_on_chord": False,
            "use_scale_mode": False,
            "arpeggio_mode": False
        },
        {
            "_id": "test_pattern_2",
            "id": "test_pattern_2",
            "name": "Descending Seconds",
            "pattern": [0, -2, -4],  # Descending second intervals
            "description": "Descending second intervals exploring melodic tension",
            "tags": ["seconds", "descending", "tension"],
            "direction": "backward",
            "use_scale_mode": True,
            "complexity": 0.3,
            "is_test": True,
            "index": 2,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 64,
            "restart_on_chord": False,
            "use_chord_tones": False,
            "arpeggio_mode": False
        }
    ]
    
    # Insert test note patterns
    for pattern in note_patterns_data:
        await db.note_pattern_collection.insert_one(pattern)
    
    logger.debug(f'Current note patterns in the database before fetching: {await db.note_pattern_collection.find().to_list(None)}')
    logger.debug(f'Fetching note patterns from the database...')
    
    result = await fetch_note_patterns(db)
    logger.debug(f'Fetched note patterns: {result}')
    
    assert len(result) > 0, "No note patterns found"
    assert all(isinstance(pattern, NotePattern) for pattern in result), "All patterns should be NotePattern instances"

import logging
import json

# Configure more verbose logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add helper function for detailed logging
def log_validation_details(obj):
    """
    Log detailed validation information for a Pydantic model.
    
    Args:
        obj: Pydantic model instance to log details for
    """
    try:
        # Convert the object to a dictionary for detailed inspection
        obj_dict = obj.model_dump() if hasattr(obj, 'model_dump') else obj.__dict__
        
        logger.debug(f"Object Type: {type(obj)}")
        logger.debug(f"Object Details:\n{json.dumps(obj_dict, indent=2)}")
    except Exception as e:
        logger.error(f"Error logging object details: {e}")

# Modify test functions to include more detailed logging
@pytest.mark.asyncio
async def test_fetch_note_patterns(test_db):
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    try:
        result = await fetch_note_patterns(db)
        
        # Log detailed information about each pattern
        for pattern in result:
            logger.debug(f"Fetched Note Pattern ID: {pattern.id}")
            log_validation_details(pattern)
        
        assert len(result) > 0
        assert all(isinstance(pattern, NotePattern) for pattern in result)
    except Exception as e:
        logger.error(f"Error in test_fetch_note_patterns: {e}")
        logger.error(f"Full exception traceback:", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(test_db) -> None:
    """Test fetching a note pattern by ID."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
    try:
        # Fetch all note patterns to get an actual pattern ID
        available_patterns = await fetch_note_patterns(db)
        
        if not available_patterns:
            logger.error("No note patterns found in the database")
            assert False, "No note patterns available for testing"
        
        # Use the first pattern's ID for testing
        pattern_id = available_patterns[0].id
        
        result = await fetch_note_pattern_by_id(db, pattern_id)
        
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
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    db = await get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen')
    
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
        await db.note_pattern_collection.insert_one(note_pattern_data)
        
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
async def test_fetch_note_patterns_with_logging(test_db):
    async with get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen') as db:
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
    async with get_db_conn(uri=os.getenv("MONGODB_URI"), db_name='test_note_gen') as db:
        # Insert rhythm patterns
        rhythm_pattern_data = {
            "_id": "test_rhythm_pattern_1",
            "id": "test_rhythm_pattern_1",
            "name": "Syncopated Jazz Rhythm",
            "pattern": {
                "notes": [
                    {
                        "position": 0.0,
                        "duration": 0.5,
                        "velocity": 100,
                        "is_rest": False,
                        "pitch": 60,
                        "swing_ratio": 0.67,
                        "accent": 1.0
                    },
                    {
                        "position": 0.5,
                        "duration": 0.5,
                        "velocity": 90,
                        "is_rest": False,
                        "pitch": 62,
                        "swing_ratio": 0.67,
                        "accent": 0.8
                    }
                ],
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
        await db.rhythm_pattern_collection.insert_one(rhythm_pattern_data)
        result = await db.rhythm_pattern_collection.find_one({'id': rhythm_pattern_data['id']})
        assert result is not None