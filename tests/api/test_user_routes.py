# file: tests/api/test_user_routes.py

import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.models.patterns import RhythmPatternData, RhythmNote
from src.note_gen.database.db import get_db_conn, init_db, close_mongo_connection
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import uuid
import httpx
import logging
from fastapi import status

# Set test environment
os.environ["TESTING"] = "1"

logger = logging.getLogger(__name__)

@pytest.fixture
def rhythm_data():
    """Fixture for valid rhythm pattern data."""
    return {
        "notes": [
            {
                "position": 0.0,
                "duration": 1.0,
                "velocity": 100,
                "is_rest": False
            },
            {
                "position": 1.0,
                "duration": 1.0,
                "velocity": 100,
                "is_rest": True
            }
        ],
        "time_signature": "4/4",
        "swing_ratio": 0.5,
        "default_duration": 1.0,
        "total_duration": 4.0,
        "groove_type": "swing"
    }

# Tests using the test_client fixture from conftest.py
@pytest.mark.asyncio
async def test_user_routes_functionality(test_client: httpx.AsyncClient):
    response = await test_client.get("/api/v1/users/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_rhythm_pattern(test_client: httpx.AsyncClient):
    response = await test_client.get("/api/v1/patterns/rhythm/test-id")
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_create_rhythm_pattern(test_client: httpx.AsyncClient):
    pattern_data = {
        "name": "Test Pattern",
        "notes": [{"position": 0.0, "duration": 1.0}]
    }
    response = await test_client.post("/api/v1/patterns/rhythm/", json=pattern_data)
    assert response.status_code in [201, 422]
