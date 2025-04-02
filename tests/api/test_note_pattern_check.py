import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_note_pattern_functionality(test_client: AsyncClient):
    """Test the note pattern validation endpoint."""
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
                "velocity": 90,
                "is_rest": False
            },
            {
                "position": 1.5,
                "duration": 0.5,
                "velocity": 80,
                "is_rest": False
            }
        ],
        "time_signature": "4/4"
    }

    response = await test_client.post("/api/v1/patterns/rhythm/", json=pattern_data)
    assert response.status_code in [200, 201]
    
    response_data = response.json()
    if isinstance(response_data, list):
        response_data = response_data[0]  # Get first item if response is a list
    assert response_data["is_valid"] is True
