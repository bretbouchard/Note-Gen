import asyncio
import pytest
import pytest_asyncio
import uuid
from fastapi.testclient import TestClient
from note_gen.database import get_db
from note_gen.routers.user_routes import app

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest_asyncio.fixture(scope="function")
async def setup_database():
    async for db in get_db():
        try:
            # Clear existing data
            await db.chord_progressions.delete_many({})
            
            # Setup code to insert test data into the database
            progression = {
                'id': str(uuid.uuid4()),
                'name': 'Test Base Progression',
                'chords': ['C', 'G', 'Am', 'F'],
                'key': 'C',
                'scale_type': 'major',
                'complexity': 0.5
            }
            await db.chord_progressions.insert_one(progression)
            yield db
        except Exception as e:
            print(f"Error during database setup: {e}")
            raise
        finally:
            # Cleanup
            await db.chord_progressions.delete_many({})

@pytest.mark.asyncio
async def test_create_chord_progression(client, setup_database):
    test_progression = {
        "id": str(uuid.uuid4()),
        "name": "Test Create Progression",
        "chords": ["C", "F", "G", "C"],
        "key": "C",
        "scale_type": "major",
        "complexity": 0.5
    }
    
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == test_progression["name"]
    assert data["chords"] == test_progression["chords"]
    assert data["key"] == test_progression["key"]
    assert data["scale_type"] == test_progression["scale_type"]
    assert data["complexity"] == test_progression["complexity"]

@pytest.mark.asyncio
async def test_create_duplicate_chord_progression(client, setup_database):
    test_progression = {
        "id": str(uuid.uuid4()),
        "name": "Test Duplicate Progression",
        "chords": ["C", "F", "G", "C"],
        "key": "C",
        "scale_type": "major",
        "complexity": 0.5
    }
    
    # Create first progression
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 200
    
    # Try to create duplicate
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_chord_progression(client, setup_database):
    # Create a progression first
    test_progression = {
        "id": str(uuid.uuid4()),
        "name": "Test Get Progression",
        "chords": ["C", "F", "G", "C"],
        "key": "C",
        "scale_type": "major",
        "complexity": 0.5
    }
    
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 200
    created_progression = response.json()
    
    # Get the progression
    response = client.get(f"/chord-progressions/{created_progression['id']}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == created_progression["id"]
    assert data["name"] == test_progression["name"]
    assert data["chords"] == test_progression["chords"]
    assert data["key"] == test_progression["key"]
    assert data["scale_type"] == test_progression["scale_type"]
    assert data["complexity"] == test_progression["complexity"]

@pytest.mark.asyncio
async def test_invalid_chord_progression_id(client):
    response = client.get("/chord-progressions/invalid_id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_and_delete_chord_progression(client, setup_database):
    # Create a progression
    test_progression = {
        "id": str(uuid.uuid4()),
        "name": "Test Delete Progression",
        "chords": ["C", "F", "G", "C"],
        "key": "C",
        "scale_type": "major",
        "complexity": 0.5
    }
    
    response = client.post("/chord-progressions", json=test_progression)
    assert response.status_code == 200
    
    # Delete the progression
    response = client.delete(f"/chord-progressions/{test_progression['id']}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify it's gone
    response = client.get(f"/chord-progressions/{test_progression['id']}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_invalid_chord_progression(client):
    progression = {
        "name": "Invalid Progression",
        # Missing required fields
    }
    response = client.post('/chord-progressions', json=progression)
    assert response.status_code == 422  # Validation error
