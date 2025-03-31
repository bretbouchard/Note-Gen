import pytest
import pytest_asyncio
import httpx
from src.note_gen.main import app
import asyncio
import logging
from httpx import ASGITransport
from src.note_gen.database.db import init_db, close_mongo_connection

# Configure logging for the test module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest_asyncio.fixture
async def client(test_db):
    """
    Client fixture that ensures database connection is initialized.
    Uses the test_db fixture to ensure proper database setup.
    """
    logger.debug("Setting up client fixture with database connection")
    # Create a client that uses the app directly via ASGITransport
    # No need to connect to a running server
    transport = ASGITransport(app=app)
    
    # Important: use base_url with the full path prefix that matches what's in main.py
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # The database connection will be closed by the test_db fixture

@pytest_asyncio.fixture
async def setup_patterns(client, test_db):
    """
    Setup fixture to create test patterns in the database.
    """
    logger.debug("Setting up test patterns...")
    
    # Create a note pattern for testing
    note_pattern = {
        "name": "Simple Triad",
        "data": {
            "notes": [
                {"note_name": "C", "octave": 4, "duration": 1.0, "velocity": 100},
                {"note_name": "E", "octave": 4, "duration": 1.0, "velocity": 100},
                {"note_name": "G", "octave": 4, "duration": 1.0, "velocity": 100}
            ],
            "intervals": [0, 4, 7],
            "duration": 1.0,
            "position": 0.0,
            "velocity": 100.0
        },
        "description": "Simple triad pattern",
        "tags": ["test"],
        "is_test": True
    }
    
    try:
        # Instead of using the API, insert directly into the database
        logger.debug("Creating note pattern directly in database")
        result = await test_db.note_patterns.insert_one(note_pattern)
        logger.debug(f"Note pattern created with ID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"Failed to create note pattern: {e}")
    
    # Create a rhythm pattern for testing
    rhythm_pattern = {
        "name": "quarter_notes",
        "data": {
            "notes": [
                {"duration": 1.0, "position": 0.0, "is_rest": False, "velocity": 100},
                {"duration": 1.0, "position": 1.0, "is_rest": False, "velocity": 100},
                {"duration": 1.0, "position": 2.0, "is_rest": False, "velocity": 100},
                {"duration": 1.0, "position": 3.0, "is_rest": False, "velocity": 100}
            ],
            "time_signature": "4/4",
            "tempo": 120
        },
        "pattern": "1.0 1.0 1.0 1.0",
        "description": "Quarter notes rhythm pattern",
        "tags": ["test"],
        "is_test": True
    }
    
    try:
        # Insert rhythm pattern directly
        logger.debug("Creating rhythm pattern directly in database")
        result = await test_db.rhythm_patterns.insert_one(rhythm_pattern)
        logger.debug(f"Rhythm pattern created with ID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"Failed to create rhythm pattern: {e}")
    
    # Create a chord progression for testing
    # Check if it already exists first
    chord_progression = await test_db.chord_progressions.find_one({"name": "I-IV-V-I"})
    
    if not chord_progression:
        chord_progression = {
            "name": "I-IV-V-I",
            "chords": [
                {"root": {"note_name": "C", "octave": 4}, "quality": "maj", "duration": 4},
                {"root": {"note_name": "F", "octave": 4}, "quality": "maj", "duration": 4},
                {"root": {"note_name": "G", "octave": 4}, "quality": "maj", "duration": 4},
                {"root": {"note_name": "C", "octave": 4}, "quality": "maj", "duration": 4}
            ],
            "tags": ["test"],
            "is_test": True,
            "description": "Classic I-IV-V-I progression"
        }
        
        try:
            # Insert chord progression directly
            logger.debug("Creating chord progression directly in database")
            result = await test_db.chord_progressions.insert_one(chord_progression)
            logger.debug(f"Chord progression created with ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Failed to create chord progression: {e}")
    else:
        logger.debug("Chord progression I-IV-V-I already exists")
    
    logger.debug("Test patterns setup complete")
    
    # No cleanup needed after tests since we're using a test database

@pytest.mark.asyncio
async def test_generate_sequence_from_presets(client, setup_patterns) -> None:
    request_data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Response: {response.status_code}, {response.json()}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_generate_sequence_invalid_progression(client, setup_patterns) -> None:
    """Test generating a sequence with an invalid progression name."""
    data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "Invalid Progression",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    logger.debug("Testing invalid progression with data: %s", data)
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=data)
    logger.debug(f"Invalid progression response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "Chord progression" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_sequence_invalid_note_pattern(client, setup_patterns) -> None:
    """Test generating a sequence with an invalid note pattern name."""
    data = {
        "note_pattern_name": "Invalid Note Pattern",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    logger.debug("Testing invalid note pattern with data: %s", data)
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=data)
    logger.debug(f"Invalid note pattern response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "Note pattern" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_sequence_invalid_rhythm_pattern(client, setup_patterns) -> None:
    """Test generating a sequence with an invalid rhythm pattern name."""
    data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Invalid Rhythm Pattern",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    logger.debug("Testing invalid rhythm pattern with data: %s", data)
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=data)
    logger.debug(f"Invalid rhythm pattern response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "Rhythm pattern" in response.json()["detail"]

@pytest.mark.asyncio
async def test_note_sequence(client, setup_patterns):
    request_data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    logger.debug("REQUEST DATA:")
    logger.debug(f"- Progression: {request_data['progression_name']}")
    logger.debug(f"- Note Pattern: {request_data['note_pattern_name']}")
    logger.debug(f"- Rhythm Pattern: {request_data['rhythm_pattern_name']}")
    logger.debug(f"- Scale: {request_data['scale_info']['key']} {request_data['scale_info']['scale_type']}")

    # Get chord progression first to log detailed chord data
    try:
        progression_resp = await client.get(f"/api/v1/chord-progressions/{request_data['progression_name']}")
        if progression_resp.status_code == 200:
            prog_data = progression_resp.json()
            logger.debug("CHORD PROGRESSION DETAILS:")
            for i, chord in enumerate(prog_data.get("chords", [])):
                chord_root = chord.get("root", {}).get("note_name", "Unknown")
                chord_quality = chord.get("quality", "Unknown")
                logger.debug(f"- Chord {i+1}: Root={chord_root}, Quality={chord_quality}")
    except Exception as e:
        logger.error(f"Error fetching chord progression details: {e}")

    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)  
    logger.debug(f"RESPONSE: Status={response.status_code}")  
    
    if response.status_code != 200:
        logger.error(f"ERROR RESPONSE: {response.text}")
    else:
        data = response.json()
        logger.debug("GENERATED SEQUENCE:")
        logger.debug(f"- Total notes: {len(data.get('notes', []))}")
        
        # Log the first few notes for debugging
        for i, note in enumerate(data.get("notes", [])[:10]):  # Log first 10 notes
            logger.debug(f"- Note {i+1}: {note.get('note_name')}{note.get('octave')}, Duration: {note.get('duration')}")
        
        if len(data.get("notes", [])) > 10:
            logger.debug(f"- ... and {len(data.get('notes', [])) - 10} more notes")

    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert len(data["notes"]) > 0

@pytest.mark.asyncio
async def test_generate_sequence_functionality(client, setup_patterns):
    # Test generate sequence from presets
    request_data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
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
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "Invalid Progression",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    logger.debug("Request Data: %s", request_data)  
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Invalid progression response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "Chord progression" in response.json()["detail"]

    # Test invalid note pattern
    request_data = {
        "note_pattern_name": "Invalid Note Pattern",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    logger.debug("Request Data: %s", request_data)  
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Invalid note pattern response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "Note pattern" in response.json()["detail"]

    # Test invalid rhythm pattern
    request_data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Invalid Rhythm Pattern",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    logger.debug("Request Data: %s", request_data)  
    response = await client.post("/api/v1/note-sequences/generate-sequence", json=request_data)
    logger.debug(f"Invalid rhythm pattern response: {response.status_code}, {response.json()}")
    assert response.status_code == 404
    assert "Rhythm pattern" in response.json()["detail"]

    # Test note sequence
    request_data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
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
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
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
