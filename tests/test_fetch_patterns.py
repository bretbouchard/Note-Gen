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
        try:
            with pytest.raises(ValueError, match="Chords cannot be empty."):
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
    result = await fetch_chord_progressions(clean_test_db)
    logger.debug(f'Fetched chord progressions: {result}')
    logger.debug(f'Asserting fetched chord progressions: {result}')
    logger.debug(f'Expected structure: list of ChordProgression objects')
    logger.debug(f'Fetched progression: {result[0]}')
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
async def test_fetch_chord_progression_by_id(setup_test_data):
    """Test fetching a chord progression by ID with correct scale types."""
    db = setup_test_data
    progression_id = 'progression_1'
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
async def test_fetch_rhythm_patterns(clean_test_db) -> None:
    db = clean_test_db
    result = await fetch_rhythm_patterns(db)
    logger.debug(f'Fetched rhythm patterns: {result}')
    logger.debug(f'Asserting fetched rhythm patterns: {result}')
    logger.debug(f'Expected structure: list of RhythmPattern objects')
    logger.debug(f'Fetched pattern: {result[0]}')
    assert result is not None

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
            default_duration=1.0
        ).model_dump(),
        "description": "Test pattern",
        "tags": ["test"],
        "complexity": 0.5,
        "style": "basic"
    }

    print(f"\n=============================================")
    print(f"--- Inserting Test Pattern: {test_pattern} ---")
    print(f"=============================================")
    print(f"\n--- Test Pattern Data Structure: {test_pattern['data']} ---")
    await db.note_patterns.insert_one(test_pattern)
    print(f"\n--- Note Patterns After Insertion: {await db.note_patterns.find().to_list(None)} ---")
    logger.debug(f'Fetching note patterns from the database...')
    result = await fetch_note_patterns(db)
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
    print(f'Asserting instance type: {type(result[0])}, expected: NotePattern')
    assert isinstance(result[0], NotePattern)
    print(f'Asserting name: {result[0].name}, expected: Test Note Pattern')
    assert result[0].name == 'Test Note Pattern'
    print(f'Asserting description: {result[0].description}, expected: Test pattern')
    assert result[0].description == 'Test pattern'
    print(f'Asserting complexity: {result[0].complexity}, expected: 0.5')
    assert result[0].complexity == 0.5
    print(f'Asserting notes length: {len(result[0].data.notes)}, expected: > 0')
    assert len(result[0].data.notes) > 0
    for note in result[0].data.notes:
        print(f'Asserting note: {note}, expected type: Note')
        assert isinstance(note, Note)
        assert note.note_name in ['C', 'D', 'E', 'F', 'G', 'A', 'B']

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(clean_test_db) -> None:
    """Test fetching note pattern by ID."""
    pattern_id = "pattern_1"
    result = await fetch_note_pattern_by_id(pattern_id, clean_test_db)
    logger.debug(f'Fetched note pattern by ID: {result}')
    logger.debug(f'Fetched note pattern structure: {result.__dict__ if result else None}')
    print(f'--- Fetched Note Pattern Structure (Explicit): ---')
    if result:
        print(f"ID: {result.id}")
        print(f"Name: {result.name}")
        print(f"Data: {result.data}")
        print(f"Description: {result.description}")
        print(f"Tags: {result.tags}")
        print(f"Complexity: {result.complexity}")
        print(f"Style: {result.style}")
    logger.debug(f'Fetched note pattern: {result}')
    logger.debug(f'Fetched pattern types: {[type(getattr(result, field)) for field in result.__dict__]}')
    logger.debug(f'Expected types: [Optional[str], str, str, List[str], Optional[float], Optional[List[Note]], Optional[Union[NotePatternData, List[Union[int, List[int]]]]], Optional[str], Optional[bool]]')
    assert result is not None
    assert isinstance(result, NotePattern)

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(clean_test_db) -> None:
    db = clean_test_db
    # Insert invalid data directly into the test database
    try:
        with pytest.raises(ValueError, match="Chords cannot be empty."):
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
    
    # Insert the test note pattern
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
            default_duration=1.0
        ).model_dump(),
        "description": "Test pattern",
        "tags": ["test"],
        "complexity": 0.5,
        "style": "basic"
    }
    await db.note_patterns.delete_many({})  # Clean the note_patterns collection
    await db.note_patterns.insert_one(test_pattern)  # Insert the test pattern
    return db

import pytest
from httpx import AsyncClient
from src.note_gen.main import app
from src.note_gen.models.note_pattern import NotePattern, NotePatternResponse
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternResponse
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionResponse

@pytest.mark.asyncio
async def test_create_rhythm_pattern():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/rhythm_patterns/", json={
            "name": "Test Rhythm Pattern",
            "description": "A test rhythm pattern",
            "tags": ["test"],
            "complexity": 0.5
        })
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_read_rhythm_pattern():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Assuming a rhythm pattern with ID '1' exists
        response = await client.get("/rhythm_patterns/1/")
    assert response.status_code == 200
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_update_rhythm_pattern():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/rhythm_patterns/1/", json={
            "name": "Updated Rhythm Pattern",
            "description": "An updated test rhythm pattern",
            "tags": ["test"],
            "complexity": 0.7
        })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Rhythm Pattern"

@pytest.mark.asyncio
async def test_delete_rhythm_pattern():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/rhythm_patterns/1/")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_create_chord_progression():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/chord_progressions/", json={
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
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Assuming a chord progression with ID '1' exists
        response = await client.get("/chord_progressions/1/")
    assert response.status_code == 200
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_update_chord_progression():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/chord_progressions/1/", json={
            "name": "Updated Chord Progression",
            "chords": [],
            "key": "C",
            "scale_type": "MAJOR",
            "complexity": 0.7
        })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Chord Progression"

@pytest.mark.asyncio
async def test_delete_chord_progression():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/chord_progressions/1/")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_create_note_pattern():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/note_patterns/", json={
            "name": "Test Note Pattern",
            "notes": [],
            "pattern_type": "melody",
            "description": "A test note pattern",
            "tags": ["test"],
            "complexity": 0.5
        })
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_read_note_pattern():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Assuming a note pattern with ID '1' exists
        response = await client.get("/note_patterns/1/")
    assert response.status_code == 200
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_update_note_pattern():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/note_patterns/1/", json={
            "name": "Updated Note Pattern",
            "notes": [],
            "pattern_type": "melody",
            "description": "An updated test note pattern",
            "tags": ["test"],
            "complexity": 0.7
        })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Note Pattern"

@pytest.mark.asyncio
async def test_delete_note_pattern():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/note_patterns/1/")
    assert response.status_code == 204