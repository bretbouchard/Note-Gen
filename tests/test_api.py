import pytest
from fastapi.testclient import TestClient
from src.note_gen.routers.user_routes import app, get_db
from tests.test_user_routes import get_test_db, init_test_db, setup_test_data

@pytest.fixture(scope="module")
def test_client() -> TestClient:
    """Test client fixture."""
    app.dependency_overrides[get_db] = get_test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_get_chord_progressions(test_client: TestClient, setup_test_data: None) -> None:
    response = test_client.get('/chord-progressions')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_note_patterns(test_client: TestClient, setup_test_data: None) -> None:
    response = test_client.get('/note-patterns')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_rhythm_patterns(test_client: TestClient, setup_test_data: None) -> None:
    response = test_client.get('/rhythm-patterns')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_endpoint(test_client: TestClient, setup_test_data: None) -> None:
    payload = {
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR"
        },
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4},
                "quality": "MAJOR"
            },
            {
                "root": {"note_name": "F", "octave": 4},
                "quality": "MAJOR"
            }
        ]
    }
    response = test_client.post('/generate_progression', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["id"], str)
    assert "name" in data
    assert "chords" in data
    assert isinstance(data["chords"], list)
    assert len(data["chords"]) > 0

def test_invalid_endpoint(test_client: TestClient) -> None:
    response = test_client.get('/invalid-endpoint')
    assert response.status_code == 404
