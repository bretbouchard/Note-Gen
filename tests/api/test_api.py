from typing import List, Dict, Any, Optional, AsyncGenerator
from collections.abc import AsyncGenerator as AsyncGeneratorABC

from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


pytestmark = pytest.mark.asyncio  # This marks all test functions in the file as async


from typing import List, Dict, Any, Optional
from collections.abc import AsyncIterator

class MockCursor(AsyncIterator[Dict[str, Any]]):
    def __init__(self, items: List[Dict[str, Any]]) -> None:
        self.items = items
        self.current = 0

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.items

    def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        return self

    async def __anext__(self) -> Dict[str, Any]:
        if self.current >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.current]
        self.current += 1
        return item

class MockCollection:
    def __init__(self, items: List[Dict[str, Any]]) -> None:
        self.items = items

    async def find(self, query: Optional[Dict[str, Any]] = None):
        # Simulate asynchronous behavior
        return MockCursor(self.items)

    async def find_one(self, query: Dict[str, Any]):
        # Simulate asynchronous behavior
        for item in self.items:
            if item.get('_id') == query.get('_id'):
                return item
        return None

    async def insert_one(self, document: Dict[str, Any]):
        # Simulate asynchronous behavior
        self.items.append(document)


class MockDatabase:
    def __init__(self) -> None:
        # Update chord progressions mock with correct root format
        self.chord_progressions = MockCollection([{
            "_id": "1",
            "name": "Test Progression",
            "chords": [
                {
                    "name": "C",
                    "root": {"note": "C", "octave": 4},  # Root as dictionary
                    "quality": "major",
                    "intervals": [0, 4, 7]
                },
                {
                    "name": "G",
                    "root": {"note": "G", "octave": 4},  # Root as dictionary
                    "quality": "major",
                    "intervals": [0, 4, 7]
                },
                {
                    "name": "Am",
                    "root": {"note": "A", "octave": 4},  # Root as dictionary
                    "quality": "minor",
                    "intervals": [0, 3, 7]
                },
                {
                    "name": "F",
                    "root": {"note": "F", "octave": 4},  # Root as dictionary
                    "quality": "major",
                    "intervals": [0, 4, 7]
                }
            ],
            "scale_info": {
                "root": "C",
                "scale_type": "major",
                "intervals": [0, 2, 4, 5, 7, 9, 11]
            }
        }])

        # Keep note patterns as is since it's working
        self.note_patterns = MockCollection([{
            "_id": "1",
            "name": "Test Pattern",
            "notes": [
                {
                    "note_name": "C",
                    "duration": 1.0,
                    "velocity": 64,
                    "octave": 4
                },
                {
                    "note_name": "E",
                    "duration": 1.0,
                    "velocity": 64,
                    "octave": 4
                },
                {
                    "note_name": "G",
                    "duration": 1.0,
                    "velocity": 64,
                    "octave": 4
                }
            ],
            "description": "Basic pattern",
            "tags": ["test"]
        }])

        # Keep rhythm patterns as is for now
        self.rhythm_patterns = MockCollection([{
            "id": "1",
            "name": "Test Rhythm",
            "pattern": "1 1",  # Changed from "1010" to a valid pattern
            "description": "Basic rhythm",
            "tags": ["test"],
            "data": {
                "notes": [{
                    "position": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "is_rest": False
                }],
                "time_signature": "4/4",
                "swing_enabled": False,
                "humanize_amount": 0.0,
                "swing_ratio": 0.67,
                "default_duration": 1.0,
                "total_duration": 1.0,
                "accent_pattern": [],
                "groove_type": "straight",
                "variation_probability": 0.0,
                "duration": 1.0,
                "style": "basic"
            },
            "complexity": 1.0,
            "style": "basic",
            "is_test": True
        }])


@pytest.fixture(scope="module")
def app():
    from main import app
    return app


@pytest.fixture
async def test_client(app: TestClient) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: MockDatabase()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True
    ) as client:
        yield client


# Consolidated tests for API functionality

@pytest.mark.asyncio
async def test_api_functionality(client):
    # Test get chord progressions
    response = await client.get("/chord-progressions")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test get note patterns
    response = await client.get("/note-patterns")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test get rhythm patterns
    response = await client.get("/rhythm-patterns")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test post endpoint
    test_data = {
        "name": "New Pattern",
        "notes": [
            {
                "note_name": "D4",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            },
            {
                "note_name": "F4",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            },
            {
                "note_name": "A4",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            }
        ],
        "pattern_type": "melody",
        "description": "New test pattern",
        "tags": ["test", "new"]
    }
    response = await client.post("/note-patterns", json=test_data)
    assert response.status_code == 200
    response_data = response.json()
    assert "id" in response_data  # Check for id instead of message

    # Test get note pattern by id
    response = await client.get("/note-patterns/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Pattern"

    # Test update note pattern
    update_data = {
        "name": "Updated Pattern",
        "notes": [
            {
                "note_name": "C",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            },
            {
                "note_name": "E",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            },
            {
                "note_name": "G",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            }
        ],
        "description": "Updated pattern",
        "tags": ["test", "updated"]
    }
    response = await client.put("/note-patterns/1", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "Updated Pattern"

    # Test delete note pattern
    response = await client.delete("/note-patterns/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Note pattern deleted successfully"

    # Test get rhythm pattern by id
    response = await client.get("/rhythm-patterns/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Rhythm"

    # Test update rhythm pattern
    update_data = {
        "name": "Updated Rhythm",
        "pattern": "1 1",
        "description": "Updated rhythm",
        "tags": ["test", "updated"]
    }
    response = await client.put("/rhythm-patterns/1", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "Updated Rhythm"

    # Test delete rhythm pattern
    response = await client.delete("/rhythm-patterns/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Rhythm pattern deleted successfully"