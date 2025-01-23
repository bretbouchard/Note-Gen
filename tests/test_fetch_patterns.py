"""Tests for fetch_patterns.py"""

import pytest
import asyncio
from src.note_gen.fetch_patterns import (
    fetch_chord_progressions,
    fetch_chord_progression_by_id,
    fetch_rhythm_patterns,
    fetch_rhythm_pattern_by_id,
    fetch_note_patterns,
    fetch_note_pattern_by_id,
    process_chord_data
)
from src.note_gen.models.enums import ChordQualityType, ScaleType
from src.note_gen.models.chord_quality import ChordQualityType

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote, RhythmPatternData
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.musical_elements import Note
import motor.motor_asyncio
import uuid 

# Sample test data
# Update SAMPLE_CHORD_PROGRESSIONS in test_fetch_patterns.py
SAMPLE_CHORD_PROGRESSIONS = [
    {
        "id": "1",
        "name": "I-IV-V",
        "complexity": 1.0,
        "key": "C",  # Add this
        "scale_type": ScaleType.MAJOR,  # Add this
        "chords": [
            {
                "root": Note(note_name="C", octave=4, duration=1, velocity=100),
                "quality": ChordQualityType.MAJOR,
                "notes": [
                    Note(note_name="C", octave=4, duration=1, velocity=100),
                    Note(note_name="E", octave=4, duration=1, velocity=100),
                    Note(note_name="G", octave=4, duration=1, velocity=100)
                ]
            },
            {
                "root": Note(note_name="F", octave=4, duration=1, velocity=100),
                "quality": ChordQualityType.MAJOR,
                "notes": [
                    Note(note_name="F", octave=4, duration=1, velocity=100),
                    Note(note_name="A", octave=4, duration=1, velocity=100),
                    Note(note_name="C", octave=5, duration=1, velocity=100)
                ]
            },
            {
                "root": Note(note_name="G", octave=4, duration=1, velocity=100),
                "quality": ChordQualityType.MAJOR,
                "notes": [
                    Note(note_name="G", octave=4, duration=1, velocity=100),
                    Note(note_name="B", octave=4, duration=1, velocity=100),
                    Note(note_name="D", octave=5, duration=1, velocity=100)
                ]
            }
        ]
    }
]


SAMPLE_NOTE_PATTERNS = [
    {
        "id": "1",
        "name": "Simple Arpeggio",
        "data": [1, 3, 5],  # Scale degrees as integers
        "notes": [
            Note(note_name="C", octave=4, duration=1, velocity=100),  # Ensure duration is included
            Note(note_name="E", octave=4, duration=1, velocity=100),
            Note(note_name="G", octave=4, duration=1, velocity=100)
        ],
        "description": "Basic triad arpeggio",
        "tags": ["test"],
        "is_test": True
    }
]


SAMPLE_RHYTHM_PATTERNS = [
    {
        "id": "1",
        "name": "Basic Quarter Notes",
        "data": RhythmPatternData(
            notes=[
                RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False),
                RhythmNote(position=1.0, duration=1.0, velocity=100, is_rest=False),
                RhythmNote(position=2.0, duration=1.0, velocity=100, is_rest=False),
                RhythmNote(position=3.0, duration=1.0, velocity=100, is_rest=False)
            ],
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.0,
            swing_ratio=0.67,
            style="basic",
            default_duration=1.0,
            total_duration=4.0,
            accent_pattern=[],
            groove_type="straight",
            variation_probability=0.0,
            duration=4.0
        ),
        "description": "Basic quarter note pattern",
        "tags": ["test"],
        "complexity": 1.0,
        "style": "basic",
        "pattern": "",
        "is_test": True
    }
]

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def clean_test_db(event_loop):
    """Clean and initialize test database."""
    client = motor.motor_asyncio.AsyncIOMotorClient(io_loop=event_loop)
    db = client.test_note_gen
    
    # Clean the database
    await db.chord_progressions.delete_many({})
    await db.rhythm_patterns.delete_many({})
    await db.note_patterns.delete_many({})
    
    # Insert test data
    test_chord_progressions = [
        {
            "_id": "1",
            "id": "progression_1",
            "name": "I-IV-V",
            "chords": [
                {"root": {"note_name": "C", "octave": 4}, "quality": ChordQualityType.MAJOR.value},
                {"root": {"note_name": "F", "octave": 4}, "quality": ChordQualityType.MAJOR.value},
                {"root": {"note_name": "G", "octave": 4}, "quality": ChordQualityType.MAJOR.value}
            ],
            "key": "C",
            "scale_type": ScaleType.MAJOR.value,
            "complexity": 0.5
        }
    ]
    
    test_rhythm_pattern = {
        "_id": "test_1",
        "id": "test_1",
        "name": "Test Pattern",
        "data": {
            "notes": [{"duration": 1.0, "velocity": 100, "position": 0.0}],
            "time_signature": "4/4",
            "swing_ratio": 0.67,
            "default_duration": 1.0,
            "total_duration": 4.0,
            "groove_type": "straight",
            "duration": 4.0,
            "style": "basic"
        },
        "description": "Test rhythm pattern",
        "complexity": 1.0,
        "style": "basic"
    }
    
    test_note_pattern = {
        "_id": "1",
        "id": "pattern_1",
        "name": "Test Note Pattern",
        "data": {
            "notes": [{
                "note_name": "C",
                "octave": 4,
                "duration": 1.0,
                "velocity": 100
            }],
            "intervals": None,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 100,
            "direction": "up",
            "use_chord_tones": False,
            "use_scale_mode": False,
            "arpeggio_mode": False,
            "restart_on_chord": False,
            "octave_range": [4, 5],
            "default_duration": 1.0
        },
        "description": "Test pattern",
        "tags": ["test"],
        "complexity": 0.5,
        "style": "basic"
    }
    
    await db.chord_progressions.insert_many(test_chord_progressions)
    await db.rhythm_patterns.insert_one(test_rhythm_pattern)
    await db.note_patterns.insert_one(test_note_pattern)
    
    yield db
    await client.close()
    
    # Insert test rhythm pattern data
    test_rhythm_pattern = {
        "_id": "test_1",
        "id": "test_1",
        "name": "Test Pattern",
        "data": {
            "notes": [{"duration": 1.0, "velocity": 100, "position": 0.0}],
            "time_signature": "4/4",
            "swing_ratio": 0.67,
            "default_duration": 1.0,
            "total_duration": 4.0,
            "groove_type": "straight",
            "duration": 4.0,
            "style": "basic"
        },
        "description": "Test rhythm pattern",
        "complexity": 1.0,
        "style": "basic"
    }
    
    # Insert test note pattern data
    test_note_pattern = {
        "_id": "1",
        "id": "pattern_1",
        "name": "Test Note Pattern",
        "data": {
            "notes": [{
                "note_name": "C",
                "octave": 4,
                "duration": 1.0,
                "velocity": 100
            }],
            "intervals": None,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 100,
            "direction": "up",
            "use_chord_tones": False,
            "use_scale_mode": False,
            "arpeggio_mode": False,
            "restart_on_chord": False,
            "octave_range": [4, 5],
            "default_duration": 1.0
        },
        "description": "Test pattern",
        "tags": ["test"],
        "complexity": 0.5,
        "style": "basic"
    }
    
    await db.chord_progressions.insert_many(test_chord_progressions)
    await db.rhythm_patterns.insert_one(test_rhythm_pattern)
    await db.note_patterns.insert_one(test_note_pattern)
    
    yield db
    await client.close()

@pytest.mark.asyncio
async def test_fetch_chord_progressions(clean_test_db):
    """Test fetching chord progressions."""
    result = await fetch_chord_progressions(clean_test_db)
    assert len(result) > 0
    assert isinstance(result[0], ChordProgression)


@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id(clean_test_db):
    db = clean_test_db
    progression_id = "1"
    result = await fetch_chord_progression_by_id(progression_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(clean_test_db):
    db = clean_test_db
    result = await fetch_rhythm_patterns(db)
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(clean_test_db):
    """Test fetching rhythm pattern by ID."""
    pattern_id = "test_1"
    result = await fetch_rhythm_pattern_by_id(pattern_id, clean_test_db)
    assert result is not None
    assert isinstance(result, RhythmPattern)


@pytest.mark.asyncio
async def test_fetch_note_patterns(clean_test_db):
    """Test fetching note patterns."""
    db = clean_test_db

    test_pattern = {
        "_id": f"test_{uuid.uuid4()}",
        "id": "test_pattern",
        "name": "Test Pattern",
        "data": {
            "notes": [
                {"note_name": "C", "octave": 4, "duration": 1.0, "velocity": 100}
            ],
            "intervals": None,
            "duration": 1.0,
            "position": 0.0,
            "velocity": 100,
            "direction": "up",
            "use_chord_tones": False,
            "use_scale_mode": False,
            "arpeggio_mode": False,
            "restart_on_chord": False,
            "octave_range": [4, 5],
            "default_duration": 1.0
        },
        "description": "Test pattern",
        "tags": ["test"],
        "complexity": 0.5,
        "style": "basic"
    }

    await db.note_patterns.insert_one(test_pattern)
    result = await fetch_note_patterns(db)
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(clean_test_db):
    """Test fetching note pattern by ID."""
    pattern_id = "1"
    result = await fetch_note_pattern_by_id(pattern_id, clean_test_db)
    assert result is not None
    assert isinstance(result, NotePattern)

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(clean_test_db):
    db = clean_test_db
    # Insert invalid data directly into the test database
    await db.chord_progressions.insert_one({"id": "invalid_id", "name": "Invalid Chord Progression", "chords": []})
    with pytest.raises(ValueError, match="Invalid chord progression data"):  # Expecting a ValueError for invalid data
        await fetch_chord_progressions(db)

@pytest.mark.asyncio
async def test_fetch_chord_progressions_with_new_data(clean_test_db):
    db = clean_test_db
    result = await fetch_chord_progressions(db)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(clean_test_db):
    db = clean_test_db
    result = await fetch_note_patterns(db)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_new_data(clean_test_db):
    """Test fetching rhythm patterns with new data."""
    db = clean_test_db

    test_pattern = {
        "_id": f"test_{uuid.uuid4()}",
        "id": "test_pattern",
        "name": "Test Pattern",
        "data": {
            "notes": [{
                "duration": 1.0,
                "velocity": 100,
                "position": 0.0
            }],
            "duration": 4.0,
            "time_signature": "4/4",
            "swing_enabled": True,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "variation_probability": 0.1,
            "humanize_amount": 0.1,
            "accent_pattern": None,
            "total_duration": 4.0,  # Added this field
            "default_duration": 1.0  # Added this field
        },
        "description": "Test rhythm pattern",
        "tags": ["test"],
        "complexity": 1.0,
        "style": "basic"
    }

    # Insert directly into collection
    await db.rhythm_patterns.insert_one(test_pattern)
    result = await fetch_rhythm_patterns(db)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_process_chord_data():
    """Test processing chord data."""
    valid_data = {
        'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
        'quality': "major"
    }
    processed = process_chord_data(valid_data)
    assert processed['quality'] == ChordQualityType.MAJOR
