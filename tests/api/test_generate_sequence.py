import pytest
from pymongo import MongoClient
import httpx

from src.note_gen.routers.user_routes import router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@pytest.fixture
def app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


@pytest.fixture
def test_db():
    """Create a test database."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client.test_note_gen
    yield db
    client.drop_database('test_note_gen')
    client.close()

@pytest.mark.asyncio
async def test_generate_sequence_from_presets() -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        request_data = {
            "progression_name": "I-IV-V-I",  # Using actual preset progression
            "note_pattern_name": "Simple Triad",  # Using actual preset note pattern
            "rhythm_pattern_name": "quarter_notes",  # Using actual preset rhythm pattern
            "scale_info": {
                "root": {
                    "note_name": "C",
                    "octave": 4
                },
                "scale_type": "major"
            }
        }
        response = await client.post("/generate-sequence", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    print("Generated Note Sequence:", data["notes"])  # Print the generated note sequence
    assert "notes" in data
    assert len(data["notes"]) > 0
    assert data["progression_name"] == request_data["progression_name"]
    assert data["note_pattern_name"] == request_data["note_pattern_name"]
    assert data["rhythm_pattern_name"] == request_data["rhythm_pattern_name"]
    
    # Check first note structure
    first_note = data["notes"][0]
    assert "note_name" in first_note
    assert "octave" in first_note
    assert "duration" in first_note
    assert "position" in first_note
    assert "velocity" in first_note
    
    # Check note values
    assert first_note["note_name"] in ["A", "B", "C", "D", "E", "F", "G"], f"Invalid note name: {first_note['note_name']}"
    assert isinstance(first_note["octave"], int), f"Invalid octave type: {type(first_note['octave'])}"
    assert 0 <= first_note["octave"] <= 8, f"Invalid octave value: {first_note['octave']}"
    assert isinstance(first_note["duration"], (int, float)), f"Invalid duration type: {type(first_note['duration'])}"
    assert isinstance(first_note["position"], (int, float)), f"Invalid position type: {type(first_note['position'])}"
    assert 0 <= first_note["velocity"] <= 127, f"Invalid velocity value: {first_note['velocity']}"

@pytest.mark.asyncio
async def test_generate_sequence_invalid_progression() -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        request_data = {
            "progression_name": "Invalid Progression",
            "note_pattern_name": "Simple Triad",
            "rhythm_pattern_name": "quarter_notes",
            "scale_info": {
                "root": {
                    "note_name": "C",
                    "octave": 4
                },
                "scale_type": "major"
            }
        }
        response = await client.post("/generate-sequence", json=request_data)
    assert response.status_code == 422
    assert "Invalid progression name" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_sequence_invalid_note_pattern() -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        request_data = {
            "progression_name": "I-IV-V-I",
            "note_pattern_name": "Invalid Note Pattern",
            "rhythm_pattern_name": "quarter_notes",
            "scale_info": {
                "root": {
                    "note_name": "C",
                    "octave": 4
                },
                "scale_type": "major"
            }
        }
        response = await client.post("/generate-sequence", json=request_data)
    assert response.status_code == 422
    assert "Invalid note pattern name" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_sequence_invalid_rhythm_pattern() -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        request_data = {
            "progression_name": "I-IV-V-I",
            "note_pattern_name": "Simple Triad",
            "rhythm_pattern_name": "Invalid Rhythm Pattern",
            "scale_info": {
                "root": {
                    "note_name": "C",
                    "octave": 4
                },
                "scale_type": "major"
            }
        }
        response = await client.post("/generate-sequence", json=request_data)
    assert response.status_code == 422
    assert "Invalid rhythm pattern name" in response.json()["detail"]
