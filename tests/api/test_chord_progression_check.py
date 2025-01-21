import asyncio
import pytest
import pytest_asyncio
import uuid
from main import app
from httpx import AsyncClient
from src.note_gen.database import get_db
from bson import ObjectId


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def setup_database():
    async with get_db() as db:
        # Clear existing data
        await db.chord_progressions.delete_many({})
        
        # Setup code to insert test data into the database
        progression = {
            'id': str(ObjectId()),
            'name': 'Test Base Progression',
            'chords': ['C', 'G', 'Am', 'F'],
            'key': 'C',
            'scale_type': 'major',
            'complexity': 0.5
        }
        await db.chord_progressions.insert_one(progression)
        yield db

# Consolidated tests for chord progression functionality

@pytest.mark.asyncio
async def test_chord_progression_functionality(client, setup_database):
    # Test create chord progression
    test_progression = {
        "id": str(ObjectId()),
        "name": "Test Create Progression",
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "major"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "major"}
        ],
        "key": "C",
        "scale_type": "major",
        "complexity": 0.5
    }
    
    response = await client.post("http://localhost:8000/chord-progressions", json=test_progression)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == test_progression["name"]
    assert data["chords"] == test_progression["chords"]
    assert data["key"] == test_progression["key"]
    assert data["scale_type"] == test_progression["scale_type"]
    assert data["complexity"] == test_progression["complexity"]

    # Test create duplicate chord progression
    test_progression = {
        "id": str(ObjectId()),
        "name": "Test Duplicate Progression",
        "chords": ["C", "F", "G", "C"],
        "key": "C",
        "scale_type": "major",
        "complexity": 0.5
    }
    
    # Create first progression
    response = await client.post("http://localhost:8000/chord-progressions", json=test_progression)
    assert response.status_code == 201
    
    # Try to create duplicate
    response = await client.post("http://localhost:8000/chord-progressions", json=test_progression)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

    # Test get chord progression
    # Create a progression first
    test_progression = {
        "id": str(ObjectId()),
        "name": "Test Get Progression",
        "chords": ["C", "F", "G", "C"],
        "key": "C",
        "scale_type": "major",
        "complexity": 0.5
    }
    
    response = await client.post("http://localhost:8000/chord-progressions", json=test_progression)
    assert response.status_code == 201
    created_progression = response.json()
    
    # Get the progression
    response = await client.get(f"http://localhost:8000/chord-progressions/{created_progression['id']}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == created_progression["id"]
    assert data["name"] == test_progression["name"]
    assert data["chords"] == test_progression["chords"]
    assert data["key"] == test_progression["key"]
    assert data["scale_type"] == test_progression["scale_type"]
    assert data["complexity"] == test_progression["complexity"]

    # Test invalid chord progression id
    response = await client.get("http://localhost:8000/chord-progressions/invalid_id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

    # Test create and delete chord progression
    # Create a progression
    test_progression = {
        "id": str(ObjectId()),
        "name": "Test Delete Progression",
        "chords": ["C", "F", "G", "C"],
        "key": "C",
        "scale_type": "major",
        "complexity": 0.5
    }
    
    response = await client.post("http://localhost:8000/chord-progressions", json=test_progression)
    assert response.status_code == 201
    
    # Delete the progression
    response = await client.delete(f"http://localhost:8000/chord-progressions/{test_progression['id']}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify it's gone
    response = await client.get(f"http://localhost:8000/chord-progressions/{test_progression['id']}")
    assert response.status_code == 404

    # Test invalid chord progression
    progression = {
        "name": "Invalid Progression",
        # Missing required fields
    }
    response = await client.post("http://localhost:8000/chord-progressions", json=progression)
    assert response.status_code == 422  # Validation error

    # Test create chord progression with db
    progression = {
        'id': str(ObjectId()),
        'name': 'Test Progression',
        'chords': ['C', 'G', 'Am', 'F'],
        'key': 'C',
        'scale_type': 'major',
        'complexity': 0.5
    }
    response = await client.post("http://localhost:8000/chord-progressions", json=progression)
    assert response.status_code == 201

    # Test create duplicate chord progression with db
    progression = {
        'id': str(ObjectId()),
        'name': 'Test Progression',
        'chords': ['C', 'G', 'Am', 'F'],
        'key': 'C',
        'scale_type': 'major',
        'complexity': 0.5
    }
    await setup_database.chord_progressions.insert_one(progression)
    response = await client.post("http://localhost:8000/chord-progressions", json=progression)
    assert response.status_code == 400

    # Test get chord progression with db
    response = await client.get("http://localhost:8000/chord-progressions/1")
    assert response.status_code == 200

    # Test invalid chord progression id with db
    response = await client.get("http://localhost:8000/chord-progressions/invalid_id")
    assert response.status_code == 404

    # Test create and delete chord progression with db
    progression = {
        'id': str(ObjectId()),
        'name': 'Test Progression',
        'chords': ['C', 'G', 'Am', 'F'],
        'key': 'C',
        'scale_type': 'major',
        'complexity': 0.5
    }
    response = await client.post("http://localhost:8000/chord-progressions", json=progression)
    assert response.status_code == 201
    
    # Now delete the progression
    response = await client.delete(f"http://localhost:8000/chord-progressions/{progression['id']}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
