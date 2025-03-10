import pytest
from motor.motor_asyncio import AsyncIOMotorClient
import httpx
from main import app
from src.note_gen.models.note import Note
from src.note_gen.models.patterns import NotePattern
from src.note_gen.models.patterns import (
    RhythmPattern,
    RhythmPatternData,
    RhythmNote
)
from src.note_gen.database.db import get_db_conn
from bson import ObjectId
import asyncio
import os
import uuid

# Setup test database
@pytest.fixture(autouse=True)
async def test_db():
    """Fixture to provide a test database."""
    # Get the database connection (not using the generator directly)
    db = await get_db_conn()
    
    # Clear all collections before each test if CLEAR_DB_AFTER_TESTS is set to 1
    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})
    
    yield db

@pytest.fixture
async def client():
    """Fixture to provide an async test client."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, 
        base_url="http://localhost:8000",
        follow_redirects=True  # Follow redirects automatically
    ) as client:
        yield client

# Consolidated tests for note pattern functionality
@pytest.mark.asyncio
async def test_note_pattern_functionality(client, test_db):
    # Test create note pattern
    note_pattern_data = {
        "name": f"Test Create Pattern {uuid.uuid4()}",  # Use unique name
        "description": "Test pattern",
        "tags": ["basic"],
        "data": {
            "intervals": [0, 4, 7],  # Major triad intervals
            "duration": 4.0,
            "position": 0.0,
            "velocity": 100,
            "direction": "up",
            "use_chord_tones": True,
            "use_scale_mode": False,
            "arpeggio_mode": False,
            "restart_on_chord": False,
            "octave_range": [4, 5],
            "default_duration": 1.0
        },
        "is_test": True  # Ensure this is marked as a test pattern
    }
    
    response = await client.post("/api/v1/note-patterns", json=note_pattern_data)
    assert response.status_code == 201, f"Failed to create note pattern: {response.text}"
    created_pattern = response.json()
    assert created_pattern["name"] == note_pattern_data["name"]
    
    # Log ID for debugging
    pattern_id = created_pattern.get("id")
    assert pattern_id is not None, "Pattern ID is missing in response"
    print(f"Created note pattern with ID: {pattern_id}")

    # Test get note pattern
    response = await client.get(f"/api/v1/note-patterns/{pattern_id}")
    assert response.status_code == 200, f"Failed to get note pattern: {response.text}"
    retrieved_pattern = response.json()
    assert retrieved_pattern["name"] == note_pattern_data["name"]

    # Test update note pattern
    update_data = {
        "name": f"Updated Pattern {uuid.uuid4()}",  # Use unique name with UUID
        "description": "Updated test pattern",
        "tags": ["basic", "updated"],
        "data": {
            "intervals": [0, 3, 7],  # Minor triad intervals
            "duration": 4.0,
            "position": 0.0,
            "velocity": 100,
            "direction": "up",
            "use_chord_tones": True,
            "use_scale_mode": False
        }
    }
    
    response = await client.put(f"/api/v1/note-patterns/{pattern_id}", json=update_data)
    assert response.status_code == 200
    updated_pattern = response.json()
    assert updated_pattern["name"] == update_data["name"]

    # Test delete note pattern
    response = await client.delete(f"/api/v1/note-patterns/{pattern_id}")
    assert response.status_code == 204, f"Failed to delete note pattern. Expected 204, got {response.status_code}"
    
    # Verify pattern is deleted
    response = await client.get(f"/api/v1/note-patterns/{pattern_id}")
    assert response.status_code == 404

    # Test pattern that was previously using simplified format
    pattern_with_proper_format = {
        "name": f"Test Pattern Format {uuid.uuid4()}",  # Use unique name with UUID
        "description": "Test pattern with proper format",
        "tags": ["basic"],
        "data": {
            "duration": 1.0,
            "position": 0.0,
            "velocity": 100,
            "intervals": [0, 4, 7],  # Major triad intervals
            "direction": "up",
            "use_chord_tones": True,
            "use_scale_mode": False
        },
        "is_test": True
    }
    
    response = await client.post('/api/v1/note-patterns', json=pattern_with_proper_format)
    assert response.status_code == 201  # Should succeed with 201 Created

    # Test pattern with only intervals, no notes - this is the actual real-world usage
    intervals_only_pattern = {
        "name": f"Intervals Only Pattern {uuid.uuid4()}",  # Use unique name with UUID
        "description": "Pattern defined only by intervals",
        "tags": ["basic"],
        "data": {
            "duration": 1.0,
            "position": 0.0,
            "velocity": 100,
            "intervals": [0, 3, 7],  # Minor triad intervals
            "direction": "up",
            "use_chord_tones": True,
            "use_scale_mode": True
        },
        "is_test": True
    }
    response = await client.post('/api/v1/note-patterns', json=intervals_only_pattern)
    assert response.status_code == 201  # Should succeed with 201 Created

    # Test create duplicate note pattern
    note_pattern_data = {
        "name": f"Test Duplicate Pattern {uuid.uuid4()}",  # Use unique name
        "description": "Test pattern",
        "tags": ["basic"],
        "data": {
            "duration": 1.0,
            "position": 0.0,
            "velocity": 100,
            "intervals": [0, 4, 7],  # Major triad intervals
            "direction": "up",
            "use_chord_tones": True,
            "use_scale_mode": False
        },
        "is_test": True
    }
    response = await client.post('/api/v1/note-patterns', json=note_pattern_data)
    assert response.status_code == 201
    
    # Try to create duplicate with same name
    response = await client.post('/api/v1/note-patterns', json=note_pattern_data)
    assert response.status_code == 409

    # Test create and delete note pattern
    test_pattern_data = {
        "name": f"Test Create Delete Pattern {uuid.uuid4()}",  # Use unique name
        "description": "Test pattern",
        "tags": ["basic"],
        "data": {
            "intervals": [0, 2, 4, 5, 7, 9, 11],  # Major scale intervals
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
        "complexity": 0.5,
        "style": "basic",
        "is_test": True
    }
    
    # Create pattern
    response = await client.post('/api/v1/note-patterns', json=test_pattern_data)
    assert response.status_code == 201
    created_pattern = response.json()
    pattern_id = created_pattern['id']
    
    # Delete pattern
    response = await client.delete(f'/api/v1/note-patterns/{pattern_id}')
    assert response.status_code == 204
    
    # Verify pattern is deleted
    response = await client.get(f'/api/v1/note-patterns/{pattern_id}')
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

    # Remove pre-generated ID completely, let the server assign one
    rhythm_pattern = RhythmPattern(
        name=f'Test Create Delete Pattern {uuid.uuid4()}',  # Use unique name
        description='Basic quarter note pattern',
        tags=['basic'],
        complexity=1.0,
        data=rhythm_data,
        pattern=[1.0, 1.0, 1.0, 1.0],  # Adding pattern field with four quarter notes (4/4 time signature)
        is_test=True
    )

    # Create the pattern
    response = await client.post(
        '/api/v1/rhythm-patterns/',  # Added trailing slash
        json=rhythm_pattern.model_dump(exclude_none=True),
        follow_redirects=True  # Add this to follow redirects automatically
    )
    assert response.status_code == 201, f"Failed to create rhythm pattern: {response.text}"
    created_rhythm = response.json()
    
    # Extract the ID assigned by the server
    rhythm_pattern_id = created_rhythm.get('id')
    assert rhythm_pattern_id is not None, "Rhythm pattern ID is missing in response"
    print(f"Created rhythm pattern with ID: {rhythm_pattern_id}")

    # Verify pattern was created using the server-assigned ID
    response = await client.get(f'/api/v1/rhythm-patterns/{rhythm_pattern_id}')
    assert response.status_code == 200, f"Failed to get rhythm pattern with ID {rhythm_pattern_id}: {response.text}"
    
    # Delete the rhythm pattern
    response = await client.delete(f'/api/v1/rhythm-patterns/{rhythm_pattern_id}')
    assert response.status_code == 204, f"Failed to delete rhythm pattern. Expected 204, got {response.status_code}"
    
    # Verify rhythm pattern is deleted
    response = await client.get(f'/api/v1/rhythm-patterns/{rhythm_pattern_id}')
    assert response.status_code == 404, f"Pattern should be deleted but was found with status {response.status_code}"

    # Test get rhythm patterns API
    # First create a pattern to ensure there's at least one
    test_rhythm = RhythmPattern(
        name=f'Test Get Patterns API {uuid.uuid4()}',  # Use unique name
        description='Test rhythm pattern for API',
        tags=['test', 'api'],
        complexity=1.0,
        data=rhythm_data,
        pattern=[1.0, 1.0, 1.0, 1.0],
        is_test=True
    )
    
    # Create using API
    response = await client.post(
        '/api/v1/rhythm-patterns/',
        json=test_rhythm.model_dump(exclude_none=True),
        follow_redirects=True
    )
    assert response.status_code == 201, f"Failed to create test rhythm pattern: {response.text}"
    test_rhythm_created = response.json()
    test_rhythm_id = test_rhythm_created.get('id')
    
    # Now test the get patterns endpoint
    response = await client.get('/api/v1/rhythm-patterns/')
    assert response.status_code == 200, f"Failed to get rhythm patterns: {response.text}"
    patterns_list = response.json()
    assert isinstance(patterns_list, list), "Expected list of rhythm patterns"
    assert len(patterns_list) > 0, "No rhythm patterns returned"
    
    # Clean up
    await client.delete(f'/api/v1/rhythm-patterns/{test_rhythm_id}')

    # Test get note patterns
    response = await client.get('/api/v1/note-patterns')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    data = response.json()
    assert len(data) > 0  # Ensure the list is not empty
    assert data[0]['name'] is not None  # Check if the name is not None

    # Test invalid rhythm pattern id
    response = await client.get('/api/v1/rhythm-patterns/invalid_id')
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

    duplicate_pattern_name = f'Test Duplicate Pattern {uuid.uuid4()}'
    pattern = RhythmPattern(
        name=duplicate_pattern_name,
        description='Basic quarter note pattern',
        tags=['basic'],
        complexity=1.0,
        data=rhythm_data,
        pattern=[1.0, 1.0, 1.0, 1.0],
        is_test=True
    )

    # Create first pattern
    response = await client.post(
        '/api/v1/rhythm-patterns/',
        json=pattern.model_dump(exclude_none=True),
        follow_redirects=True
    )
    assert response.status_code == 201, f"Failed to create first pattern: {response.text}"
    
    # Get the pattern ID for cleanup later
    first_pattern = response.json()
    first_pattern_id = first_pattern.get('id')

    # Try to create duplicate with same name
    duplicate_pattern = RhythmPattern(
        name=duplicate_pattern_name,  # Same name as before
        description='Duplicate pattern',
        tags=['basic'],
        complexity=1.0,
        data=rhythm_data,
        pattern=[1.0, 1.0, 1.0, 1.0],
        is_test=True
    )
    
    response = await client.post(
        '/api/v1/rhythm-patterns/',
        json=duplicate_pattern.model_dump(exclude_none=True),
        follow_redirects=True
    )
    assert response.status_code == 409, f"Expected conflict error when creating duplicate pattern"

    # Clean up
    await client.delete(f'/api/v1/rhythm-patterns/{first_pattern_id}')
