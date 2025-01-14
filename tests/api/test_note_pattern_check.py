import pytest
from fastapi.testclient import TestClient
from src.note_gen.routers.user_routes import app
from src.note_gen.models.note import Note
from src.note_gen.models.note_pattern import NotePattern
from bson import ObjectId
import uuid

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_database(client):
    # Setup code to insert test data into the database
    note_pattern = {
        'id': str(ObjectId()),
        'name': 'Test Base Pattern',
        'notes': [{'note_name': 'C', 'octave': 4, 'duration': 1.0}],
        'pattern_type': 'melodic',
        'description': 'Base test pattern',
        'tags': ['basic'],
        'complexity': 1.0
    }
    client.post('/note-patterns', json=note_pattern)
    yield

def test_create_note_pattern(client):
    note_pattern = {
        'id': str(uuid.uuid4()),
        'name': 'Test Create Pattern',
        'pattern_type': 'melodic',
        'notes': [
            {'note_name': 'C', 'octave': 4, 'duration': 1.0},
            {'note_name': 'E', 'octave': 4, 'duration': 1.0},
            {'note_name': 'G', 'octave': 4, 'duration': 1.0}
        ],
        'description': 'Test pattern',
        'tags': ['basic'],
        'complexity': 1.0
    }
    response = client.post('/note-patterns', json=note_pattern)
    assert response.status_code == 200
    created_pattern = response.json()
    assert created_pattern['name'] == note_pattern['name']
    assert len(created_pattern['notes']) == len(note_pattern['notes'])

def test_invalid_note_pattern(client):
    invalid_pattern = {
        'id': str(ObjectId()),
        'name': 'Invalid Pattern',
        'notes': [{'note_name': 'Z', 'octave': -1, 'duration': -1.0}],  # Invalid note values
        'pattern_type': 'invalid',  # Invalid pattern type
        'description': 'Invalid pattern',
        'tags': ['basic'],
        'complexity': -1.0  # Invalid complexity
    }
    response = client.post('/note-patterns', json=invalid_pattern)
    assert response.status_code == 422  # Validation error

def test_create_duplicate_note_pattern(client):
    # Create first pattern
    note_pattern = {
        'id': str(uuid.uuid4()),
        'name': 'Test Duplicate Pattern',
        'pattern_type': 'melodic',
        'notes': [
            {'note_name': 'C', 'octave': 4, 'duration': 1.0}
        ],
        'description': 'Test pattern',
        'tags': ['basic'],
        'complexity': 1.0
    }
    response = client.post('/note-patterns', json=note_pattern)
    assert response.status_code == 200

    # Try to create duplicate with same name
    note_pattern['id'] = str(uuid.uuid4())
    response = client.post('/note-patterns', json=note_pattern)
    assert response.status_code == 409

def test_create_and_delete_note_pattern(client):
    # Create a test note pattern
    test_pattern = {
        "id": str(uuid.uuid4()),
        "name": "Test Create Delete Pattern",
        "pattern_type": "melodic",
        "notes": [
            {"note_name": "C", "octave": 4, "duration": 1.0},
            {"note_name": "E", "octave": 4, "duration": 1.0},
            {"note_name": "G", "octave": 4, "duration": 1.0}
        ],
        "description": "Test pattern",
        "tags": ['basic'],
        "complexity": 1.0
    }

    # Create the pattern
    response = client.post("/note-patterns", json=test_pattern)
    assert response.status_code == 200
    created_pattern = response.json()
    pattern_id = created_pattern["id"]

    # Delete the pattern
    response = client.delete(f"/note-patterns/{pattern_id}")
    assert response.status_code == 200

    # Verify pattern is deleted
    response = client.get(f"/note-patterns/{pattern_id}")
    assert response.status_code == 404
