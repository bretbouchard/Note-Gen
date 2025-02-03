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

@pytest.mark.asyncio
async def test_generate_sequence_from_presets(client) -> None:
    request_data = {
        "progression_name": "I-IV-V",  # Ensure this progression exists in your database
        "note_pattern_name": "Simple Triad",  # Ensure this pattern exists
        "rhythm_pattern_name": "jazz",  # Ensure this pattern exists
        "scale_info": {
            "root": "C",
            "octave": 4
        }
    }
    response = await client.post("/generate-sequence", json=request_data)
    
    # Log the response for debugging
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_generate_sequence_invalid_progression(client) -> None:
    request_data = {
        "progression_name": "Invalid Progression",
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
    logger.debug("Request Data:", request_data)  # Log the request data
    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 422:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 422
    assert "Invalid progression name" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_sequence_invalid_note_pattern(client) -> None:
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
    logger.debug("Request Data:", request_data)  # Log the request data
    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 422:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 422
    assert "Invalid note pattern name" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_sequence_invalid_rhythm_pattern(client) -> None:
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
    logger.debug("Request Data:", request_data)  # Log the request data
    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 422:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 422
    assert "Invalid rhythm pattern name" in response.json()["detail"]

@pytest.mark.asyncio
async def test_note_sequence(client):
    request_data = {
        "progression_name": "I-IV-V",  # Updated to a valid progression
        "note_pattern_name": "Simple Triad",  # Example note pattern
        "rhythm_pattern_name": "jazz",  # Using 'jazz' rhythm pattern
        "scale_info": {"root": {"note_name": "C", "octave": 4}, "scale_type": "MAJOR"}
    }
    logger.debug("Request Data:", request_data)  # Log the request data

    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 200:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 200
    data = response.json()
    logger.debug("Generated Note Sequence:", data["notes"])  # Print the generated note sequence
    assert "notes" in data
    assert len(data["notes"]) > 0

# Consolidated tests for sequence generation functionality

@pytest.mark.asyncio
async def test_generate_sequence_functionality(client):
    # Test generate sequence from presets
    request_data = {
        "progression_name": "I-IV-V-I",  # Using actual preset progression
        "note_pattern_name": "Simple Triad",  # Using actual preset note pattern
        "rhythm_pattern_name": "quarter_notes",  # Using actual preset rhythm pattern
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Request Data:", request_data)  # Log the request data
    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 200:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 200
    
    data = response.json()
    logger.debug("Generated Note Sequence:", data["notes"])  # Print the generated note sequence
    assert "notes" in data
    assert len(data["notes"]) > 0
    assert data["progression_name"] == request_data["progression_name"]
    assert data["note_pattern_name"] == request_data["note_pattern_name"]
    assert data["rhythm_pattern_name"] == request_data["rhythm_pattern_name"]
    
    # Test invalid progression
    request_data = {
        "progression_name": "Invalid Progression",
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
    logger.debug("Request Data:", request_data)  # Log the request data
    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 422:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 422
    assert "Invalid progression name" in response.json()["detail"]

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
    logger.debug("Request Data:", request_data)  # Log the request data
    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 422:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 422
    assert "Invalid note pattern name" in response.json()["detail"]

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
    logger.debug("Request Data:", request_data)  # Log the request data
    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 422:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 422
    assert "Invalid rhythm pattern name" in response.json()["detail"]

    # Test note sequence
    request_data = {
        "progression_name": "I-IV-V",  # Updated to a valid progression
        "note_pattern_name": "Simple Triad",  # Example note pattern
        "rhythm_pattern_name": "jazz",  # Using 'jazz' rhythm pattern
        "scale_info": {"root": {"note_name": "C", "octave": 4}, "scale_type": "MAJOR"}
    }
    logger.debug("Request Data:", request_data)  # Log the request data

    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 200:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 200
    data = response.json()
    logger.debug("Generated Note Sequence:", data["notes"])  # Print the generated note sequence
    assert "notes" in data
    assert len(data["notes"]) > 0

    # Test generate sequence from presets with note structure check
    request_data = {
        "progression_name": "I-IV-V-I",  # Using actual preset progression
        "note_pattern_name": "Simple Triad",  # Using actual preset note pattern
        "rhythm_pattern_name": "quarter_notes",  # Using actual preset rhythm pattern
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4
            },
            "scale_type": "MAJOR"
        }
    }
    logger.debug("Request Data:", request_data)  # Log the request data
    response = await client.post("/generate-sequence", json=request_data)
    logger.debug("Response Status Code: %s", response.status_code)  # Log the response status
    if response.status_code != 200:
        logger.error("Response Body: %s", response.text)  # Log the response body for debugging

    assert response.status_code == 200
    
    data = response.json()
    logger.debug("Generated Note Sequence:", data["notes"])  # Print the generated note sequence
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
