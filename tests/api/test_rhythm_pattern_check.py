"""
Tests for rhythm pattern functionality.
"""

import os
import sys
import pytest
from httpx import AsyncClient
from src.note_gen.main import app
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from bson import ObjectId
import uuid
import asyncio
from src.note_gen.database.db import get_db_conn, init_db, close_mongo_connection
import httpx
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@pytest.fixture(autouse=True)
async def test_db():
    """Fixture to provide a test database."""
    await init_db()
    db = await get_db_conn()
    
    # Clear all collections before each test
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})
    
    yield db
    
    # Clean up after test
    await close_mongo_connection()

@pytest.fixture
async def async_test_client():
    """Fixture to provide an async test client."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_rhythm_pattern(async_test_client):
    """
    Fixture to create a test rhythm pattern with a unique name.
    Ensures cleanup after the test.
    """
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )
    
    unique_name = f"Test Rhythm Pattern {uuid.uuid4()}"
    rhythm_pattern = RhythmPattern(
        name=unique_name,
        description="A test rhythm pattern",
        data=rhythm_data,
        tags=["test"],
        is_test=True
    )
    
    # Create the pattern
    request_data = rhythm_pattern.model_dump()
    logger.debug(f"POST Request URL: /api/v1/rhythm-patterns")
    logger.debug(f"POST Request Data: {request_data}")
    response = await async_test_client.post('/api/v1/rhythm-patterns', json=request_data)
    logger.debug(f"POST Response Status: {response.status_code}")
    logger.debug(f"POST Response Headers: {response.headers}")
    logger.debug(f"POST Response Content: {response.text}")
    
    assert response.status_code == 201
    created_pattern = response.json()

    # Cleanup the pattern after the test
    try:
        yield created_pattern
    finally:
        try:
            delete_url = f'/api/v1/rhythm-patterns/{created_pattern["id"]}'
            logger.debug(f"DELETE Request URL: {delete_url}")
            response = await async_test_client.delete(delete_url)
            logger.debug(f"DELETE Response Status: {response.status_code}")
            logger.debug(f"DELETE Response Content: {response.text}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

@pytest.mark.asyncio
async def test_rhythm_pattern_functionality(async_test_client, test_rhythm_pattern):
    # Test get rhythm pattern
    get_url = f'/api/v1/rhythm-patterns/{test_rhythm_pattern["id"]}'
    logger.debug(f"GET Request URL: {get_url}")
    response = await async_test_client.get(get_url)
    logger.debug(f"GET Response Status: {response.status_code}")
    logger.debug(f"GET Response Content: {response.text}")
    
    assert response.status_code == 200
    pattern = response.json()
    assert pattern["id"] == test_rhythm_pattern["id"]
    assert pattern["name"] == test_rhythm_pattern["name"]

@pytest.mark.asyncio
async def test_create_rhythm_pattern(async_test_client):
    """Test creating a rhythm pattern."""
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )
    
    unique_name = f"Test Rhythm Pattern {uuid.uuid4()}"
    rhythm_pattern = RhythmPattern(
        name=unique_name,
        description="A test rhythm pattern",
        data=rhythm_data,
        tags=["test"],
        is_test=True
    )
    
    request_data = rhythm_pattern.model_dump()
    logger.debug(f"POST Request URL: /api/v1/rhythm-patterns")
    logger.debug(f"POST Request Data: {request_data}")
    response = await async_test_client.post('/api/v1/rhythm-patterns', json=request_data)
    logger.debug(f"POST Response Status: {response.status_code}")
    logger.debug(f"POST Response Headers: {response.headers}")
    logger.debug(f"POST Response Content: {response.text}")
    
    assert response.status_code == 201
    created_pattern = response.json()
    assert created_pattern["name"] == unique_name

@pytest.mark.asyncio
async def test_create_duplicate_rhythm_pattern(async_test_client):
    """Test creating a rhythm pattern with a duplicate name."""
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )
    
    unique_name = f"Test Rhythm Pattern {uuid.uuid4()}"
    rhythm_pattern = RhythmPattern(
        name=unique_name,
        description="A test rhythm pattern",
        data=rhythm_data,
        tags=["test"],
        is_test=True
    )
    
    # Create first pattern
    request_data = rhythm_pattern.model_dump()
    logger.debug(f"POST Request URL: /api/v1/rhythm-patterns")
    logger.debug(f"POST Request Data: {request_data}")
    response = await async_test_client.post('/api/v1/rhythm-patterns', json=request_data)
    logger.debug(f"POST Response Status: {response.status_code}")
    logger.debug(f"POST Response Headers: {response.headers}")
    logger.debug(f"POST Response Content: {response.text}")
    
    assert response.status_code == 201
    
    # Try to create second pattern with same name
    response = await async_test_client.post('/api/v1/rhythm-patterns', json=request_data)
    logger.debug(f"POST Response Status: {response.status_code}")
    logger.debug(f"POST Response Headers: {response.headers}")
    logger.debug(f"POST Response Content: {response.text}")
    
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_create_invalid_rhythm_pattern(async_test_client):
    """Test creating an invalid rhythm pattern."""
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
        time_signature="invalid",  # Invalid time signature
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )
    
    unique_name = f"Test Rhythm Pattern {uuid.uuid4()}"
    rhythm_pattern = RhythmPattern(
        name=unique_name,
        description="A test rhythm pattern",
        data=rhythm_data,
        tags=["test"],
        is_test=True
    )
    
    request_data = rhythm_pattern.model_dump()
    logger.debug(f"POST Request URL: /api/v1/rhythm-patterns")
    logger.debug(f"POST Request Data: {request_data}")
    response = await async_test_client.post('/api/v1/rhythm-patterns', json=request_data)
    logger.debug(f"POST Response Status: {response.status_code}")
    logger.debug(f"POST Response Headers: {response.headers}")
    logger.debug(f"POST Response Content: {response.text}")
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_delete_rhythm_pattern(async_test_client):
    """Test creating and then deleting a rhythm pattern."""
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )
    
    unique_name = f"Test Rhythm Pattern {uuid.uuid4()}"
    rhythm_pattern = RhythmPattern(
        name=unique_name,
        description="A test rhythm pattern",
        data=rhythm_data,
        tags=["test"],
        is_test=True
    )
    
    # Create the pattern
    request_data = rhythm_pattern.model_dump()
    logger.debug(f"POST Request URL: /api/v1/rhythm-patterns")
    logger.debug(f"POST Request Data: {request_data}")
    response = await async_test_client.post('/api/v1/rhythm-patterns', json=request_data)
    logger.debug(f"POST Response Status: {response.status_code}")
    logger.debug(f"POST Response Headers: {response.headers}")
    logger.debug(f"POST Response Content: {response.text}")
    
    assert response.status_code == 201
    created_pattern = response.json()
    
    # Delete the pattern
    delete_url = f'/api/v1/rhythm-patterns/{created_pattern["id"]}'
    logger.debug(f"DELETE Request URL: {delete_url}")
    response = await async_test_client.delete(delete_url)
    logger.debug(f"DELETE Response Status: {response.status_code}")
    logger.debug(f"DELETE Response Content: {response.text}")
    
    assert response.status_code == 204
    
    # Verify pattern is deleted
    get_url = f'/api/v1/rhythm-patterns/{created_pattern["id"]}'
    logger.debug(f"GET Request URL: {get_url}")
    response = await async_test_client.get(get_url)
    logger.debug(f"GET Response Status: {response.status_code}")
    logger.debug(f"GET Response Content: {response.text}")
    
    assert response.status_code == 404
