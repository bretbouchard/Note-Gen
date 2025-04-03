import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_generate_sequence_invalid_progression(test_client: AsyncClient):
    """Test generating a sequence with an invalid progression name."""
    response = await test_client.post(
        "/api/v1/sequences/generate",
        json={
            "progression_name": "nonexistent_progression",
            "pattern_name": "test_pattern",
            "rhythm_pattern_name": "test_rhythm"
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

async def test_generate_sequence_invalid_note_pattern(test_client: AsyncClient):
    """Test generating a sequence with an invalid note pattern name."""
    # We'll just test the endpoint with an invalid pattern name
    # No need to create a test progression first

    # Now test with invalid note pattern
    response = await test_client.post(
        "/api/v1/sequences/generate",
        json={
            "progression_name": "test_progression",
            "pattern_name": "nonexistent_pattern",
            "rhythm_pattern_name": "test_rhythm"
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

async def test_generate_sequence_invalid_rhythm_pattern(test_client: AsyncClient):
    """Test generating a sequence with an invalid rhythm pattern name."""
    # We'll just test the endpoint with an invalid rhythm pattern name
    # No need to create a test note pattern first

    # Now test with invalid rhythm pattern
    response = await test_client.post(
        "/api/v1/sequences/generate",
        json={
            "progression_name": "test_progression",
            "pattern_name": "test_note_pattern",
            "rhythm_pattern_name": "nonexistent_rhythm"
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

