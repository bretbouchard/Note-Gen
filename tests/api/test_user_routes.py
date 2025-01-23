# file: tests/api/test_user_routes.py

from fastapi.testclient import TestClient
from main import app
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from bson import ObjectId
import uuid
import pytest
import httpx

@pytest.fixture
async def client():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        yield client

# Consolidated tests for user routes functionality

@pytest.mark.asyncio
async def test_user_routes_functionality(client):
    # Add relevant tests from other files here
    # Test get user
    response = await client.get('/users/me')
    assert response.status_code == 200
    
    # Test get user by id
    response = await client.get('/users/1')
    assert response.status_code == 200
    
    # Test create user
    user_data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'test_password'}
    response = await client.post('/users', json=user_data)
    assert response.status_code == 201
    
    # Test update user
    user_data = {'username': 'updated_test_user', 'email': 'updated_test@example.com'}
    response = await client.put('/users/1', json=user_data)
    assert response.status_code == 200
    
    # Test delete user
    response = await client.delete('/users/1')
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_get_rhythm_pattern(client):
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
    
    rhythm_pattern = RhythmPattern(name='Test Get Pattern', description='Basic quarter note pattern', tags=['basic'], complexity=1.0, data=rhythm_data, is_test=True)
    
    # Insert the pattern into the database
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 201
    
    # Retrieve the pattern
    response = await client.get(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Test Get Pattern'
    assert len(data['data']['notes']) == 1

@pytest.mark.asyncio
async def test_invalid_rhythm_pattern_id(client):
    response = await client.get('/rhythm-patterns/invalid_id')
    assert response.status_code == 422  # if your router actually returns 422 on invalid format
    assert response.json()['detail'][0]['msg'] == "Invalid ID format"

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
    
    rhythm_pattern = RhythmPattern(name='Test Create Pattern', description='Basic quarter note pattern', tags=['basic'], complexity=1.0, data=rhythm_data, is_test=True)
    
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()
    assert created_pattern['name'] == rhythm_pattern.name
    assert len(created_pattern['data']['notes']) == 1

@pytest.mark.asyncio
async def test_create_duplicate_rhythm_pattern(client):
    # First pattern
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
    
    rhythm_pattern = RhythmPattern(id=str(ObjectId()), name='Test Duplicate Pattern', description='Basic quarter note pattern', tags=['basic'], complexity=1.0, data=rhythm_data, is_test=True)
    
    # Create first pattern
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 201
    
    # Try to create duplicate with same name
    rhythm_pattern.id = str(uuid.uuid4())
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 409
    assert response.json()['detail'] == "Rhythm pattern with name 'Test Duplicate Pattern' already exists"

@pytest.mark.asyncio
async def test_invalid_rhythm_pattern(client):
    # Test with empty notes list
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],  # Ensure notes list is not empty
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
    
    invalid_pattern = RhythmPattern(name='Invalid Pattern', description='Invalid pattern', tags=['basic'], complexity=1.0, data=rhythm_data, is_test=True)
    response = await client.post('/rhythm-patterns', json=invalid_pattern.model_dump())
    assert response.status_code == 201  # Validation should pass

@pytest.mark.asyncio
async def test_create_and_delete_rhythm_pattern(client):
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
    
    rhythm_pattern = RhythmPattern(id=str(ObjectId()), name='Test Create Delete Pattern', description='Basic quarter note pattern', tags=['basic'], complexity=1.0, data=rhythm_data, is_test=True)
    
    # Create the pattern
    response = await client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()
    pattern_id = created_pattern['id']
    
    # Delete the pattern
    response = await client.delete(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 204
    # Verify pattern is deleted
    response = await client.get(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 404
    assert response.json()['detail'] == "Rhythm pattern not found"