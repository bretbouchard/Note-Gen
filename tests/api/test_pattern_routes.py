"""Tests for pattern routes."""
import pytest
import httpx
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.note_gen.core.enums import ScaleType

@pytest.fixture
def test_pattern_data():
    """Return valid test pattern data."""
    return {
        "root_note": "C",
        "scale_type": ScaleType.MAJOR.value,
        "pattern_config": {
            "intervals": [0, 2, 4],
            "direction": "up",
            "octave_range": [4, 5],
            "key": "C4",
            "use_scale_mode": True,
            "use_chord_tones": True,
            "allow_chromatic": False,
            "max_interval_jump": 12
        }
    }

@pytest.mark.asyncio
async def test_generate_pattern(test_client: AsyncClient):
    """Test pattern generation endpoint."""
    request_data = {
        "root_note": "C",
        "scale_type": "MAJOR",
        "pattern_config": {
            "direction": "UP",
            "octave": 4,
            "max_interval_jump": 12
        }
    }
    
    response = await test_client.post("/api/v1/patterns/generate/note", json=request_data)
    assert response.status_code == 200
    assert "data" in response.json()

@pytest.mark.asyncio
async def test_validate_pattern(test_client: AsyncClient, test_pattern_data):
    """Test pattern validation endpoint."""
    response = await test_client.post(
        "/api/v1/patterns/validate",
        json=test_pattern_data,
        params={"validation_level": "NORMAL"}
    )
    assert response.status_code == 200
    result = response.json()
    assert "is_valid" in result
