"""
Tests for rhythm pattern functionality.
"""
import pytest
import os
import logging
from httpx import AsyncClient

logger = logging.getLogger(__name__)

@pytest.fixture
async def rhythm_pattern_fixture(test_db):
    """Fixture providing a test rhythm pattern."""
    pattern_data = {
        "pattern": [1.0, 0.5, 0.25, 1.0],
        "name": "Test Rhythm Pattern",
        "description": "Test pattern with float values",
        "tags": ["test"],
        "complexity": 2.0,
        "data": {
            "notes": [
                {"duration": 1.0, "position": 0, "is_rest": False, "velocity": 100},
                {"duration": 0.5, "position": 1.0, "is_rest": False, "velocity": 90},
                {"duration": 0.25, "position": 1.5, "is_rest": False, "velocity": 80},
                {"duration": 1.0, "position": 1.75, "is_rest": False, "velocity": 100}
            ],
            "time_signature": "4/4"
        }
    }

    # Insert the pattern into the test database
    result = await test_db.rhythm_patterns.insert_one(pattern_data)
    pattern_data["id"] = str(result.inserted_id)

    yield pattern_data

    # Cleanup
    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        await test_db.rhythm_patterns.delete_one({"_id": result.inserted_id})

@pytest.mark.asyncio
async def test_rhythm_pattern_with_float_values(test_client: AsyncClient):
    """Test that rhythm patterns with float values in the pattern field are properly handled."""
    pattern_data = {
        "notes": [
            {"position": 0.0, "duration": 0.25, "velocity": 100, "is_rest": False},
            {"position": 0.25, "duration": 0.5, "velocity": 90, "is_rest": False},
            {"position": 0.75, "duration": 0.75, "velocity": 80, "is_rest": False}
        ],
        "time_signature": "4/4"
    }

    # Send the validation request
    response = await test_client.post("/api/v1/patterns/rhythm-patterns/validate", json=pattern_data)

    assert response.status_code == 400
    response_data = response.json()
    assert isinstance(response_data, dict)  # Changed from list to dict
    assert "detail" in response_data

@pytest.mark.asyncio
async def test_rhythm_pattern_with_rests(test_client: AsyncClient):
    """Test creating a rhythm pattern with rest values."""
    pattern_data = {
        "notes": [
            {
                "position": 0.0,
                "duration": 1.0,
                "velocity": 100,
                "is_rest": False
            },
            {
                "position": 1.0,
                "duration": 0.5,
                "velocity": 0,
                "is_rest": True
            },
            {
                "position": 1.5,
                "duration": 2.0,
                "velocity": 100,
                "is_rest": False
            }
        ],
        "time_signature": "4/4"
    }

    response = await test_client.post(
        "/api/v1/patterns/rhythm-patterns/validate",
        json=pattern_data
    )

    assert response.status_code == 400
    response_data = response.json()
    assert isinstance(response_data, dict)  # Changed from list to dict
    assert "detail" in response_data

# Test class for rhythm pattern checks

class TestRhythmPatternCheck:
    @pytest.mark.asyncio
    async def test_check_rhythm_pattern(self, test_client: AsyncClient):
        """Test checking a valid rhythm pattern."""
        pattern_data = {
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 64},
                {"position": 1.0, "duration": 1.0, "velocity": 64},
                {"position": 2.0, "duration": 1.0, "velocity": 64},
                {"position": 3.0, "duration": 1.0, "velocity": 64}
            ],
            "time_signature": "4/4"
        }

        response = await test_client.post("/api/v1/patterns/rhythm-patterns/validate", json=pattern_data)
        assert response.status_code == 400
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_rhythm_pattern_with_float_values(self, test_client: AsyncClient):
        """Test checking a rhythm pattern with floating point values."""
        pattern_data = {
            "notes": [
                {"position": 0.0, "duration": 0.5, "velocity": 64},
                {"position": 0.5, "duration": 0.5, "velocity": 64},
                {"position": 1.0, "duration": 0.5, "velocity": 64},
                {"position": 1.5, "duration": 0.5, "velocity": 64}
            ],
            "time_signature": "4/4"
        }

        response = await test_client.post("/api/v1/patterns/rhythm-patterns/validate", json=pattern_data)
        assert response.status_code == 400
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_rhythm_pattern_with_rests(self, test_client: AsyncClient):
        """Test checking a rhythm pattern with rests."""
        pattern_data = {
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 64},
                {"position": 1.0, "duration": 1.0, "velocity": 0, "is_rest": True},
                {"position": 2.0, "duration": 1.0, "velocity": 64},
                {"position": 3.0, "duration": 1.0, "velocity": 0, "is_rest": True}
            ],
            "time_signature": "4/4"
        }

        response = await test_client.post("/api/v1/patterns/rhythm-patterns/validate", json=pattern_data)
        assert response.status_code == 400
        assert "detail" in response.json()