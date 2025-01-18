import pytest
from fastapi.testclient import TestClient
from main import app
from src.note_gen.routers.user_routes import get_db
from unittest.mock import MagicMock, AsyncMock
from bson import ObjectId
from typing import List
import logging
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def test_db():
    """Create a mock database for testing."""
    db = MagicMock()
    db.chord_progressions = AsyncMock()
    db.note_patterns = AsyncMock()
    db.rhythm_patterns = AsyncMock()
    
    # Setup mock data
    mock_chord_progressions = [
        {
            "_id": ObjectId(),
            "name": "Test Progression",
            "scale_info": {
                "root": {"note_name": "C", "octave": 4},
                "scale_type": "MAJOR"
            },
            "chords": [
                {
                    "root": {"note_name": "C", "octave": 4},
                    "quality": "MAJOR"
                },
                {
                    "root": {"note_name": "G", "octave": 4},
                    "quality": "MAJOR"
                }
            ],
            "complexity": 1
        }
    ]
    mock_note_patterns = [
        {
            "_id": ObjectId(),
            "name": "Test Pattern",
            "notes": [{"note_name": "C", "octave": 4, "duration": 1.0}],
            "pattern_type": "melodic",
            "description": "Test pattern",
            "tags": ["test"],
            "complexity": 0.5
        }
    ]
    mock_rhythm_patterns = [
        {
            "_id": ObjectId(),
            "name": "Test Rhythm",
            "description": "Test rhythm pattern",
            "tags": ["test"],
            "complexity": 0.5,
            "style": "rock",
            "data": {
                "notes": [{"duration": 1.0, "velocity": 100}],
                "time_signature": "4/4",
                "swing_enabled": False,
                "humanize_amount": 0.1,
                "swing_ratio": 0.5,
                "default_duration": 1.0,
                "total_duration": 4.0,
                "accent_pattern": [1.0],
                "groove_type": "straight",
                "variation_probability": 0.1,
                "duration": 1.0,
                "style": "rock"
            }
        }
    ]

    # Mock MongoDB cursor methods
    class MockCursor:
        def __init__(self, items: List[dict]):
            self.items = items

        async def to_list(self, length=None):
            return self.items

        def skip(self, n):
            return self

        def limit(self, n):
            return self

    # Setup mock methods
    db.chord_progressions.find.return_value = MockCursor(mock_chord_progressions)
    db.note_patterns.find.return_value = MockCursor(mock_note_patterns)
    db.rhythm_patterns.find.return_value = MockCursor(mock_rhythm_patterns)

    # Mock insert_one to return ObjectId
    async def mock_insert_one(doc):
        return MagicMock(inserted_id=ObjectId())

    db.chord_progressions.insert_one.side_effect = mock_insert_one
    db.note_patterns.insert_one.side_effect = mock_insert_one
    db.rhythm_patterns.insert_one.side_effect = mock_insert_one

    return db

@pytest.fixture(scope="module")
def test_client(test_db):
    """Create a test client with a mock database."""
    async def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_post_invalid_data(test_client):
    logger.info("Testing post invalid data")
    invalid_data = {"invalid_field": "test"}
    response = test_client.post('/generate-chord-progression', json=invalid_data)
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data



@pytest.mark.asyncio
async def test_get_chord_progressions(test_client):
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.get('/chord-progressions')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Ensure the list is not empty
        assert data[0]['name'] is not None  # Check if the name is not None

def test_get_note_patterns(test_client):
    response = test_client.get('/note-patterns')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    data = response.json()
    assert len(data) > 0

def test_get_rhythm_patterns(test_client):
    response = test_client.get('/rhythm-patterns')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    data = response.json()
    assert len(data) > 0

def test_post_endpoint(test_client):
    test_data = {
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR"
        },
        "num_chords": 4,
        "progression_pattern": "I-IV-V-I"
    }
    response = test_client.post('/generate-chord-progression', json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Generated Chord Progression"
    assert len(data["chords"]) == 4
    for chord in data["chords"]:
        assert "root" in chord
        assert "quality" in chord

def test_invalid_endpoint(test_client):
    response = test_client.get('/invalid-endpoint')
    assert response.status_code == 404
    error_data = response.json()
    assert "detail" in error_data
    assert error_data["detail"] == "Not Found"
