import pytest
import httpx
from main import app
from src.note_gen.models.note import Note

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_note_sequence(client: httpx.AsyncClient):
    request_data = {
        "progression_name": "I-IV-V",  # Updated to a valid progression
        "note_pattern_name": "Simple Triad",  # Example note pattern
        "rhythm_pattern_name": "quarter_notes",  # Example rhythm pattern
        "scale_info": {"root": {"note_name": "C", "octave": 4}, "scale_type": "major"}
    }

    response = await client.post("/generate-sequence", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert len(data["notes"]) > 0

    # Verify that the note sequence follows the Simple Triad pattern
    expected_intervals = [0, 2, 4]  # Simple Triad intervals
    root_note = 60  # MIDI number for C4
    for i, note in enumerate(data["notes"]):
        expected_pitch = root_note + expected_intervals[i % len(expected_intervals)]
        expected_note = Note.from_midi(expected_pitch, velocity=64, duration=1.0)
        assert note["note_name"] == expected_note.note_name
        assert note["octave"] == expected_note.octave

@pytest.mark.asyncio
async def test_get_note_sequences(client: httpx.AsyncClient) -> None:
    response = await client.get('/note-sequences')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    data = response.json()
    assert len(data) > 0  # Ensure the list is not empty
    assert data[0]['name'] is not None  # Check if the name is not None

@pytest.mark.asyncio
async def test_note_sequence_functionality(client):
    # Add relevant tests from other files here
    request_data = {
        "progression_name": "I-IV-V",  # Updated to a valid progression
        "note_pattern_name": "Simple Triad",  # Example note pattern
        "rhythm_pattern_name": "quarter_notes",  # Example rhythm pattern
        "scale_info": {"root": {"note_name": "C", "octave": 4}, "scale_type": "major"}
    }

    response = await client.post("/generate-sequence", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert len(data["notes"]) > 0

    # Verify that the note sequence follows the Simple Triad pattern
    expected_intervals = [0, 2, 4]  # Simple Triad intervals
    root_note = 60  # MIDI number for C4
    for i, note in enumerate(data["notes"]):
        expected_pitch = root_note + expected_intervals[i % len(expected_intervals)]
        expected_note = Note.from_midi(expected_pitch, velocity=64, duration=1.0)
        assert note["note_name"] == expected_note.note_name
        assert note["octave"] == expected_note.octave

    response = await client.get('/note-sequences')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    data = response.json()
    assert len(data) > 0  # Ensure the list is not empty
    assert data[0]['name'] is not None  # Check if the name is not None
