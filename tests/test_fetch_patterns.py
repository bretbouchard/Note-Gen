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
from src.note_gen.models.chord import Chord  # Added missing import
import motor.motor_asyncio
import uuid 

# Sample test data
# Update SAMPLE_CHORD_PROGRESSIONS in test_fetch_patterns.py
SAMPLE_CHORD_PROGRESSIONS = [
    {
        "id": "progression_1",
        "index": 0,
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
        "is_test": True,
        "index": 0
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
            swing_ratio=0.67,
            default_duration=1.0,
            total_duration=4.0,
            groove_type="straight",
            variation_probability=0.0,
            duration=4.0
        ),
        "description": "Basic quarter note pattern",
        "tags": ["test"],
        "complexity": 1.0,
        "style": "basic",
        "pattern": "",
        "is_test": True,
        "index": 0
    }
]

logger = logging.getLogger(__name__)

@pytest.fixture
async def clean_test_db() -> None:
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
                "index": 0,
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
            "index": 0,
            "name": "Test Pattern",
            "data": {
                "notes": [{"duration": 1.0, "velocity": 100, "position": 0.0}],
                "time_signature": "4/4",
                "swing_ratio": 0.67,
                "default_duration": 1.0,
                "total_duration": 1.0,
                "groove_type": "straight",
                "duration": 1.0
            },
            "description": "Test rhythm pattern",
            "tags": ["test"],
            "complexity": 1.0,
            "style": "basic"
        }
        
        test_note_pattern = {
            "id": "pattern_1",  # Unique ID for testing
            "index": 0,
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
                default_duration=1.0,
                index=0
            )
            .model_dump(),
            "description": "Test pattern",
            "tags": ["test"],
            "complexity": 0.5,
            "style": "basic"
        }

        # Insert test data into the database
        await db.rhythm_patterns.insert_one(test_rhythm_pattern)
        await db.note_patterns.insert_one(test_note_pattern)

        # Invalid data test
        try:
            with pytest.raises(ValueError, match=r"Value error, Chords list cannot be empty"):
                await db.chord_progressions.insert_one(ChordProgression(
                    id="invalid_id",
                    name="Invalid Chord Progression",
                    chords=[],  # This should trigger the validation error
                    key="C",
                    scale_type=ScaleType.MAJOR.value,
                    scale_info={"root": {"note_name": "C", "octave": 4}, "scale_type": ScaleType.MAJOR.value}
                ).dict())
        except ValueError as e:
            logger.error(f'Error raised: {e}')
            logger.error(f'Error message: {e.args[0]}')  # Capture actual error message
            raise
        yield db
        client.close()  # Ensure client is closed after all operations

    except Exception as e:
        print(f"An error occurred: {e}")
        raise

@pytest.mark.asyncio
async def test_fetch_chord_progressions(clean_test_db) -> None:
    """Test fetching chord progressions."""
    logger.debug('Starting test for fetching chord progressions.')
    result = await fetch_chord_progressions(clean_test_db)
    logger.debug(f'Fetched chord progressions: {result}')
    logger.debug(f'Asserting fetched chord progressions: {result}')
    logger.debug(f'Expected structure: list of ChordProgression objects')
    logger.debug(f'Fetched progression: {result[0] if result else None}')
    assert len(result) > 0
    assert isinstance(result[0], ChordProgression)
    assert result[0].id == 'progression_1'
    assert result[0].name == 'I-IV-V'
    assert result[0].key == 'C'
    assert result[0].scale_type == ScaleType.MAJOR
    assert len(result[0].chords) > 0
    for chord in result[0].chords:
        assert isinstance(chord, Chord)
        assert chord.quality == ChordQualityType.MAJOR

    # Update scale types and chord qualities in the fetched data
    for progression in result:
        progression.scale_type = 'MAJOR'  # Update scale type
        for chord in progression.chords:
            chord.quality = 'MAJOR'  # Update chord quality

    logger.debug(f'Updated chord progressions: {result}')
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id(clean_test_db) -> None:
    """Test fetching a chord progression by ID with correct scale types."""
    db = setup_test_data
    progression_id = 'I-IV-V'
    test_pattern = {
        "id": progression_id,
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
    logger.debug(f'Test Pattern Data: {test_pattern}')
    result = await fetch_chord_progression_by_id(progression_id, db)
    logger.debug(f'Asserting fetched chord progression by ID: {result}')
    logger.debug(f'Expected structure: ChordProgression object')
    logger.debug(f'Fetched progression: {result}')
    assert result is not None
    assert isinstance(result, ChordProgression)
    assert result.id == progression_id
    assert result.name == 'I-IV-V'
    assert result.key == 'C'
    assert result.scale_type == 'MAJOR'
    assert len(result.chords) > 0
    for chord in result.chords:
        assert isinstance(chord, Chord)
        assert chord.quality == ChordQualityType.MAJOR

    logger.debug(f'Fetched chord progression by ID: {result}')

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(clean_test_db):
    """Test fetching rhythm patterns."""
    client = TestClient(app)
    
    # Insert a test rhythm pattern with ID 'test_1'
    test_pattern = RhythmPattern(
        id='test_1',
        name='Test Pattern',
        data=RhythmPatternData(
            notes=[
                RhythmNote(
                    position=0.0,
                    duration=1.0,
                    velocity=100,
                    is_rest=False
                )
            ],
            time_signature='4/4',
            swing_ratio=0.67,
            default_duration=1.0,
            total_duration=1.0,
            groove_type='straight'
        ),
        description='Test rhythm pattern',
        tags=['test'],
        complexity=1.0,
        style='basic'
    )
    await clean_test_db.insert_one(test_pattern.dict())
    
    # Fetch the rhythm pattern by ID
    response = client.get('/api/rhythm_patterns/test_1/')
    assert response.status_code == 200
    assert response.json()['name'] == 'Test Pattern'

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(clean_test_db) -> None:
    """Test fetching rhythm pattern by ID."""
    pattern_id = "test_1"
    result = await fetch_rhythm_pattern_by_id(pattern_id, clean_test_db)
    logger.debug(f'Fetched rhythm pattern: {result}')
    logger.debug(f'Asserting fetched rhythm pattern: {result}')
    logger.debug(f'Expected structure: RhythmPattern object')
    logger.debug(f'Fetched pattern: {result}')
    assert result is not None
    assert isinstance(result, RhythmPattern)


@pytest.mark.asyncio
async def test_fetch_note_patterns(clean_test_db) -> None:
    print("\n--- Starting test_fetch_note_patterns ---")
    print(f"\n--- Current Note Patterns in Database: {await clean_test_db.note_patterns.find().to_list(None)} ---")
    db = clean_test_db
    test_pattern = {
        "id": "pattern_2",
        "index": 0,
        "name": "Test Pattern",
        "data": NotePatternData(
            notes=[
                {
                    "note_name": "C",
                    "octave": 4,
                    "duration": 1.0,
                    "velocity": 100
                },
                {
                    "note_name": "E",
                    "octave": 4,
                    "duration": 1.0,
                    "velocity": 100
                },
                {
                    "note_name": "G",
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
            default_duration=1.0,
            index=0
        ),
        "description": "Test Pattern Description",
        "tags": ["test"],
        "complexity": 0.5,
    }
    
    print(f"\n--- Test Pattern Before Insertion: {test_pattern} ---\n")
    await db.note_patterns.insert_one(test_pattern)

    # Log the contents of the chord_progressions collection
    chord_progressions = await db.chord_progressions.find().to_list(None)
    logger.debug(f'Chord Progressions in Database: {chord_progressions}')

    # Log the contents of the note_patterns collection
    note_patterns = await db.note_patterns.find().to_list(None)
    logger.debug(f'Note Patterns in Database: {note_patterns}')

    return db

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(setup_test_data):
    """Test fetching a note pattern by ID."""
    db = setup_test_data
    pattern_id = 'pattern_2'
    result = await fetch_note_pattern_by_id(pattern_id, db)
    logger.debug(f'Asserting fetched note pattern by ID: {result}')
    assert result is not None
    assert result.id == pattern_id
    assert result.name == 'Test Pattern'
    assert len(result.data) > 0
    logger.debug(f'Fetched note pattern by ID: {result}')

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(clean_test_db) -> None:
    db = clean_test_db
    # Insert invalid data directly into the test database
    try:
        with pytest.raises(ValueError, match=r"Value error, Chords list cannot be empty"):
            await db.chord_progressions.insert_one(ChordProgression(
                id="invalid_id",
                name="Invalid Chord Progression",
                chords=[],  # This should trigger the validation error
                key="C",
                scale_type=ScaleType.MAJOR.value,
                scale_info={"root": {"note_name": "C", "octave": 4}, "scale_type": ScaleType.MAJOR.value}
            ).dict())
    except ValueError as e:
        logger.error(f'Error raised: {e}')
        logger.error(f'Error message: {e.args[0]}')  # Capture actual error message
        raise

@pytest.mark.asyncio
async def test_fetch_chord_progressions_with_new_data(clean_test_db) -> None:
    db = clean_test_db
    result = await fetch_chord_progressions(db)
    logger.debug(f'Fetched chord progressions with new data: {result}')
    logger.debug(f'Asserting fetched chord progressions with new data: {result}')
    logger.debug(f'Expected structure: list of ChordProgression objects')
    logger.debug(f'Fetched progression: {result[0]}')
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(clean_test_db) -> None:
    db = clean_test_db
    logger.debug(f'Current note patterns in the database before fetching: {await db.note_patterns.find().to_list(None)}')
    logger.debug(f'Fetching note patterns from the database...')
    result = await fetch_note_patterns(db)
    if not result:
        logger.error('No note patterns fetched from the database.');
        assert False, 'No note patterns found.'
    logger.debug(f'Fetched note patterns: {result}')
    logger.debug(f'Asserting fetched note patterns: {result}')
    logger.debug(f'Expected structure: list of NotePattern objects')
    logger.debug(f'Fetched pattern: {result[0]}')
    print(f'--- Fetched Note Patterns: ---')
    print(result)
    print(f'--- Fetched Note Patterns Structure: ---')
    for pattern in result:
        print(pattern.__dict__)
    print(f'--- Fetched Note Patterns Structure (Explicit): ---')
    for pattern in result:
        print(f"ID: {pattern.id}")
        print(f"Name: {pattern.name}")
        print(f"Data: {pattern.data}")
        print(f"Description: {pattern.description}")
        print(f"Tags: {pattern.tags}")
        print(f"Complexity: {pattern.complexity}")
        print(f"Style: {pattern.style}")
    logger.debug(f'Fetched note pattern: {result[0]}')
    logger.debug(f'Fetched pattern types: {[type(getattr(result[0], field)) for field in result[0].__dict__]}')
    logger.debug(f'Expected types: [Optional[str], str, str, List[str], Optional[float], Optional[List[Note]], Optional[Union[NotePatternData, List[Union[int, List[int]]]]], Optional[str], Optional[bool]]')
    assert len(result) > 0
    logger.debug(f'Asserting fetched note patterns: {result}')
    logger.debug(f'Expected structure: list of NotePattern objects')
    logger.debug(f'Fetched pattern: {result[0]}')
    assert isinstance(result[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_new_data(clean_test_db) -> None:
    """Test fetching rhythm patterns with new data."""
    db = clean_test_db

    test_pattern = {
        "id": "test_2",
        "name": "Test Pattern",
        "index": 0,
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

    print(f"\n--- Test Pattern Data Structure: {test_pattern['data']} ---")
    # Insert directly into collection
    await db.rhythm_patterns.insert_one(test_pattern)
    logger.debug(f'Current rhythm patterns in the database before fetching: {await db.rhythm_patterns.find().to_list(None)}')
    result = await fetch_rhythm_patterns(db)
    logger.debug(f'Fetched rhythm patterns with new data: {result}')
    logger.debug(f'Asserting fetched rhythm patterns with new data: {result}')
    logger.debug(f'Expected structure: list of RhythmPattern objects')
    logger.debug(f'Fetched pattern: {result[0]}')
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
    logger.debug(f'Asserting processed chord data: {processed}')
    logger.debug(f'Expected structure: dictionary with quality as ChordQualityType.MAJOR.value')
    logger.debug(f'Processed data: {processed}')
    assert processed['quality'] == ChordQualityType.MAJOR.value  # Compare with enumeration value

from fastapi.testclient import TestClient
from main import app

@pytest.fixture
async def setup_test_data(clean_test_db):
    """Setup test data with correct scale types."""
    db = clean_test_db
    # Insert the chord progressions with correct scale type
    test_progressions = [
        {
            'id': 'I-IV-V',
            'index': 0,
            'name': 'I-IV-V',
            'chords': [
                {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'F', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'},
            ],
            'key': 'C',
            'scale_type': 'MAJOR',
            'tags': ['preset'],
            'complexity': 1.0,
        },
        {
            'id': 'Pop Ballad_I-V-vi-IV',
            'index': 1,
            'name': 'Pop Ballad_I-V-vi-IV',
            'chords': [
                {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'A', 'octave': 4}, 'quality': 'MINOR'},
                {'root': {'note_name': 'F', 'octave': 4}, 'quality': 'MAJOR'},
            ],
            'key': 'C',
            'scale_type': 'MAJOR',
            'tags': ['preset'],
            'complexity': 1.0,
        },
    ]
    await db.chord_progressions.insert_many(test_progressions)
    # Insert the test note pattern
    test_pattern = {
        "id": "pattern_2",
        "index": 0,
        "name": "Test Pattern",
        "data": NotePatternData(
            notes=[
                {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100}
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
    }
    
    print(f"\n--- Test Pattern Before Insertion: {test_pattern} ---\n")
    await db.note_patterns.insert_one(test_pattern)

    # Log the contents of the chord_progressions collection
    chord_progressions = await db.chord_progressions.find().to_list(None)
    logger.debug(f'Chord Progressions in Database: {chord_progressions}')

    # Log the contents of the note_patterns collection
    note_patterns = await db.note_patterns.find().to_list(None)
    logger.debug(f'Note Patterns in Database: {note_patterns}')

    return db

@pytest.mark.asyncio
async def test_create_rhythm_pattern():
    client = TestClient(app)
    response = client.post("/api/rhythm_patterns/", json={
        "name": "Test Rhythm Pattern",
        "description": "A test rhythm pattern",
        "tags": ["test"],
        "complexity": 0.5
    })
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_read_rhythm_pattern(clean_test_db):
    client = TestClient(app)
    
    # Insert a rhythm pattern with ID 'test_1'
    test_pattern = RhythmPattern(
        id='test_1',
        name='Test Pattern',
        data=RhythmPatternData(
            notes=[
                RhythmNote(
                    position=0.0,
                    duration=1.0,
                    velocity=100,
                    is_rest=False
                )
            ],
            time_signature='4/4',
            swing_ratio=0.67,
            default_duration=1.0,
            total_duration=1.0,
            groove_type='straight'
        ),
        description='Test rhythm pattern',
        tags=['test'],
        complexity=1.0,
        style='basic'
    )
    await clean_test_db.rhythm_patterns.insert_one(test_pattern.model_dump())
    
    # Fetch the rhythm pattern by ID
    response = client.get("/api/rhythm_patterns/test_1/")
    assert response.status_code == 200
    assert response.json()['name'] == 'Test Pattern'

@pytest.mark.asyncio
async def test_update_rhythm_pattern():
    client = TestClient(app)
    response = client.put("/api/rhythm_patterns/1/", json={
        "name": "Updated Rhythm Pattern",
        "description": "An updated test rhythm pattern",
        "tags": ["test"],
        "complexity": 0.7
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Rhythm Pattern"

@pytest.mark.asyncio
async def test_delete_rhythm_pattern():
    client = TestClient(app)
    response = client.delete("/api/rhythm_patterns/1/")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_create_chord_progression():
    client = TestClient(app)
    response = client.post("/api/chord_progressions/", json={
        "name": "Test Chord Progression",
        "chords": [],
        "key": "C",
        "scale_type": "MAJOR",
        "complexity": 0.5
    })
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_read_chord_progression():
    client = TestClient(app)
    # Use the correct ID for the chord progression
    response = client.get("/api/chord_progressions/progression_1/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_chord_progression():
    client = TestClient(app)
    response = client.put("/api/chord_progressions/progression_1/", json={
        "name": "Updated Chord Progression",
        "chords": [],
        "key": "C",
        "scale_type": "MAJOR",
        "complexity": 0.7
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_chord_progression():
    client = TestClient(app)
    response = client.delete("/api/chord_progressions/progression_1/")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_create_note_pattern():
    client = TestClient(app)
    test_pattern = {
        "name": "Test Note Pattern",
        "pattern": ["C", "D", "E", "F", "G", "A", "B"],  # Include a valid pattern
        "pattern_type": "melody",   
        "description": "A test note pattern",
        "tags": ["test"],
        "complexity": 0.5
    }  
    
    # Create the pattern and verify it was created
    create_response = client.post("/api/note_patterns/", json=test_pattern)
    logger.debug("Create Response: %s", create_response.json())
    assert create_response.status_code == 201, f"Failed to create note pattern: {create_response.text}"
    
    # Verify the pattern exists
    get_response = client.get(f"/api/note_patterns/{create_response.json()['id']}/")
    logger.debug("Get Response: %s", get_response.json())
    assert get_response.status_code == 200, f"Failed to get created pattern: {get_response.text}"
    
    # Now delete the pattern
    delete_response = client.delete(f"/api/note_patterns/{create_response.json()['id']}/")
    logger.debug("Delete Response: %s", delete_response.json())
    assert delete_response.status_code == 204, f"Failed to delete pattern: {delete_response.text}"
    
    # Verify the pattern was deleted
    get_after_delete = client.get(f"/api/note_patterns/{create_response.json()['id']}/")
    logger.debug("Get After Delete Response: %s", get_after_delete.json())
    assert get_after_delete.status_code == 404, "Pattern still exists after deletion"

@pytest.mark.asyncio
async def test_read_note_pattern():
    client = TestClient(app)
    # Use the correct ID for the note pattern
    response = client.get("/api/note_patterns/pattern_2/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_note_pattern():
    client = TestClient(app)
    response = client.put("/api/note_patterns/pattern_2/", json={
        "name": "Updated Note Pattern",
        "notes": [],
        "pattern_type": "melody",
        "description": "An updated test note pattern",
        "tags": ["test"],
        "complexity": 0.7
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_note_pattern():
    client = TestClient(app)
    # First, ensure the pattern doesn't exist
    client.delete("/api/note_patterns/pattern_2/")
    
    # Create the test pattern
    test_pattern = {
        "id": "pattern_2",
        "name": "Test Note Pattern 2",
        "data": {
            "notes": [{"note_name": "D", "octave": 4, "duration": 1.0, "velocity": 100}],
            "intervals": [2, 2, 1, 2, 2, 2, 1],
            "duration": 1.0, 
            "velocity": 100, 
            "direction": "up",
            "octave_range": [4, 5],
            "default_duration": 1.0,
            "index": 0,
            "position": 0
        },
        "description": "Another test pattern",
        "tags": ["test"],
        "complexity": 0.5,
        "style": "basic"
    }
    
    # Create the pattern and verify it was created
    create_response = client.post("/note_patterns/", json=test_pattern)
    assert create_response.status_code == 201, f"Failed to create note pattern: {create_response.text}"
    
    # Verify the pattern exists
    get_response = client.get("/note_patterns/pattern_2/")
    assert get_response.status_code == 200, f"Failed to get created pattern: {get_response.text}"
    
    # Now delete the pattern
    delete_response = client.delete("/note_patterns/pattern_2/")
    assert delete_response.status_code == 204, f"Failed to delete pattern: {delete_response.text}"
    
    # Verify the pattern was deleted
    get_after_delete = client.get("/note_patterns/pattern_2/")
    assert get_after_delete.status_code == 404, "Pattern still exists after deletion"

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_logging(clean_test_db) -> None:
    db = clean_test_db
    logger.debug(f'Current note patterns in the database before fetching: {await db.note_patterns.find().to_list(None)}')
    logger.debug(f'Fetching note patterns from the database...')
    result = await fetch_note_patterns(db)
    if not result:
        logger.error('No note patterns fetched from the database.');
        assert False, 'No note patterns found.'
    logger.debug(f'Fetched note patterns: {result}')
    logger.debug(f'Asserting fetched note patterns: {result}')
    logger.debug(f'Expected structure: list of NotePattern objects')
    logger.debug(f'Fetched pattern: {result[0]}')
    print(f'--- Fetched Note Patterns: ---')
    print(result)
    print(f'--- Fetched Note Patterns Structure: ---')
    for pattern in result:
        print(pattern.__dict__)
    print(f'--- Fetched Note Patterns Structure (Explicit): ---')
    for pattern in result:
        print(f"ID: {pattern.id}")
        print(f"Name: {pattern.name}")
        print(f"Data: {pattern.data}")
        print(f"Description: {pattern.description}")
        print(f"Tags: {pattern.tags}")
        print(f"Complexity: {pattern.complexity}")
        print(f"Style: {pattern.style}")
    logger.debug(f'Fetched note pattern: {result[0]}')
    logger.debug(f'Fetched pattern types: {[type(getattr(result[0], field)) for field in result[0].__dict__]}')
    logger.debug(f'Expected types: [Optional[str], str, str, List[str], Optional[float], Optional[List[Note]], Optional[Union[NotePatternData, List[Union[int, List[int]]]]], Optional[str], Optional[bool]]')
    assert len(result) > 0
    logger.debug(f'Asserting fetched note patterns: {result}')
    logger.debug(f'Expected structure: list of NotePattern objects')
    logger.debug(f'Fetched pattern: {result[0]}')
    assert isinstance(result[0], NotePattern)

    test_pattern = {
        "id": "pattern_2",
        "index": 0,
        "name": "Test Pattern",
        "data": NotePatternData(
            notes=[
                {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100}
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
    }
    print(f"\n--- Test Pattern Data Structure: {test_pattern['data']} ---")
    # Insert directly into collection
    await db.note_patterns.insert_one(test_pattern)
    logger.debug(f'Current note patterns in the database before fetching: {await db.note_patterns.find().to_list(None)}')
    logger.debug(f'Fetching note patterns from the database...')
    result = await fetch_note_patterns(db)
    if not result:
        logger.error('No note patterns fetched from the database.');
        assert False, 'No note patterns found.'
    logger.debug(f'Fetched note patterns: {result}')
    logger.debug(f'Asserting fetched note patterns: {result}')
    logger.debug(f'Expected structure: list of NotePattern objects')
    logger.debug(f'Fetched pattern: {result[0]}')
    print(f'--- Fetched Note Patterns: ---')
    print(result)
    print(f'--- Fetched Note Patterns Structure: ---')
    for pattern in result:
        print(pattern.__dict__)
    print(f'--- Fetched Note Patterns Structure (Explicit): ---')
    for pattern in result:
        print(f"ID: {pattern.id}")
        print(f"Name: {pattern.name}")
        print(f"Data: {pattern.data}")
        print(f"Description: {pattern.description}")
        print(f"Tags: {pattern.tags}")
        print(f"Complexity: {pattern.complexity}")
        print(f"Style: {pattern.style}")
    logger.debug(f'Fetched note pattern: {result[0]}')
    logger.debug(f'Fetched pattern types: {[type(getattr(result[0], field)) for field in result[0].__dict__]}')
    logger.debug(f'Expected types: [Optional[str], str, str, List[str], Optional[float], Optional[List[Note]], Optional[Union[NotePatternData, List[Union[int, List[int]]]]], Optional[str], Optional[bool]]')
    assert len(result) > 0
    logger.debug(f'Asserting fetched note patterns: {result}')
    logger.debug(f'Expected structure: list of NotePattern objects')
    logger.debug(f'Fetched pattern: {result[0]}')
    assert isinstance(result[0], NotePattern)

    for note_data in test_pattern['data']['notes']:
        logger.debug(f'Creating Note with data: {note_data}')
        note = Note(**note_data)
        logger.debug(f'Created Note: {note}')

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern():
    db = clean_test_db
    # Insert the test rhythm pattern
    db.rhythm_patterns.insert_one({
        "id": "test_basic_rhythm",
        "index": 1,
        "pattern": [1, -1, 1, -1],
        "tags": ["test", "basic", "rhythm"],
        "complexity": 0.2,
        "description": "A simple on-off rhythm pattern.",
        "notes": [
            {"position": 0, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 1, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 2, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 3, "duration": 1.0, "velocity": 100, "is_rest": False}
        ]
    })

    rhythm_pattern = db.rhythm_patterns.find_one({"id": "test_basic_rhythm"})
    assert rhythm_pattern is not None
    assert rhythm_pattern["pattern"] == [1, -1, 1, -1]
    assert rhythm_pattern["description"] == "A simple on-off rhythm pattern."

@pytest.mark.asyncio
async def test_fetch_note_pattern():
    db = clean_test_db
    # Insert the test note pattern
    db.note_patterns.insert_one({
        "id": "test_simple_triad",
        "index": 1,
        "pattern": [0, 2, 4],
        "tags": ["test", "triad", "basic"],
        "complexity": 0.5,
        "description": "A simple triad pattern."
    })

    note_pattern = db.note_patterns.find_one({"id": "test_simple_triad"})
    assert note_pattern is not None
    assert note_pattern["pattern"] == [0, 2, 4]
    assert note_pattern["description"] == "A simple triad pattern."

@pytest.mark.asyncio
async def test_fetch_chord_progression():
    db = clean_test_db
    # Insert the test chord progression
    db.chord_progressions.insert_one({
        "id": "test_i_iv_v",
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

    chord_progression = db.chord_progressions.find_one({"id": "test_i_iv_v"})
    assert chord_progression is not None
    assert chord_progression["description"] == "A common chord progression in popular music."