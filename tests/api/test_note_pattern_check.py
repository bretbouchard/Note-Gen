import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_note_pattern_functionality(test_client: AsyncClient):
    """Test the note pattern validation endpoint."""
    # Create a test pattern to validate
    pattern_data = {
        "name": "Test Pattern",
        "pattern": [
            {"pitch": "C", "octave": 4, "duration": 1.0, "position": 0.0, "velocity": 64}
        ]
    }

    # Test the validation endpoint
    response = await test_client.post(
        "/api/v1/patterns/validate",
        json=pattern_data,
        params={"validation_level": "NORMAL"}
    )

    # The endpoint can return 200 or 400 depending on the validation result
    assert response.status_code in [200, 400]
    data = response.json()
    if response.status_code == 200:
        assert "is_valid" in data
    else:
        assert "detail" in data
