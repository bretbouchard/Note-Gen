import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app  # Adjust the import based on your app structure
from src.note_gen.models.note import Note

client = TestClient(app)

# Test for generating note sequence

def test_note_sequence():
    request_data = {
        "progression_name": "I-IV-V",  # Updated to a valid progression
        "note_pattern_name": "Simple Triad",  # Example note pattern
        "rhythm_pattern_name": "quarter_notes",  # Example rhythm pattern
        "scale_info": {"root": {"note_name": "C", "octave": 4}, "scale_type": "major"}
    }

    response = client.post("/generate-sequence", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert len(data["notes"]) > 0

    # Verify that the note sequence follows the Simple Triad pattern
    expected_intervals = [0, 2, 4]  # Simple Triad intervals
    root_note = 60  # MIDI number for C4
    for i, note in enumerate(data["notes"]):
        expected_pitch = root_note + expected_intervals[i % len(expected_intervals)]
        expected_note = Note.from_midi(expected_pitch)
        assert note["note_name"] == expected_note.note_name
        assert note["octave"] == expected_note.octave

@pytest.mark.asyncio
async def test_get_note_sequences() -> None:
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.get('/note-sequences')
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        data = response.json()
        assert len(data) > 0  # Ensure the list is not empty
        assert data[0]['name'] is not None  # Check if the name is not None
