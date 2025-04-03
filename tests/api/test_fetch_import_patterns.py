"""Test pattern fetching endpoints."""
import pytest
from httpx import AsyncClient
from bson import ObjectId
from note_gen.models.patterns import NotePattern

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_note_pattern():
    """Create a mock note pattern for testing."""
    from note_gen.models.note import Note
    return NotePattern(
        name="Test Pattern",
        pattern=[Note(pitch="C", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None)]
    )

class TestPatternFetching:
    async def test_fetch_pattern_by_id(self, test_client: AsyncClient, mock_note_pattern):
        # Create a pattern to fetch
        pattern_id = str(ObjectId())
        mock_note_pattern.id = pattern_id

        # Mock the repository to return the pattern
        from note_gen.controllers.pattern_controller import PatternController
        original_get_note_pattern = PatternController.get_note_pattern

        async def mock_get_note_pattern(self, pattern_id):
            return mock_note_pattern

        PatternController.get_note_pattern = mock_get_note_pattern

        try:
            # Fetch the pattern
            response = await test_client.get(f"/api/v1/patterns/{pattern_id}?type=note")

            # Check the response
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == pattern_id
            assert data["name"] == mock_note_pattern.name
        finally:
            # Restore the original method
            PatternController.get_note_pattern = original_get_note_pattern

    async def test_fetch_nonexistent_pattern(self, test_client: AsyncClient):
        # Generate a random pattern ID
        pattern_id = str(ObjectId())

        # Mock the repository to return None
        from note_gen.controllers.pattern_controller import PatternController
        original_get_note_pattern = PatternController.get_note_pattern

        async def mock_get_note_pattern(self, pattern_id):
            return None

        PatternController.get_note_pattern = mock_get_note_pattern

        try:
            # Fetch the pattern
            response = await test_client.get(f"/api/v1/patterns/{pattern_id}?type=note")

            # Check the response
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()
        finally:
            # Restore the original method
            PatternController.get_note_pattern = original_get_note_pattern

    async def test_database_error(self, test_client: AsyncClient, monkeypatch):
        # Generate a random pattern ID
        pattern_id = str(ObjectId())

        # Mock the repository to raise an exception
        from note_gen.controllers.pattern_controller import PatternController
        original_get_note_pattern = PatternController.get_note_pattern

        async def mock_get_note_pattern(self, pattern_id):
            raise Exception("Database error")

        PatternController.get_note_pattern = mock_get_note_pattern

        try:
            # Fetch the pattern
            response = await test_client.get(f"/api/v1/patterns/{pattern_id}?type=note")

            # Check the response
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "database error" in data["detail"].lower()
        finally:
            # Restore the original method
            PatternController.get_note_pattern = original_get_note_pattern


