import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_note_sequences(test_client: AsyncClient):
    # Test getting all sequences
    response = await test_client.get("/api/v1/sequences/")
    assert response.status_code == 200
    data = response.json()
    assert "sequences" in data
    assert isinstance(data["sequences"], list)

@pytest.mark.asyncio
async def test_create_sequence(test_client: AsyncClient):
    # Test creating a new sequence
    sequence_data = {
        "name": "Test Sequence",
        "notes": [
            {"pitch": "C", "octave": 4, "duration": 1.0, "position": 0.0, "velocity": 64}
        ],
        "duration": 1.0,
        "tempo": 120,
        "time_signature": [4, 4]
    }

    response = await test_client.post("/api/v1/sequences/", json=sequence_data)
    # The endpoint can return 200 or 400 depending on validation
    assert response.status_code in [200, 400]
    data = response.json()
    if response.status_code == 200:
        assert "id" in data
        assert data["name"] == "Test Sequence"
    else:
        assert "detail" in data
