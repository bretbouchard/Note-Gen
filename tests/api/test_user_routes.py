import pytest
from fastapi.testclient import TestClient
from note_gen.routers.user_routes import app, get_db
from note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from note_gen.models.note import Note
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.note_pattern import NotePattern
import logging
from typing import Generator, Any, Dict, List, cast
from mongomock import MongoClient
from pymongo.database import Database
from bson import ObjectId
import json

# Configure logging to show debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_test_client: MongoClient | None = None
_test_db: Database[Any] | None = None

def get_test_db() -> Generator[Database[Any], None, None]:
    """Get test database."""
    global _test_db
    if _test_db is None:
        raise RuntimeError("Test database not initialized")
    yield _test_db

@pytest.fixture(scope="module", autouse=True)
def init_test_db() -> Generator[None, None, None]:
    """Initialize test database."""
    global _test_client, _test_db
    _test_client = MongoClient()
    _test_db = cast(Database[Any], _test_client.db)
    yield
    if _test_client is not None:
        _test_client.close()
        _test_client = None
    _test_db = None

@pytest.fixture(scope="module")
def test_client() -> TestClient:
    """Test client fixture."""
    app.dependency_overrides[get_db] = get_test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

@pytest.fixture(scope="module")
def setup_test_data(test_client: TestClient) -> Generator[Dict[str, str], None, None]:
    """Setup test data."""
    global _test_db
    if _test_db is None:
        raise RuntimeError("Test database not initialized")

    # Create test data with ObjectIds
    chord_progression_1_id = str(ObjectId())
    chord_progression_2_id = str(ObjectId())
    note_pattern_1_id = str(ObjectId())
    note_pattern_2_id = str(ObjectId())
    rhythm_pattern_1_id = str(ObjectId())
    rhythm_pattern_2_id = str(ObjectId())

    # Create test data
    chord_progression_1 = {
        'id': chord_progression_1_id,
        'name': 'I-IV-V',
        'scale_info': {
            'root': {'note_name': 'C', 'octave': 4},
            'scale_type': 'major'
        },
        'chords': [
            {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'},
            {'root': {'note_name': 'F', 'octave': 4}, 'quality': 'MAJOR'},
            {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'}
        ]
    }
    
    chord_progression_2 = {
        'id': chord_progression_2_id,
        'name': 'ii-V-I',
        'scale_info': {
            'root': {'note_name': 'C', 'octave': 4},
            'scale_type': 'major'
        },
        'chords': [
            {'root': {'note_name': 'D', 'octave': 4}, 'quality': 'MINOR'},
            {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'},
            {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'}
        ]
    }
    
    note_pattern_1 = {
        'id': note_pattern_1_id,
        'name': 'Simple Triad',
        'notes': [{'note_name': 'C', 'octave': 4, 'duration': 1.0}],
        'pattern_type': 'melodic',
        'description': 'Simple triad pattern',
        'tags': ['basic'],
        'complexity': 1.0
    }
    
    note_pattern_2 = {
        'id': note_pattern_2_id,
        'name': 'Pentatonic',
        'notes': [{'note_name': 'C', 'octave': 4, 'duration': 1.0}],
        'pattern_type': 'melodic',
        'description': 'Pentatonic pattern',
        'tags': ['basic'],
        'complexity': 1.0
    }
    
    rhythm_data = {
        'notes': [{'position': 0.0, 'duration': 1.0, 'velocity': 100, 'is_rest': False}],
        'time_signature': '4/4',
        'swing_enabled': False,
        'humanize_amount': 0.0,
        'swing_ratio': 0.67,
        'default_duration': 1.0,
        'total_duration': 4.0,
        'accent_pattern': [],
        'groove_type': 'straight',
        'variation_probability': 0.0,
        'duration': 1.0,
        'style': 'test'
    }
    
    rhythm_pattern_1 = {
        'id': rhythm_pattern_1_id,
        'name': 'Quarter Notes',
        'data': rhythm_data,
        'description': 'Basic quarter note pattern',
        'tags': ['basic'],
        'complexity': 1.0,
        'style': 'test'
    }
    
    rhythm_pattern_2 = {
        'id': rhythm_pattern_2_id,
        'name': 'Eighth Notes',
        'data': {
            **rhythm_data,
            'notes': [
                {'position': 0.0, 'duration': 0.5, 'velocity': 100, 'is_rest': False},
                {'position': 0.5, 'duration': 0.5, 'velocity': 100, 'is_rest': False}
            ]
        },
        'description': 'Basic eighth note pattern',
        'tags': ['basic'],
        'complexity': 1.0,
        'style': 'test'
    }
    
    # Insert test data
    _test_db.chord_progressions.insert_many([
        chord_progression_1,
        chord_progression_2
    ])
    
    _test_db.note_patterns.insert_many([
        note_pattern_1,
        note_pattern_2
    ])
    
    _test_db.rhythm_patterns.insert_many([
        rhythm_pattern_1,
        rhythm_pattern_2
    ])
    
    yield {
        'chord_progression_1_id': chord_progression_1_id,
        'chord_progression_2_id': chord_progression_2_id,
        'note_pattern_1_id': note_pattern_1_id,
        'note_pattern_2_id': note_pattern_2_id,
        'rhythm_pattern_1_id': rhythm_pattern_1_id,
        'rhythm_pattern_2_id': rhythm_pattern_2_id
    }

def test_get_rhythm_patterns(test_client: TestClient, setup_test_data: Dict[str, str]) -> None:
    """Test GET /rhythm-patterns endpoint."""
    response = test_client.get('/rhythm-patterns')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == 'Quarter Notes'
    assert data[1]['name'] == 'Eighth Notes'

def test_get_rhythm_pattern_by_id(test_client: TestClient, setup_test_data: Dict[str, str]) -> None:
    """Test GET /rhythm-patterns/{id} endpoint."""
    response = test_client.get(f'/rhythm-patterns/{setup_test_data["rhythm_pattern_1_id"]}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Quarter Notes'
    assert len(data['data']['notes']) == 1

async def test_get_chord_progressions() -> None:
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    # Create some chord progressions first
    progressions = [
        {
            "id": "test_id_1",
            "name": "Test Progression 1",
            "chords": ["C", "F", "G"],
            "key": "C",
            "scale_type": "major",
            "complexity": 0.5
        },
        {
            "id": "test_id_2",
            "name": "Test Progression 2",
            "chords": ["Am", "Dm", "E"],
            "key": "A",
            "scale_type": "minor",
            "complexity": 0.7
        }
    ]
    
    for progression in progressions:
        response = client.post("/chord-progressions", json=progression)
        assert response.status_code == 200
    
    # Get all progressions
    response = client.get("/chord-progressions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(progressions)
    assert all(prog in data for prog in progressions)

def test_get_chord_progression_by_id(test_client: TestClient, setup_test_data: Dict[str, str]) -> None:
    """Test GET /chord-progressions/{id} endpoint."""
    response = test_client.get(f'/chord-progressions/{setup_test_data["chord_progression_1_id"]}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'I-IV-V'
    assert len(data['chords']) == 3

def test_get_note_patterns(test_client: TestClient, setup_test_data: Dict[str, str]) -> None:
    """Test GET /note-patterns endpoint."""
    response = test_client.get('/note-patterns')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == 'Simple Triad'
    assert data[1]['name'] == 'Pentatonic'

def test_get_note_pattern_by_id(test_client: TestClient, setup_test_data: Dict[str, str]) -> None:
    """Test GET /note-patterns/{id} endpoint."""
    response = test_client.get(f'/note-patterns/{setup_test_data["note_pattern_1_id"]}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Simple Triad'
    assert len(data['notes']) == 1

def test_create_duplicate_note_pattern(test_client: TestClient, setup_test_data: Dict[str, str]):
    """Test creating a note pattern with a duplicate name."""
    pattern = {
        'id': str(ObjectId()),
        'name': 'Simple Triad',  # Using an existing name
        'notes': [{'note_name': 'C', 'octave': 4, 'duration': 1.0}],
        'pattern_type': 'melodic',
        'description': 'Test pattern',
        'tags': ['test'],
        'complexity': 0.5
    }
    response = test_client.post("/note-patterns", json=pattern)
    assert response.status_code == 409
    assert "already exists" in response.json()['detail']

def test_create_duplicate_rhythm_pattern(test_client: TestClient, setup_test_data: Dict[str, str]):
    """Test creating a rhythm pattern with a duplicate name."""
    pattern = {
        'id': str(ObjectId()),
        'name': 'Quarter Notes',  # Using an existing name
        'description': 'Test pattern',
        'tags': ['test'],
        'complexity': 0.5,
        'style': 'basic',
        'data': {
            'notes': [{'position': 0.0, 'duration': 1.0, 'velocity': 100, 'is_rest': False}],
            'time_signature': '4/4',
            'swing_enabled': False,
            'humanize_amount': 0.1,
            'swing_ratio': 0.5,
            'default_duration': 1.0,
            'total_duration': 4.0,
            'accent_pattern': [1.0],
            'groove_type': 'straight',
            'variation_probability': 0.1,
            'duration': 4.0,
            'style': 'basic'
        }
    }
    response = test_client.post("/rhythm-patterns", json=pattern)
    assert response.status_code == 409
    assert "already exists" in response.json()['detail']
