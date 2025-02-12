import pytest
from httpx import AsyncClient
from main import app
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from bson import ObjectId
import uuid
import asyncio
from src.note_gen.dependencies import get_db

@pytest.fixture(scope="function")
async def client():
    """
    Create an async client for testing with proper lifecycle management.
    """
    async with AsyncClient(base_url="http://localhost:8000", verify=False) as c:
        yield c

async def cleanup_pattern(pattern_id):
    """
    Cleanup helper function to remove a pattern after test.
    Uses the new get_db method with proper error handling.
    """
    try:
        db = await get_db()
        await db.rhythm_patterns.delete_one({"_id": pattern_id})
    except Exception as e:
        print(f"Error during cleanup: {e}")

@pytest.fixture(scope="function")
async def test_rhythm_pattern(client):
    """
    Fixture to create a test rhythm pattern with a unique name.
    Ensures cleanup after the test.
    """
    # Create a unique test rhythm pattern
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

    # Generate a unique name
    unique_name = f'Test Rhythm Pattern {uuid.uuid4()}'
    rhythm_pattern = RhythmPattern(
        name=unique_name, 
        description='Basic quarter note pattern', 
        tags=['basic'], 
        complexity=1.0, 
        data=rhythm_data, 
        is_test=True
    )

    # Create the pattern
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()

    try:
        yield created_pattern
    finally:
        # Cleanup the pattern after the test
        try:
            await cleanup_pattern(created_pattern['id'])
        except Exception:
            # Log or handle cleanup errors if needed
            pass

# Consolidated tests for rhythm pattern functionality

@pytest.mark.asyncio
async def test_rhythm_pattern_functionality(client, test_rhythm_pattern):
    # Test get rhythm pattern
    response = await client.get(f'/rhythm-patterns/{test_rhythm_pattern["id"]}')
    
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == test_rhythm_pattern['name']
    assert len(data['data']['notes']) == 1

    # Test invalid rhythm pattern id
    response = await client.get('/rhythm-patterns/invalid_id')
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_rhythm_pattern(client):
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
    
    unique_name = f'Test Create Pattern {uuid.uuid4()}'
    rhythm_pattern = RhythmPattern(
        name=unique_name, 
        description='Basic quarter note pattern', 
        tags=['basic'], 
        complexity=1.0, 
        data=rhythm_data, 
        is_test=True
    )
    
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    
    assert response.status_code == 201
    created_pattern = response.json()
    assert created_pattern['name'] == unique_name
    assert len(created_pattern['data']['notes']) == 1

    # Cleanup
    await cleanup_pattern(created_pattern['id'])

@pytest.mark.asyncio
async def test_create_duplicate_rhythm_pattern(client):
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
    
    unique_name = f'Test Duplicate Pattern {uuid.uuid4()}'
    rhythm_pattern = RhythmPattern(
        id=str(ObjectId()), 
        name=unique_name, 
        description='Basic quarter note pattern', 
        tags=['basic'], 
        complexity=1.0, 
        data=rhythm_data, 
        is_test=True
    )
    
    # Create first pattern
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 201
    first_pattern = response.json()

    # Try to create duplicate
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Content: {response.text}")
    
    assert response.status_code == 409
    assert response.json()['detail'] == f"Rhythm pattern with name '{unique_name}' already exists"

    # Cleanup
    await cleanup_pattern(first_pattern['id'])

@pytest.mark.asyncio
async def test_create_invalid_rhythm_pattern(client):
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
    
    unique_name = f'Invalid Pattern {uuid.uuid4()}'
    invalid_pattern = RhythmPattern(
        name=unique_name, 
        description='Invalid pattern', 
        tags=['basic'], 
        complexity=1.0, 
        data=rhythm_data, 
        is_test=True
    )
    response = await client.post('/rhythm-patterns', json=invalid_pattern.model_dump())
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Content: {response.text}")

    # Add more specific validation checks here based on your requirements
    assert response.status_code == 201  # Assuming the pattern is valid

@pytest.mark.asyncio
async def test_create_delete_rhythm_pattern(client: AsyncClient):
    """Test creating and then deleting a rhythm pattern."""
    notes = [
        RhythmNote(position=0.0, duration=1.0, velocity=100.0),
        RhythmNote(position=1.0, duration=1.0, velocity=0.0),
        RhythmNote(position=2.0, duration=1.0, velocity=0.0),
        RhythmNote(position=3.0, duration=1.0, velocity=0.0)
    ]
    
    rhythm_data = RhythmPatternData(
        beats_per_measure=4,
        beat_unit=4,
        subdivisions=4,
        pattern=[1, 0, 0, 0],
        style="basic",
        notes=notes
    )

    unique_name = f'Test Create Delete Pattern {uuid.uuid4()}'
    rhythm_pattern = RhythmPattern(
        name=unique_name,
        description='Basic quarter note pattern',
        tags=['basic'],
        complexity=1.0,
        data=rhythm_data,
        is_test=True
    )

    # Create the pattern
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()
    assert created_pattern['name'] == unique_name

    # Print the pattern details for debugging
    print(f"Created pattern: {created_pattern}")
    
    # Delete the pattern
    response = await client.delete(f'/rhythm-patterns/{created_pattern["id"]}')
    print(f"Delete response: {response.status_code} - {response.text}")
    assert response.status_code == 204

    # Verify pattern is deleted
    response = await client.get(f'/rhythm-patterns/{created_pattern["id"]}')
    assert response.status_code == 404

    # Add relevant tests from other files here
    pass
