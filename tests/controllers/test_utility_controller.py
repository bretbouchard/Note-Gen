"""Tests for the utility controller."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from motor.motor_asyncio import AsyncIOMotorDatabase

from note_gen.controllers.utility_controller import UtilityController
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.note import Note
from note_gen.core.enums import ScaleType, PatternDirection


@pytest.fixture
def mock_db():
    """Create a mock database."""
    db = AsyncMock(spec=AsyncIOMotorDatabase)
    db.chord_progressions = AsyncMock()
    db.note_patterns = AsyncMock()
    db.rhythm_patterns = AsyncMock()
    db.sequences = AsyncMock()
    db.users = AsyncMock()
    return db


@pytest.fixture
def mock_repositories():
    """Create mock repositories."""
    chord_progression_repository = AsyncMock()
    note_pattern_repository = AsyncMock()
    rhythm_pattern_repository = AsyncMock()
    sequence_repository = AsyncMock()
    user_repository = AsyncMock()

    return {
        "chord_progression_repository": chord_progression_repository,
        "note_pattern_repository": note_pattern_repository,
        "rhythm_pattern_repository": rhythm_pattern_repository,
        "sequence_repository": sequence_repository,
        "user_repository": user_repository
    }


@pytest.fixture
def controller(mock_db, mock_repositories):
    """Create a utility controller instance."""
    return UtilityController(
        mock_db,
        mock_repositories["chord_progression_repository"],
        mock_repositories["note_pattern_repository"],
        mock_repositories["rhythm_pattern_repository"],
        mock_repositories["sequence_repository"],
        mock_repositories["user_repository"]
    )


@pytest.fixture
def sample_chord_progressions():
    """Create sample chord progressions."""
    # Mock the chord progressions to avoid validation issues
    chord_progression1 = MagicMock(spec=ChordProgression)
    chord_progression1.id = "507f1f77bcf86cd799439011"
    chord_progression1.name = "Test Progression 1"
    chord_progression1.key = "C"
    chord_progression1.scale_type = "MAJOR"
    chord_progression1.chords = []
    chord_progression1.model_dump.return_value = {
        "id": "507f1f77bcf86cd799439011",
        "name": "Test Progression 1",
        "key": "C",
        "scale_type": "MAJOR",
        "chords": []
    }

    chord_progression2 = MagicMock(spec=ChordProgression)
    chord_progression2.id = "507f1f77bcf86cd799439012"
    chord_progression2.name = "Test Progression 2"
    chord_progression2.key = "G"
    chord_progression2.scale_type = "MINOR"
    chord_progression2.chords = []
    chord_progression2.model_dump.return_value = {
        "id": "507f1f77bcf86cd799439012",
        "name": "Test Progression 2",
        "key": "G",
        "scale_type": "MINOR",
        "chords": []
    }

    return [chord_progression1, chord_progression2]


@pytest.fixture
def sample_note_patterns():
    """Create sample note patterns."""
    # Mock the note patterns to avoid validation issues
    note_pattern1 = MagicMock(spec=NotePattern)
    note_pattern1.id = "507f1f77bcf86cd799439013"
    note_pattern1.name = "Test Pattern 1"
    note_pattern1.complexity = 3.0
    note_pattern1.tags = ["test", "pattern"]
    note_pattern1.model_dump.return_value = {
        "id": "507f1f77bcf86cd799439013",
        "name": "Test Pattern 1",
        "complexity": 3.0,
        "tags": ["test", "pattern"],
        "data": {
            "notes": [{"pitch": "C", "octave": 4, "duration": 1.0, "velocity": 100}],
            "scale_type": "MAJOR",
            "direction": "up"
        }
    }

    note_pattern2 = MagicMock(spec=NotePattern)
    note_pattern2.id = "507f1f77bcf86cd799439014"
    note_pattern2.name = "Test Pattern 2"
    note_pattern2.complexity = 4.0
    note_pattern2.tags = ["test", "pattern"]
    note_pattern2.model_dump.return_value = {
        "id": "507f1f77bcf86cd799439014",
        "name": "Test Pattern 2",
        "complexity": 4.0,
        "tags": ["test", "pattern"],
        "data": {
            "notes": [{"pitch": "D", "octave": 4, "duration": 1.0, "velocity": 100}],
            "scale_type": "MINOR",
            "direction": "down"
        }
    }

    return [note_pattern1, note_pattern2]


@pytest.fixture
def sample_rhythm_patterns():
    """Create sample rhythm patterns."""
    # Mock the rhythm patterns to avoid validation issues
    rhythm_pattern1 = MagicMock(spec=RhythmPattern)
    rhythm_pattern1.id = "507f1f77bcf86cd799439015"
    rhythm_pattern1.name = "Test Rhythm 1"
    rhythm_pattern1.time_signature = [4, 4]
    rhythm_pattern1.notes = [MagicMock(spec=RhythmNote)]
    rhythm_pattern1.model_dump.return_value = {
        "id": "507f1f77bcf86cd799439015",
        "name": "Test Rhythm 1",
        "time_signature": [4, 4],
        "notes": [{"position": 0, "duration": 1.0, "velocity": 100}]
    }

    rhythm_pattern2 = MagicMock(spec=RhythmPattern)
    rhythm_pattern2.id = "507f1f77bcf86cd799439016"
    rhythm_pattern2.name = "Test Rhythm 2"
    rhythm_pattern2.time_signature = [3, 4]
    rhythm_pattern2.notes = [MagicMock(spec=RhythmNote)]
    rhythm_pattern2.model_dump.return_value = {
        "id": "507f1f77bcf86cd799439016",
        "name": "Test Rhythm 2",
        "time_signature": [3, 4],
        "notes": [{"position": 0, "duration": 0.5, "velocity": 100}]
    }

    return [rhythm_pattern1, rhythm_pattern2]


@pytest.mark.asyncio
async def test_create(mock_db, mock_repositories):
    """Test the create factory method."""
    controller = await UtilityController.create(
        mock_db,
        mock_repositories["chord_progression_repository"],
        mock_repositories["note_pattern_repository"],
        mock_repositories["rhythm_pattern_repository"],
        mock_repositories["sequence_repository"],
        mock_repositories["user_repository"]
    )

    assert isinstance(controller, UtilityController)
    assert controller.db is mock_db
    assert controller.chord_progression_repository is mock_repositories["chord_progression_repository"]
    assert controller.note_pattern_repository is mock_repositories["note_pattern_repository"]
    assert controller.rhythm_pattern_repository is mock_repositories["rhythm_pattern_repository"]
    assert controller.sequence_repository is mock_repositories["sequence_repository"]
    assert controller.user_repository is mock_repositories["user_repository"]


@pytest.mark.asyncio
async def test_health_check(controller):
    """Test the health check endpoint."""
    result = await controller.health_check()
    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_statistics(controller, mock_db):
    """Test getting statistics."""
    # Setup mocks
    mock_db.chord_progressions.count_documents.return_value = 10
    mock_db.note_patterns.count_documents.return_value = 20
    mock_db.rhythm_patterns.count_documents.return_value = 15
    mock_db.sequences.count_documents.return_value = 5
    mock_db.users.count_documents.return_value = 3

    # Call method
    result = await controller.get_statistics()

    # Verify
    assert result["statistics"]["chord_progressions"] == 10
    assert result["statistics"]["note_patterns"] == 20
    assert result["statistics"]["rhythm_patterns"] == 15
    assert result["statistics"]["sequences"] == 5
    assert result["statistics"]["users"] == 3

    # Verify calls - use any() to match any arguments
    assert mock_db.chord_progressions.count_documents.call_count >= 1
    assert mock_db.note_patterns.count_documents.call_count >= 1
    assert mock_db.rhythm_patterns.count_documents.call_count >= 1
    assert mock_db.sequences.count_documents.call_count >= 1
    assert mock_db.users.count_documents.call_count >= 1


@pytest.mark.asyncio
async def test_list_all_patterns(controller, mock_repositories, sample_chord_progressions, sample_note_patterns, sample_rhythm_patterns):
    """Test listing all patterns."""
    # Setup mocks
    mock_repositories["chord_progression_repository"].find_all.return_value = sample_chord_progressions
    mock_repositories["note_pattern_repository"].find_all.return_value = sample_note_patterns
    mock_repositories["rhythm_pattern_repository"].find_all.return_value = sample_rhythm_patterns

    # Call method
    result = await controller.list_all_patterns()

    # Verify
    assert len(result["chord_progressions"]) == 2
    assert len(result["note_patterns"]) == 2
    assert len(result["rhythm_patterns"]) == 2

    # Check content
    assert result["chord_progressions"][0]["name"] == "Test Progression 1"
    assert result["chord_progressions"][1]["name"] == "Test Progression 2"
    assert result["note_patterns"][0]["name"] == "Test Pattern 1"
    assert result["note_patterns"][1]["name"] == "Test Pattern 2"
    assert result["rhythm_patterns"][0]["name"] == "Test Rhythm 1"
    assert result["rhythm_patterns"][1]["name"] == "Test Rhythm 2"

    # Verify calls
    mock_repositories["chord_progression_repository"].find_all.assert_called_once()
    mock_repositories["note_pattern_repository"].find_all.assert_called_once()
    mock_repositories["rhythm_pattern_repository"].find_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_api_info(controller):
    """Test getting API information."""
    result = await controller.get_api_info()

    assert result["app"] == "Note Generator API"
    assert "version" in result
    assert "description" in result
    assert "documentation" in result
    assert "endpoints" in result

    # Check endpoints
    endpoints = result["endpoints"]
    assert "/api/v1/chord-progressions" in endpoints
    assert "/api/v1/patterns" in endpoints
    assert "/api/v1/sequences" in endpoints
    assert "/api/v1/users" in endpoints
    assert "/api/v1/validation" in endpoints
    assert "/api/v1/import-export" in endpoints
    assert "/health" in endpoints
    assert "/stats" in endpoints
    assert "/patterns-list" in endpoints
