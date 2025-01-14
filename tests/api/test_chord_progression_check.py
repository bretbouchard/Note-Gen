import pytest
from fastapi.testclient import TestClient
from src.note_gen.routers.user_routes import app
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.scale_info import ScaleInfo
from bson import ObjectId
import uuid

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_database(client):
    # Setup code to insert test data into the database
    progression = {
        'id': str(ObjectId()),
        'name': 'Test Base Progression',
        'chords': ['C', 'G', 'Am', 'F'],
        'key': 'C',
        'scale_type': 'major',
        'description': 'Base test progression',
        'tags': ['basic'],
        'complexity': 1.0
    }
    client.post('/chord-progressions', json=progression)
    yield

def test_create_chord_progression(client):
    test_progression = {
        "id": str(uuid.uuid4()),
        "name": "Test Create Progression",
        "scale_info": {
            "key": "C",
            "mode": "major"
        },
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "major"}
        ],
        "root": {
            "note_name": "C",
            "octave": 4
        },
        "description": "Test progression",
        "tags": ["basic"],
        "complexity": 1.0,
        "style": "basic"
    }
    
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 200
    created_progression = response.json()
    assert created_progression['name'] == test_progression['name']
    assert len(created_progression['chords']) == len(test_progression['chords'])

def test_create_duplicate_chord_progression(client):
    test_progression = {
        "id": str(uuid.uuid4()),
        "name": "Test Duplicate Progression",
        "scale_info": {
            "key": "C",
            "mode": "major"
        },
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "major"}
        ],
        "root": {
            "note_name": "C",
            "octave": 4
        },
        "description": "Test progression",
        "tags": ["basic"],
        "complexity": 1.0,
        "style": "basic"
    }
    
    # Create first progression
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 200
    
    # Try to create duplicate with same name
    test_progression["id"] = str(uuid.uuid4())
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 409

def test_invalid_chord_progression(client):
    progression = {
        'id': str(ObjectId()),
        'name': 'Invalid Progression',
        'chords': ['H', 'X', 'Y', 'Z'],  # Invalid chord names
        'key': 'H',  # Invalid key
        'scale_type': 'invalid',  # Invalid scale type
        'description': 'Invalid progression',
        'tags': ['basic'],
        'complexity': 2.0  # Invalid complexity (should be 0-1)
    }
    response = client.post('/chord-progressions', json=progression)
    assert response.status_code == 422  # Validation error

def test_get_chord_progression(client):
    # Create a test progression
    test_progression = {
        'id': str(uuid.uuid4()),
        'name': 'Test Get Progression',
        'chords': ['C', 'G', 'Am', 'F'],
        'key': 'C',
        'scale_type': 'major',
        'description': 'Test progression',
        'tags': ['basic'],
        'complexity': 1.0
    }
    
    response = client.post('/chord-progressions', json=test_progression)
    assert response.status_code == 200
    created = response.json()
    
    # Get the progression
    response = client.get(f'/chord-progressions/{created["id"]}')
    assert response.status_code == 200
    assert response.json()['name'] == test_progression['name']

def test_invalid_chord_progression_id(client):
    response = client.get('/chord-progressions/invalid_id')
    assert response.status_code == 422  # Invalid ID format

def test_create_and_delete_chord_progression(client):
    test_progression = {
        "id": str(uuid.uuid4()),
        "name": "Test Create Delete Progression",
        "scale_info": {
            "key": "C",
            "mode": "major"
        },
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "major"}
        ],
        "root": {
            "note_name": "C",
            "octave": 4
        },
        "description": "Test progression",
        "tags": ["basic"],
        "complexity": 1.0,
        "style": "basic"
    }
    
    # Create the progression
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 200
    created_progression = response.json()
    progression_id = created_progression["id"]
    
    # Delete the progression
    response = client.delete(f"/chord-progressions/{progression_id}")
    assert response.status_code == 200
    
    # Verify progression is deleted
    response = client.get(f"/chord-progressions/{progression_id}")
    assert response.status_code == 404
