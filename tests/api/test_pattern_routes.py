"""Tests for pattern routes."""
import pytest
from httpx import AsyncClient
from src.note_gen.core.enums import ScaleType, ValidationLevel
from src.note_gen.main import app
from src.note_gen.schemas.pattern_request import PatternRequest

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
async def test_generate_pattern(test_pattern_data):
    """Test pattern generation endpoint."""
    async with AsyncClient(base_url="http://testserver") as client:
        response = await client.post("/patterns/note", json=test_pattern_data)
        assert response.status_code == 200
        data = response.json()
        assert "pattern" in data
        assert data["pattern"]["data"]["root_note"] == "C"
        assert data["pattern"]["data"]["scale_type"] == ScaleType.MAJOR.value

@pytest.mark.asyncio
async def test_validate_pattern(test_pattern_data):
    """Test pattern validation endpoint."""
    async with AsyncClient(base_url="http://testserver") as client:
        response = await client.post(
            "/patterns/validate",
            params={"validation_level": ValidationLevel.NORMAL.value},
            json=test_pattern_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
