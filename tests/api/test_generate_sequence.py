import pytest
import httpx
from main import app
import asyncio
import logging

# Configure logging for the test module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
async def client():
    loop = asyncio.get_running_loop()
    async with httpx.AsyncClient(base_url="http://localhost:8000") as c:
        yield c

@pytest.fixture
async def setup_patterns(client):
    # Create required note and rhythm patterns for tests
    note_pattern = {
        "name": "Simple Triad",
        "data": {"intervals": [0, 4, 7]},
        "is_test": True
    }
    rhythm_pattern = {
        "name": "quarter_notes",
        "data": {"notes": [{"duration": 1.0, "is_rest": False}], "groove_type": "straight"},
        "is_test": True
    }
    await client.post("/api/v1/note-patterns", json=note_pattern)
    await client.post("/api/v1/rhythm-patterns", json=rhythm_pattern)

@pytest.mark.asyncio
async def test_generate_sequence_from_presets(client, setup_patterns) -> None:
    request_data = {
        "progression_name": "I-IV-V-I",  
        "note_pattern_name": "Simple Triad",  
        "rhythm_pattern_name": "quarter_notes",  
        "scale_info": {
            "root": {
                "note_name": "C",  
                "octave": 4
            },
            "scale_type": "MAJOR"  
        }
    }
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Response: {response.status_code}, {response.json()}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_generate_sequence_invalid_progression(client, setup_patterns) -> None:
    """Test generating a sequence with an invalid progression name."""
    data = {
        "progression_name": "Invalid Progression",  
        "note_pattern_name": "Nonexistent Pattern",  
        "rhythm_pattern_name": "Invalid Rhythm",  
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Testing invalid progression with data: %s", data)
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=data)
    logger.debug(f"Invalid progression response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "progression not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_sequence_invalid_note_pattern(client, setup_patterns) -> None:
    """Test generating a sequence with an invalid note pattern name."""
    data = {
        "progression_name": "I-IV-V-I",
        "note_pattern_name": "Invalid Note Pattern",  
        "rhythm_pattern_name": "quarter_notes",
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Testing invalid note pattern with data: %s", data)
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=data)
    logger.debug(f"Invalid note pattern response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "note pattern not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_sequence_invalid_rhythm_pattern(client, setup_patterns) -> None:
    """Test generating a sequence with an invalid rhythm pattern name."""
    data = {
        "progression_name": "I-IV-V-I",
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Invalid Rhythm Pattern",  
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Testing invalid rhythm pattern with data: %s", data)
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=data)
    logger.debug(f"Invalid rhythm pattern response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "rhythm pattern not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_note_sequence(client, setup_patterns):
    request_data = {
        "progression_name": "I-IV-V-I",
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "quarter_notes",
        "scale_info": {"root": {"note_name": "C", "octave": 4}, "scale_type": "MAJOR"}
    }
    logger.debug("Request Data: %s", request_data)

    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)  
    logger.debug(f"Response: {response.status_code}, {response.json()}")  
    if response.status_code != 200:
        logger.error("Response Body: %s", response.text)

    assert response.status_code == 200
    data = response.json()
    logger.debug("Generated Note Sequence: %s", data["notes"])
    assert "notes" in data
    assert len(data["notes"]) > 0

@pytest.mark.asyncio
async def test_generate_sequence_functionality(client, setup_patterns):
    # Test generate sequence from presets
    request_data = {
        "progression_name": "I-IV-V-I",  
        "note_pattern_name": "Simple Triad",  
        "rhythm_pattern_name": "quarter_notes",  
        "scale_info": {
            "root": {
                "note_name": "C",  
                "octave": 4
            },
            "scale_type": "MAJOR"  
        }
    }
    logger.debug("Request Data: %s", request_data)  
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Response: {response.status_code}, {response.json()}")
    if response.status_code != 200:
        logger.error("Response Body: %s", response.text)  

    assert response.status_code == 200
    
    data = response.json()
    logger.debug("Generated Note Sequence: %s", data["notes"])  
    assert "notes" in data
    assert len(data["notes"]) > 0
    assert data["progression_name"] == request_data["progression_name"]
    assert data["note_pattern_name"] == request_data["note_pattern_name"]
    assert data["rhythm_pattern_name"] == request_data["rhythm_pattern_name"]
    
    # Test invalid progression
    request_data = {
        "progression_name": "Invalid Progression",  
        "note_pattern_name": "Nonexistent Pattern",  
        "rhythm_pattern_name": "Invalid Rhythm",  
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Request Data: %s", request_data)  
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Invalid progression response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "progression not found" in response.json()["detail"]

    # Test invalid note pattern
    request_data = {
        "progression_name": "I-IV-V-I",
        "note_pattern_name": "Invalid Note Pattern",  
        "rhythm_pattern_name": "quarter_notes",
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Request Data: %s", request_data)  
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Invalid note pattern response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "note pattern not found" in response.json()["detail"]

    # Test invalid rhythm pattern
    request_data = {
        "progression_name": "I-IV-V-I",
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Invalid Rhythm Pattern",  
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Request Data: %s", request_data)  
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Invalid rhythm pattern response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "rhythm pattern not found" in response.json()["detail"]

    # Test note sequence
    request_data = {
        "progression_name": "I-IV-V-I",  
        "note_pattern_name": "Simple Triad",  
        "rhythm_pattern_name": "quarter_notes",  
        "scale_info": {"root": {"note_name": "C", "octave": 4}, "scale_type": "MAJOR"}
    }
    logger.debug("Request Data: %s", request_data)  

    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Response: {response.status_code}, {response.json()}")
    if response.status_code != 200:
        logger.error("Response Body: %s", response.text)  

    assert response.status_code == 200
    data = response.json()
    logger.debug("Generated Note Sequence: %s", data["notes"])  
    assert "notes" in data
    assert len(data["notes"]) > 0

    # Test generate sequence from presets with note structure check
    request_data = {
        "progression_name": "I-IV-V-I",  
        "note_pattern_name": "Simple Triad",  
        "rhythm_pattern_name": "quarter_notes",  
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Request Data: %s", request_data)  
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Response: {response.status_code}, {response.json()}")
    if response.status_code != 200:
        logger.error("Response Body: %s", response.text)  

    assert response.status_code == 200
    
    data = response.json()
    logger.debug("Generated Note Sequence: %s", data["notes"])  
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
