import pytest
import httpx
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ScaleType

@pytest.mark.asyncio
async def test_note_sequence(app_client: httpx.AsyncClient, test_presets):
    request_data = {
        "progression_name": "test_I-IV-V",  # I-IV-V progression
        "note_pattern_name": "test_simple_triad",  # Example note pattern
        "rhythm_pattern_name": "test_quarter_notes",  # Example rhythm pattern
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4,
                "duration": 1,
                "velocity": 64
            },
            "scale_type": "MAJOR"
        }
    }

    response = await app_client.post("/api/v1/note-sequences/generate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert len(data["notes"]) > 0

    # For I-IV-V progression in C major:
    # I   (C): [C4, E4, G4]  - [0, 4, 7]
    # IV  (F): [F4, A4, C5]  - [5, 9, 12]
    # V   (G): [G4, B4, D5]  - [7, 11, 14]
    expected_notes = [
        # C major triad (I)
        {"note_name": "C", "octave": 4},  # Root
        {"note_name": "E", "octave": 4},  # Major third
        {"note_name": "G", "octave": 4},  # Perfect fifth
        # F major triad (IV)
        {"note_name": "F", "octave": 4},  # Root
        {"note_name": "A", "octave": 4},  # Major third
        {"note_name": "C", "octave": 5},  # Perfect fifth
        # G major triad (V)
        {"note_name": "G", "octave": 4},  # Root
        {"note_name": "B", "octave": 4},  # Major third
        {"note_name": "D", "octave": 5},  # Perfect fifth
    ]

    assert len(data["notes"]) == len(expected_notes)
    for actual, expected in zip(data["notes"], expected_notes):
        assert actual["note_name"] == expected["note_name"]
        assert actual["octave"] == expected["octave"]

@pytest.mark.asyncio
async def test_get_note_sequences(app_client: httpx.AsyncClient, test_presets) -> None:
    response = await app_client.get('/api/v1/note-sequences')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    data = response.json()
    assert len(data) >= 0  # List may be empty initially

@pytest.mark.asyncio
async def test_note_sequence_functionality(app_client: httpx.AsyncClient, test_presets):
    # Test data
    note_sequence_data = {
        "name": "Test Sequence",
        "is_test": True,
        "notes": [{"note_name": "C", "octave": 4, "duration": 1.0, "velocity": 64}],
        "events": [],
        "duration": 0.0,
        "default_duration": 1.0,
        "progression_name": None,
        "note_pattern_name": None,
        "rhythm_pattern_name": None
    }

    # Create note sequence
    response = await app_client.post("/api/v1/note-sequences", json=note_sequence_data)
    assert response.status_code == 201
    result = response.json()
    sequence_id = result["id"]

    # Get note sequence
    response = await app_client.get(f"/api/v1/note-sequences/{sequence_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == note_sequence_data["name"]

    # Test invalid ID
    response = await app_client.get("/api/v1/note-sequences/invalid_id")
    assert response.status_code == 404

    # Delete note sequence
    response = await app_client.delete(f"/api/v1/note-sequences/{sequence_id}")
    assert response.status_code == 204

    # Verify deletion
    response = await app_client.get(f"/api/v1/note-sequences/{sequence_id}")
    assert response.status_code == 404

    # Add relevant tests from other files here
    request_data = {
        "progression_name": "test_I-IV-V",  # Updated to a valid progression
        "note_pattern_name": "test_simple_triad",  # Updated to a valid pattern
        "rhythm_pattern_name": "test_quarter_notes",  # Updated to a valid pattern
        "scale_info": {
            "root": {
                "note_name": "C",
                "octave": 4,
                "duration": 1,
                "velocity": 64
            },
            "scale_type": "MAJOR"
        }
    }

    response = await app_client.post("/api/v1/note-sequences/generate", json=request_data)
    assert response.status_code == 200
    result = response.json()
    assert "notes" in result
    assert len(result["notes"]) > 0
