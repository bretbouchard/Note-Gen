import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_generate_sequence_invalid_progression(test_client: AsyncClient):
    """Test generating a sequence with an invalid progression name."""
    data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "Invalid Progression",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    response = await test_client.post("/api/v1/note-sequences/generate", json=data)
    assert response.status_code == 404
    assert "Note pattern" in response.json()["detail"]

async def test_generate_sequence_invalid_note_pattern(test_client: AsyncClient):
    """Test generating a sequence with an invalid note pattern name."""
    data = {
        "note_pattern_name": "Invalid Note Pattern",
        "rhythm_pattern_name": "Basic Rhythm",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    response = await test_client.post("/api/v1/note-sequences/generate", json=data)
    assert response.status_code == 404
    assert "Note pattern" in response.json()["detail"]

async def test_generate_sequence_invalid_rhythm_pattern(test_client: AsyncClient):
    """Test generating a sequence with an invalid rhythm pattern name."""
    data = {
        "note_pattern_name": "Simple Triad",
        "rhythm_pattern_name": "Invalid Rhythm Pattern",
        "progression_name": "I-IV-V-I",
        "scale_info": {"key": "C", "scale_type": "MAJOR"}
    }
    response = await test_client.post("/api/v1/note-sequences/generate", json=data)
    assert response.status_code == 404
    assert "Note pattern" in response.json()["detail"]

