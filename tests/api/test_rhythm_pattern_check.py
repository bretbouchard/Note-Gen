import pytest
from fastapi.testclient import TestClient
from note_gen.routers.user_routes import app
from note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from bson import ObjectId
import uuid

@pytest.fixture
def client():
    return TestClient(app)

def test_get_rhythm_pattern(client):
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
    response = client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 200
    
    # Retrieve the pattern
    response = client.get(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Test Get Pattern'
    assert len(data['data']['notes']) == 1

def test_invalid_rhythm_pattern_id(client):
    response = client.get('/rhythm-patterns/invalid_id')
    assert response.status_code == 422  # Invalid ID format
    assert response.json()['detail'][0]['msg'] == "Invalid ID format"

def test_create_rhythm_pattern(client):
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
    
    response = client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 200
    created_pattern = response.json()
    assert created_pattern['name'] == rhythm_pattern.name
    assert len(created_pattern['data']['notes']) == 1

def test_create_duplicate_rhythm_pattern(client):
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
    response = client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 200
    
    # Try to create duplicate with same name
    rhythm_pattern.id = str(uuid.uuid4())
    response = client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 409
    assert response.json()['detail'] == "Rhythm pattern with name 'Test Duplicate Pattern' already exists"

def test_invalid_rhythm_pattern(client):
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
    response = client.post('/rhythm-patterns', json=invalid_pattern.model_dump())
    assert response.status_code == 200  # Validation should pass

def test_create_and_delete_rhythm_pattern(client):
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
    response = client.post('/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 200
    created_pattern = response.json()
    pattern_id = created_pattern['id']
    
    # Delete the pattern
    response = client.delete(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 200
    
    # Verify pattern is deleted
    response = client.get(f'/rhythm-patterns/{pattern_id}')
    assert response.status_code == 404
    assert response.json()['detail'] == "Rhythm pattern not found"
