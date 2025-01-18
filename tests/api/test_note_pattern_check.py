import pytest
from motor.motor_asyncio import AsyncIOMotorClient
import httpx
from main import app
from src.note_gen.models.note import Note
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.database import get_db, MONGO_URL, TEST_DB_NAME, MONGO_SETTINGS
from src.note_gen.models.rhythm_pattern import (
    RhythmPattern,
    RhythmPatternData,
    RhythmNote
)
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
async def setup_database(test_db):
    # Setup code to insert test data into the database
    note_pattern = NotePattern(
        name='Test Base Pattern',
        description='Base test pattern',
        tags=['basic'],
        data=[0],  # Simple single note pattern
        notes=[Note(note_name='C', octave=4)],
        is_test=True
    )
    pattern_dict = note_pattern.model_dump()
    pattern_dict["_id"] = ObjectId()
    pattern_dict.pop("id", None)
    await test_db.note_patterns.insert_one(pattern_dict)
    yield

@pytest.mark.asyncio
async def test_create_note_pattern(test_db) -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
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
        print(response.json())  # Debug output of validation errors
        assert response.status_code == 201
        created_pattern = response.json()
        assert created_pattern['name'] == note_pattern.name
        assert len(created_pattern['data']) == len(note_pattern.data)

@pytest.mark.asyncio
async def test_invalid_note_pattern(test_db) -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # Test with invalid data format
        invalid_pattern = NotePattern(
            name='Invalid Pattern',
            description='Invalid pattern',
            tags=['basic'],
            data=[-1],  # Invalid interval
            notes=[Note(note_name='C', octave=4)],
            is_test=True
        )
        response = await client.post('/note-patterns', json=invalid_pattern.model_dump())
        print(response.json())  # Debug output of validation errors
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_create_duplicate_note_pattern(test_db) -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # Create first pattern
        note_pattern = NotePattern(
            name='Test Duplicate Pattern',
            description='Test pattern',
            tags=['basic'],
            data=[0],  # Simple single note pattern
            notes=[Note(note_name='C', octave=4)],
            is_test=True
        )
        response = await client.post('/note-patterns', json=note_pattern.model_dump())
        print(response.json())  # Debug output of validation errors
        assert response.status_code == 201

        # Try to create duplicate with same name
        response = await client.post('/note-patterns', json=note_pattern.model_dump())
        print(response.json())  # Debug output of validation errors
        assert response.status_code == 409

@pytest.mark.asyncio
async def test_create_and_delete_note_pattern(test_db) -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # Create a test note pattern
        test_pattern = NotePattern(
            name='Test Create Delete Pattern',
            description='Test pattern',
            tags=['basic'],
            data=[0, 2, 4],  # Simple triad pattern
            notes=[
                Note(note_name='C', octave=4),
                Note(note_name='D', octave=4),
                Note(note_name='E', octave=4)
            ],
            is_test=True
        )
        
        # Create pattern
        response = await client.post('/note-patterns', json=test_pattern.model_dump())
        assert response.status_code == 201
        created_pattern = response.json()
        
        # Delete pattern
        pattern_id = created_pattern['id']
        response = await client.delete(f'/note-patterns/{pattern_id}')
        assert response.status_code == 204
        
        # Verify pattern is deleted
        response = await client.get(f'/note-patterns/{pattern_id}')
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_and_delete_rhythm_pattern(test_db) -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
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

@pytest.mark.asyncio
async def test_get_rhythm_pattern(test_db) -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
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

@pytest.mark.asyncio
async def test_get_note_patterns() -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.get('/note-patterns')
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        data = response.json()
        assert len(data) > 0  # Ensure the list is not empty
        assert data[0]['name'] is not None  # Check if the name is not None

@pytest.mark.asyncio
async def test_invalid_rhythm_pattern_id() -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.get('/rhythm-patterns/invalid_id')
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_duplicate_rhythm_pattern(test_db) -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
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
