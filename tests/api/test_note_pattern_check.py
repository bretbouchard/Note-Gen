import pytest
from motor.motor_asyncio import AsyncIOMotorClient
import httpx
from main import app
from src.note_gen.models.note import Note
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import (
    RhythmPattern,
    RhythmPatternData,
    RhythmNote
)
from src.note_gen.database import get_db, MONGO_URL, TEST_DB_NAME, MONGO_SETTINGS
from bson import ObjectId
import asyncio

# Create a new event loop for the tests
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Setup test database
@pytest.fixture(autouse=True)
async def test_db():
    client = AsyncIOMotorClient(MONGO_URL, **MONGO_SETTINGS)
    db = client[TEST_DB_NAME]
    
    # Override the get_db dependency
    async def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Clean up before test
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    
    yield db
    
    # Clean up after test
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    app.dependency_overrides.clear()
    client.close()

@pytest.fixture
async def client(test_db):
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
        yield c

# Consolidated tests for note pattern functionality
@pytest.mark.asyncio
async def test_note_pattern_functionality(client):
    # Test create note pattern
    note_pattern = NotePattern(
        name='Test Create Pattern',
        description='Test pattern',
        tags=['basic'],
        data=[0, 4, 7],  # C major triad intervals
        notes=[
            Note(note_name='C', octave=4),
            Note(note_name='E', octave=4),
            Note(note_name='G', octave=4)
        ],
        is_test=True
    )
    response = await client.post('/note-patterns', json=note_pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()
    assert created_pattern['name'] == note_pattern.name
    assert len(created_pattern['data']) == len(note_pattern.data)

    # Test invalid note pattern
    invalid_pattern = NotePattern(
        name='Invalid Pattern',
        description='Invalid pattern',
        tags=['basic'],
        data=[-1],  # Invalid interval
        notes=[Note(note_name='C', octave=4)],
        is_test=True
    )
    response = await client.post('/note-patterns', json=invalid_pattern.model_dump())
    assert response.status_code == 422  # Validation error

    # Test create duplicate note pattern
    note_pattern = NotePattern(
        name='Test Duplicate Pattern',
        description='Test pattern',
        tags=['basic'],
        data=[0],  # Simple single note pattern
        notes=[Note(note_name='C', octave=4)],
        is_test=True
    )
    response = await client.post('/note-patterns', json=note_pattern.model_dump())
    assert response.status_code == 201
    
    # Try to create duplicate with same name
    response = await client.post('/note-patterns', json=note_pattern.model_dump())
    assert response.status_code == 409

    # Test create and delete note pattern
    test_pattern = NotePattern(
        name='Test Create Delete Pattern',
        description='Test pattern',
        tags=['basic'],
        data={
            "notes": [
                {
                    "note_name": "C",
                    "octave": 4,
                    "duration": 1.0,
                    "velocity": 100
                },
                {
                    "note_name": "D",
                    "octave": 4,
                    "duration": 1.0,
                    "velocity": 100
                },
                {
                    "note_name": "E",
                    "octave": 4,
                    "duration": 1.0,
                    "velocity": 100
                }
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
        complexity=0.5,
        style="basic",
        is_test=True
    )
    
    # Create pattern
    response = await client.post('/note-patterns', json=test_pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()
    pattern_id = created_pattern['id']
    
    # Delete pattern
    response = await client.delete(f'/note-patterns/{pattern_id}')
    assert response.status_code == 204
    
    # Verify pattern is deleted
    response = await client.get(f'/note-patterns/{pattern_id}')
    assert response.status_code == 404

    # Test create and delete rhythm pattern
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )

    pattern_id = str(ObjectId())
    rhythm_pattern = RhythmPattern(
        id=pattern_id,
        name='Test Create Delete Pattern',
        description='Basic quarter note pattern',
        tags=['basic'],
        complexity=1.0,
        data=rhythm_data,
        is_test=True
    )

    # Create the pattern
    response = await client.post(
        '/rhythm-patterns',
        json=rhythm_pattern.model_dump(exclude_none=True)
    )
    assert response.status_code == 201
    
    # Verify pattern was created
    response = await client.get(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 200
    
    # Delete the pattern
    response = await client.delete(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 204

    # Test get rhythm pattern
    pattern_id = str(ObjectId())
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )

    rhythm_pattern = RhythmPattern(
        id=pattern_id,
        name='Test Get Pattern',
        description='Basic quarter note pattern',
        tags=['basic'],
        complexity=1.0,
        data=rhythm_data,
        is_test=True
    )

    # Insert directly to database
    await test_db.rhythm_patterns.insert_one(rhythm_pattern.model_dump(exclude_none=True))
    
    # Get the pattern
    response = await client.get(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 200

    # Test get note patterns
    response = await client.get('/note-patterns')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    data = response.json()
    assert len(data) > 0  # Ensure the list is not empty
    assert data[0]['name'] is not None  # Check if the name is not None

    # Test invalid rhythm pattern id
    response = await client.get('/rhythm-patterns/invalid_id')
    assert response.status_code == 404

    # Test create duplicate rhythm pattern
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )

    pattern = RhythmPattern(
        id=str(ObjectId()),
        name='Test Duplicate Pattern',
        description='Basic quarter note pattern',
        tags=['basic'],
        complexity=1.0,
        data=rhythm_data,
        is_test=True
    )

    # Create first pattern
    response = await client.post(
        '/rhythm-patterns',
        json=pattern.model_dump(exclude_none=True)
    )
    assert response.status_code == 201

    # Try to create duplicate
    response = await client.post(
        '/rhythm-patterns',
        json=pattern.model_dump(exclude_none=True)
    )
    assert response.status_code == 409  # Conflict
