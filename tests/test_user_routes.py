import pytest
from fastapi.testclient import TestClient
from src.note_gen.routers.user_routes import app, get_db
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
import logging
from typing import Generator, Any, Dict, List, cast
from mongomock import MongoClient
from pymongo.database import Database

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
def setup_test_data(test_client: TestClient) -> Generator[None, None, None]:
    """Setup test data."""
    global _test_db
    if _test_db is None:
        raise RuntimeError("Test database not initialized")

    # Insert test data
    _test_db.chord_progressions.insert_many([
        {
            'id': "1",
            'name': 'I-IV-V',
            'chords': [
                {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'F', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'}
            ]
        },
        {
            'id': "2",
            'name': 'ii-V-I',
            'chords': [
                {'root': {'note_name': 'D', 'octave': 4}, 'quality': 'MINOR'},
                {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'},
                {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'}
            ]
        }
    ])
    
    _test_db.note_patterns.insert_many([
        {'id': "1", 'name': 'Simple Triad', 'pattern': [0, 2, 4]},
        {'id': "2", 'name': 'Pentatonic', 'pattern': [0, 2, 4, 7, 9]}
    ])
    
    _test_db.rhythm_patterns.insert_many([
        {
            'id': "1",
            'name': 'quarter_notes',
            'pattern': {
                'notes': [
                    {'duration': 1.0, 'velocity': 64}
                ],
                'total_duration': 1.0
            }
        },
        {
            'id': "2",
            'name': 'eighth_notes',
            'pattern': {
                'notes': [
                    {'duration': 0.5, 'velocity': 64},
                    {'duration': 0.5, 'velocity': 64}
                ],
                'total_duration': 1.0
            }
        }
    ])
    
    yield
    
    # Cleanup
    _test_db.chord_progressions.delete_many({})
    _test_db.note_patterns.delete_many({})
    _test_db.rhythm_patterns.delete_many({})

def test_get_rhythm_patterns(test_client: TestClient, setup_test_data: None) -> None:
    """Test GET /rhythm-patterns endpoint."""
    response = test_client.get("/rhythm-patterns")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(isinstance(pattern, dict) for pattern in data)

def test_get_rhythm_pattern_by_id(test_client: TestClient, setup_test_data: None) -> None:
    """Test GET /rhythm-patterns/{id} endpoint."""
    response = test_client.get("/rhythm-patterns/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'name' in data
    assert 'pattern' in data

def test_get_chord_progressions(test_client: TestClient, setup_test_data: None) -> None:
    """Test GET /chord-progressions endpoint."""
    response = test_client.get("/chord-progressions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(isinstance(prog, dict) for prog in data)

def test_get_chord_progression_by_id(test_client: TestClient, setup_test_data: None) -> None:
    """Test GET /chord-progressions/{id} endpoint."""
    response = test_client.get("/chord-progressions/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'name' in data
    assert 'chords' in data

def test_get_note_patterns(test_client: TestClient, setup_test_data: None) -> None:
    """Test GET /note-patterns endpoint."""
    response = test_client.get("/note-patterns")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(isinstance(pattern, dict) for pattern in data)

def test_get_note_pattern_by_id(test_client: TestClient, setup_test_data: None) -> None:
    """Test GET /note-patterns/{id} endpoint."""
    response = test_client.get("/note-patterns/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'name' in data
    assert 'pattern' in data
