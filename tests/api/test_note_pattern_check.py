import pytest
from fastapi.testclient import TestClient
from note_gen.routers.user_routes import app
from note_gen.models.note import Note
from note_gen.models.note_pattern import NotePattern
from bson import ObjectId
import uuid

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_database(client):
    # Setup code to insert test data into the database
    note_pattern = NotePattern(name='Test Base Pattern', description='Base test pattern', tags=['basic'], complexity=1.0, data=[{'note_name': 'C', 'octave': 4, 'duration': 1.0}], is_test=True)
    client.post('/note-patterns', json=note_pattern.dict())
    yield

def test_create_note_pattern(client):
    note_pattern = NotePattern(name='Test Create Pattern', description='Test pattern', tags=['basic'], complexity=1.0, data=[
        {'note_name': 'C', 'octave': 4, 'duration': 1.0},
        {'note_name': 'E', 'octave': 4, 'duration': 1.0},
        {'note_name': 'G', 'octave': 4, 'duration': 1.0}
    ], is_test=True)
    response = client.post('/note-patterns', json=note_pattern.dict())
    assert response.status_code == 200
    created_pattern = response.json()
    assert created_pattern['name'] == note_pattern.name
    assert len(created_pattern['data']) == len(note_pattern.data)

def test_invalid_note_pattern(client):
    invalid_pattern = NotePattern(name='Invalid Pattern', description='Invalid pattern', tags=['basic'], complexity=-1.0, data=[{'note_name': 'Z', 'octave': -1, 'duration': -1.0}], is_test=True)
    response = client.post('/note-patterns', json=invalid_pattern.dict())
    assert response.status_code == 422  # Validation error

def test_create_duplicate_note_pattern(client):
    # Create first pattern
    note_pattern = NotePattern(name='Test Duplicate Pattern', description='Test pattern', tags=['basic'], complexity=1.0, data=[
        {'note_name': 'C', 'octave': 4, 'duration': 1.0}
    ], is_test=True)
    response = client.post('/note-patterns', json=note_pattern.dict())
    assert response.status_code == 200

    # Try to create duplicate with same name
    response = client.post('/note-patterns', json=note_pattern.dict())
    assert response.status_code == 409

def test_create_and_delete_note_pattern(client):
    # Create a test note pattern
    test_pattern = NotePattern(name='Test Create Delete Pattern', description='Test pattern', tags=['basic'], complexity=1.0, data=[
        {'note_name': 'C', 'octave': 4, 'duration': 1.0},
        {'note_name': 'E', 'octave': 4, 'duration': 1.0},
        {'note_name': 'G', 'octave': 4, 'duration': 1.0}
    ], is_test=True)

    # Create the pattern
    response = client.post("/note-patterns", json=test_pattern.dict())
    assert response.status_code == 200
    created_pattern = response.json()
    pattern_id = created_pattern["id"]

    # Delete the pattern
    response = client.delete(f"/note-patterns/{pattern_id}")
    assert response.status_code == 200

    # Verify pattern is deleted
    response = client.get(f"/note-patterns/{pattern_id}")
    assert response.status_code == 404
