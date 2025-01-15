import pytest
from fastapi.testclient import TestClient
from main import app  # Adjust the import based on your app structure
from note_gen.routers.user_routes import get_note_name, get_octave

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
        assert note["note_name"] == get_note_name(expected_pitch)
        assert note["octave"] == get_octave(expected_pitch)
