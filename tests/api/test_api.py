import pytest
import unittest
from unittest.mock import patch, MagicMock
from src.note_gen.models.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale import Scale, ScaleType
from src.note_gen.models.chord_progression import ChordProgression
import random
import logging
from fastapi.testclient import TestClient
from src.note_gen.routers.user_routes import app, get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    db = MagicMock()
    db.chord_progressions = MagicMock()
    db.note_patterns = MagicMock()
    db.rhythm_patterns = MagicMock()
    
    # Setup mock data
    db.chord_progressions.find.return_value = [
        {
            "_id": "test_id_1",
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
    db.note_patterns.find.return_value = [
        {
            "_id": "test_id_2",
            "name": "Test Pattern",
            "notes": [
                {
                    "note_name": "C",
                    "octave": 4,
                    "duration": 1.0,
                    "velocity": 64,
                    "stored_midi_number": 60
                }
            ],
            "pattern_type": "melodic",
            "description": "Test pattern description",
            "tags": ["test"],
            "complexity": 1.0
        }
    ]
    db.rhythm_patterns.find.return_value = [
        {
            "_id": "test_id_3",
            "name": "Test Pattern",
            "description": "Test rhythm pattern",
            "tags": ["test"],
            "complexity": 1.0,
            "style": "rock",
            "data": {
                "notes": [
                    {
                        "position": 0.0,
                        "duration": 1.0,
                        "velocity": 100,
                        "is_rest": False
                    }
                ],
                "time_signature": "4/4",
                "swing_enabled": False,
                "humanize_amount": 0.0,
                "swing_ratio": 0.67,
                "default_duration": 1.0,
                "total_duration": 4.0,
                "accent_pattern": [],
                "groove_type": "straight",
                "variation_probability": 0.0,
                "duration": 1.0,
                "style": "rock"
            }
        }
    ]
    return db

@pytest.fixture(scope="module")
def test_client(test_db):
    def override_get_db():
        return test_db
    app.dependency_overrides[get_db] = override_get_db
    yield client
    app.dependency_overrides.clear()

def test_get_chord_progressions(test_client):
    response = test_client.get('/chord-progressions')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    data = response.json()
    assert len(data) > 0

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
    assert "name" in data
    assert "chords" in data

def test_invalid_endpoint(test_client):
    response = test_client.get('/invalid-endpoint')
    assert response.status_code == 404
