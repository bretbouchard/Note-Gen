"""Tests for the import/export router."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from note_gen.routers.import_export import router
from note_gen.controllers.import_export_controller import ImportExportController


@pytest.fixture
def app():
    """Create a test app with the import/export router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_controller():
    """Create a mock import/export controller."""
    controller = AsyncMock(spec=ImportExportController)
    return controller


def test_export_chord_progressions_json(client, mock_controller):
    """Test exporting chord progressions to JSON."""
    # Setup mock
    mock_data = json.dumps([
        {"name": "Test Progression 1", "key": "C", "scale_type": "MAJOR"},
        {"name": "Test Progression 2", "key": "G", "scale_type": "MINOR"}
    ])
    mock_controller.export_chord_progressions.return_value = mock_data

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/export/chord-progressions?format=json")

        # Verify
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.headers["Content-Disposition"] == "attachment; filename=chord_progressions.json"

        data = json.loads(response.content)
        assert len(data) == 2
        assert data[0]["name"] == "Test Progression 1"
        assert data[1]["name"] == "Test Progression 2"

        mock_controller.export_chord_progressions.assert_called_once_with("json")


def test_export_chord_progressions_csv(client, mock_controller):
    """Test exporting chord progressions to CSV."""
    # Setup mock
    mock_data = b"name,key,scale_type\nTest Progression 1,C,MAJOR\nTest Progression 2,G,MINOR"
    mock_controller.export_chord_progressions.return_value = mock_data

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/export/chord-progressions?format=csv")

        # Verify
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv"
        assert response.headers["Content-Disposition"] == "attachment; filename=chord_progressions.csv"

        content = response.content.decode()
        assert "name,key,scale_type" in content
        assert "Test Progression 1,C,MAJOR" in content
        assert "Test Progression 2,G,MINOR" in content

        mock_controller.export_chord_progressions.assert_called_once_with("csv")


def test_export_note_patterns(client, mock_controller):
    """Test exporting note patterns."""
    # Setup mock
    mock_data = json.dumps([
        {"name": "Test Pattern 1"},
        {"name": "Test Pattern 2"}
    ])
    mock_controller.export_note_patterns.return_value = mock_data

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/export/note-patterns")

        # Verify
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.headers["Content-Disposition"] == "attachment; filename=note_patterns.json"

        data = json.loads(response.content)
        assert len(data) == 2
        assert data[0]["name"] == "Test Pattern 1"
        assert data[1]["name"] == "Test Pattern 2"

        mock_controller.export_note_patterns.assert_called_once_with("json")


def test_export_rhythm_patterns(client, mock_controller):
    """Test exporting rhythm patterns."""
    # Setup mock
    mock_data = json.dumps([
        {"name": "Test Rhythm 1"},
        {"name": "Test Rhythm 2"}
    ])
    mock_controller.export_rhythm_patterns.return_value = mock_data

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/export/rhythm-patterns")

        # Verify
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.headers["Content-Disposition"] == "attachment; filename=rhythm_patterns.json"

        data = json.loads(response.content)
        assert len(data) == 2
        assert data[0]["name"] == "Test Rhythm 1"
        assert data[1]["name"] == "Test Rhythm 2"

        mock_controller.export_rhythm_patterns.assert_called_once_with("json")


def test_export_sequences(client, mock_controller):
    """Test exporting sequences."""
    # Setup mock
    mock_data = json.dumps([
        {"name": "Test Sequence 1"},
        {"name": "Test Sequence 2"}
    ])
    mock_controller.export_sequences.return_value = mock_data

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/export/sequences")

        # Verify
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.headers["Content-Disposition"] == "attachment; filename=sequences.json"

        data = json.loads(response.content)
        assert len(data) == 2
        assert data[0]["name"] == "Test Sequence 1"
        assert data[1]["name"] == "Test Sequence 2"

        mock_controller.export_sequences.assert_called_once_with("json")


def test_import_chord_progressions(client, mock_controller):
    """Test importing chord progressions."""
    # Setup mock
    mock_controller.import_chord_progressions.return_value = 2

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Create test file
        test_data = [
            {"name": "Test Progression 1", "key": "C", "scale_type": "MAJOR"},
            {"name": "Test Progression 2", "key": "G", "scale_type": "MINOR"}
        ]
        files = {"file": ("test.json", json.dumps(test_data), "application/json")}

        # Call endpoint
        response = client.post("/import/chord-progressions", files=files)

        # Verify
        assert response.status_code == 200
        assert response.json()["imported_count"] == 2


def test_import_note_patterns(client, mock_controller):
    """Test importing note patterns."""
    # Setup mock
    mock_controller.import_note_patterns.return_value = 2

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Create test file
        test_data = [
            {"name": "Test Pattern 1"},
            {"name": "Test Pattern 2"}
        ]
        files = {"file": ("test.json", json.dumps(test_data), "application/json")}

        # Call endpoint
        response = client.post("/import/note-patterns", files=files)

        # Verify
        assert response.status_code == 200
        assert response.json()["imported_count"] == 2


def test_import_rhythm_patterns(client, mock_controller):
    """Test importing rhythm patterns."""
    # Setup mock
    mock_controller.import_rhythm_patterns.return_value = 2

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Create test file
        test_data = [
            {"name": "Test Rhythm 1"},
            {"name": "Test Rhythm 2"}
        ]
        files = {"file": ("test.json", json.dumps(test_data), "application/json")}

        # Call endpoint
        response = client.post("/import/rhythm-patterns", files=files)

        # Verify
        assert response.status_code == 200
        assert response.json()["imported_count"] == 2


def test_import_sequences(client, mock_controller):
    """Test importing sequences."""
    # Setup mock
    mock_controller.import_sequences.return_value = 2

    # Patch the dependency
    with patch("note_gen.routers.import_export.get_import_export_controller", return_value=mock_controller):
        # Create test file
        test_data = [
            {"name": "Test Sequence 1"},
            {"name": "Test Sequence 2"}
        ]
        files = {"file": ("test.json", json.dumps(test_data), "application/json")}

        # Call endpoint
        response = client.post("/import/sequences", files=files)

        # Verify
        assert response.status_code == 200
        assert response.json()["imported_count"] == 2
