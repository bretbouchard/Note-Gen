"""Tests for fetch_patterns.py"""

import pytest
import asyncio
import logging
from src.note_gen.fetch_patterns import (
    fetch_chord_progressions,
    fetch_chord_progression_by_id,
    fetch_rhythm_patterns,
    fetch_rhythm_pattern_by_id,
    fetch_note_patterns,
    fetch_note_pattern_by_id,
    process_chord_data
)
from src.note_gen.models.enums import ScaleType

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote, RhythmPatternData
from src.note_gen.models.note_pattern import NotePatternData, NotePatternResponse as NotePattern
from src.note_gen.models.note import Note
import motor.motor_asyncio
import uuid 

# Sample test data
# Update SAMPLE_CHORD_PROGRESSIONS in test_fetch_patterns.py
SAMPLE_CHORD_PROGRESSIONS = [
    {
        "id": "progression_1",
        "name": "I-IV-V",
        "complexity": 0.5,
        "key": "C",
        "scale_type": ScaleType.MAJOR,
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
                    Note(note_name="C", octave=4, duration=1, velocity=100)
                ]
            },
            {
                "root": Note(note_name="G", octave=4, duration=1, velocity=100),
                "quality": ChordQualityType.MAJOR,
                "notes": [
                    Note(note_name="G", octave=4, duration=1, velocity=100),
                    Note(note_name="B", octave=4, duration=1, velocity=100),
                    Note(note_name="D", octave=4, duration=1, velocity=100)
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

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
async def event_loop() -> None:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def clean_test_db(event_loop: asyncio.AbstractEventLoop) -> None:
    """Clean and initialize test database."""
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient()
        if client is None:
            raise RuntimeError("Failed to initialize MongoDB client.")
        db = client.test_note_gen
        
        # Clean the database
        await db.chord_progressions.delete_many({})
        await db.rhythm_patterns.delete_many({})
        await db.note_patterns.delete_many({})
        
        # ChordProgression test data
        test_chord_progression_data = [
            {
                "id": "progression_1",  # Unique ID for testing
                "name": "I-IV-V",
                "chords": [
                    {"root": {"note_name": "C", "octave": 4}, "quality": ChordQualityType.MAJOR.value},
                    {"root": {"note_name": "F", "octave": 4}, "quality": ChordQualityType.MAJOR.value},
                    {"root": {"note_name": "G", "octave": 4}, "quality": ChordQualityType.MAJOR.value}
                ],
                "key": "C",
                "scale_type": ScaleType.MAJOR.value,
                "complexity": 0.5,
                "scale_info": {
                    "root": {"note_name": "C", "octave": 4},
                    "scale_type": ScaleType.MAJOR.value
                }
            }
        ]
        
        logger.debug(f'Inserting test chord progression: {test_chord_progression_data}')
        
        # Log the current state of the database before insertion
        current_progressions = await db.chord_progressions.find().to_list(None)
        logger.debug(f'Current chord progressions in the database before insertion: {current_progressions}')

        # Insert the test chord progression
        await db.chord_progressions.insert_many(test_chord_progression_data)
        logger.debug(f'Inserted test chord progression: {test_chord_progression_data}')

        # Log the current state of the database after insertion
        current_progressions_after = await db.chord_progressions.find().to_list(None)
        logger.debug(f'Current chord progressions in the database after insertion: {current_progressions_after}')

        # RhythmPattern test data
        test_rhythm_pattern = {
            "id": "test_1",  # Unique ID for testing
            "name": "Test Pattern",
            "data": {
                "notes": [{"duration": 1.0, "velocity": 100, "position": 0.0}],
                "time_signature": "4/4",
                "swing_ratio": 0.67,
                "default_duration": 1.0,
                "total_duration": 4.0,
                "groove_type": "straight",
                "duration": 4.0
            },
            "description": "Test rhythm pattern",
            "complexity": 1.0
        }
        
        test_note_pattern = {
            "id": "pattern_1",  # Unique ID for testing
            "name": "Test Note Pattern",
            "data": NotePatternData(
                notes=[
                    {
                        "note_name": "C",
                        "octave": 4,
                        "duration": 1.0,
                        "velocity": 100
                    }
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
                default_duration=1.0
            ).model_dump(),
            "description": "Test pattern",
            "tags": ["test"],
            "complexity": 0.5,
            "style": "basic"
        }

        # Insert test data into the database
        await db.rhythm_patterns.insert_one(test_rhythm_pattern)
        await db.note_patterns.insert_one(test_note_pattern)

        # Invalid data test
        with pytest.raises(ValueError, match="Chords must be a non-empty list."):
            await db.chord_progressions.insert_one(ChordProgression(
                id="invalid_id",
                name="Invalid Chord Progression",
                chords=[],  # This should trigger the validation error
                key="C",
                scale_type=ScaleType.MAJOR.value,
                scale_info={"root": {"note_name": "C", "octave": 4}, "scale_type": ScaleType.MAJOR.value}
            ).dict())
        yield db
        client.close()  # Ensure client is closed after all operations

    except Exception as e:
        print(f"An error occurred: {e}")
        raise

@pytest.mark.asyncio
async def test_fetch_chord_progressions(clean_test_db) -> None:
    """Test fetching chord progressions."""
    result = await fetch_chord_progressions(clean_test_db)
    logger.debug(f'Fetched chord progressions: {result}')
    assert len(result) > 0
    assert isinstance(result[0], ChordProgression)

    # Update scale types and chord qualities in the fetched data
    for progression in result:
        progression.scale_type = 'MAJOR'  # Update scale type
        for chord in progression.chords:
            chord.quality = 'MAJOR'  # Update chord quality

    logger.debug(f'Updated chord progressions: {result}')
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id(setup_test_data):
    """Test fetching a chord progression by ID with correct scale types."""
    db = setup_test_data
    progression_id = 'progression_1'
    result = await fetch_chord_progression_by_id(progression_id, db)
    assert result is not None

    # Ensure scale type is uppercase
    assert result.scale_type == 'MAJOR'  # Update scale type check
    assert result.key == 'C'
    assert len(result.chords) > 0
    for chord in result.chords:
        assert chord.quality == 'MAJOR'  # Update chord quality check

    logger.debug(f'Fetched chord progression by ID: {result}')

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(clean_test_db) -> None:
    db = clean_test_db
    result = await fetch_rhythm_patterns(db)
    logger.debug(f'Fetched rhythm patterns: {result}')
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(clean_test_db) -> None:
    """Test fetching rhythm pattern by ID."""
    pattern_id = "test_1"
    result = await fetch_rhythm_pattern_by_id(pattern_id, clean_test_db)
    logger.debug(f'Fetched rhythm pattern: {result}')
    assert result is not None
    assert isinstance(result, RhythmPattern)


@pytest.mark.asyncio
async def test_fetch_note_patterns(clean_test_db) -> None:
    """Test fetching note patterns."""
    db = clean_test_db

    test_pattern = {
        "id": "pattern_2",
        "name": "Test Pattern",
        "data": NotePatternData(
            notes=[
                {
                    "note_name": "C",
                    "octave": 4,
                    "duration": 1.0,
                    "velocity": 100
                }
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
            default_duration=1.0
        ).model_dump(),
        "description": "Test pattern",
        "tags": ["test"],
        "complexity": 0.5,
        "style": "basic"
    }

    await db.note_patterns.insert_one(test_pattern)
    result = await fetch_note_patterns(db)
    logger.debug(f'Fetched note patterns: {result}')
    assert len(result) > 0
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(clean_test_db) -> None:
    """Test fetching note pattern by ID."""
    pattern_id = "pattern_1"
    result = await fetch_note_pattern_by_id(pattern_id, clean_test_db)
    logger.debug(f'Fetched note pattern: {result}')
    assert result is not None
    assert isinstance(result, NotePattern)

@pytest.mark.asyncio 
async def test_fetch_with_invalid_data(clean_test_db) -> None:
    db = clean_test_db
    # Insert invalid data directly into the test database
    with pytest.raises(ValueError, match="Chords must be a non-empty list."):
        await db.chord_progressions.insert_one(ChordProgression(
            id="invalid_id",
            name="Invalid Chord Progression",
            chords=[],  # This should trigger the validation error
            key="C",
            scale_type=ScaleType.MAJOR.value,
            scale_info={"root": {"note_name": "C", "octave": 4}, "scale_type": ScaleType.MAJOR.value}
        ).dict())

@pytest.mark.asyncio
async def test_fetch_chord_progressions_with_new_data(clean_test_db) -> None:
    db = clean_test_db
    result = await fetch_chord_progressions(db)
    logger.debug(f'Fetched chord progressions with new data: {result}')
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(clean_test_db) -> None:
    db = clean_test_db
    result = await fetch_note_patterns(db)
    logger.debug(f'Fetched note patterns with new data: {result}')
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_new_data(clean_test_db) -> None:
    """Test fetching rhythm patterns with new data."""
    db = clean_test_db

    test_pattern = {
        "id": "test_2",
        "name": "Test Pattern",
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
        ).model_dump(),
        "description": "Test rhythm pattern",
        "tags": ["test"],
        "complexity": 1.0,
        "style": "basic"
    }

    # Insert directly into collection
    await db.rhythm_patterns.insert_one(test_pattern)
    result = await fetch_rhythm_patterns(db)
    logger.debug(f'Fetched rhythm patterns with new data: {result}')
    assert len(result) > 0


@pytest.mark.asyncio
async def test_process_chord_data() -> None:
    """Test processing chord data."""
    valid_data = {
        'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
        'quality': "MAJOR"
    }
    db_name = "test_db"  # Mock database name
    processed = process_chord_data(valid_data, db_name=db_name)
    logger.debug(f'Processed chord data: {processed}')
    assert processed['quality'] == ChordQualityType.MAJOR.value  # Compare with enumeration value

@pytest.fixture
async def setup_test_data(clean_test_db):
    """Setup test data with correct scale types."""
    db = clean_test_db
    # Insert the chord progression with correct scale type
    test_progression = {
        'id': 'progression_1',
        'name': 'I-IV-V',
        'chords': [
            {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'},
            {'root': {'note_name': 'F', 'octave': 4}, 'quality': 'MAJOR'},
            {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'}
        ],
        'key': 'C',
        'scale_type': ScaleType.MAJOR.value,
        'complexity': 0.5,
        'scale_info': {
            'root': {'note_name': 'C', 'octave': 4},
            'scale_type': ScaleType.MAJOR.value
        }
    }
    await db.chord_progressions.delete_many({})
    await db.chord_progressions.insert_one(test_progression)
    return db