import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_note_sequences(test_client: AsyncClient):
    response = await test_client.get("/api/v1/note-sequences/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_note_sequence_functionality(test_client: AsyncClient):
    # Test data
    sequence_data = {
        "name": "Test Sequence",
        "notes": [
            {"pitch": 60, "duration": 1.0, "velocity": 100},
            {"pitch": 62, "duration": 0.5, "velocity": 90}
        ]
    }

    # Create a new sequence
    create_response = await test_client.post("/api/v1/note-sequences/", json=sequence_data)
    assert create_response.status_code == 201

    # Get the created sequence ID
    created_data = create_response.json()
    assert "_id" in created_data
    sequence_id = created_data["_id"]

    # Get the sequence by ID
    get_response = await test_client.get(f"/api/v1/note-sequences/{sequence_id}")
    assert get_response.status_code == 200

    # Verify the sequence data
    sequence = get_response.json()
    assert sequence["name"] == sequence_data["name"]
    assert len(sequence["notes"]) == len(sequence_data["notes"])
