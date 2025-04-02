"""Tests for the chord progression controller."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.note_gen.controllers.chord_progression_controller import ChordProgressionController
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord import Chord


@pytest.fixture
def mock_repository():
    """Create a mock repository for testing."""
    repository = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.find_all = AsyncMock(return_value=[])
    repository.create = AsyncMock()
    return repository


@pytest.fixture
def controller(mock_repository):
    """Create a controller instance for testing."""
    return ChordProgressionController(mock_repository)


@pytest.mark.asyncio
async def test_get_progression(controller, mock_repository):
    """Test getting a progression by ID."""
    # Arrange
    progression_id = "test_id"
    expected_progression = ChordProgression(
        name="Test Progression",
        key="C",
        scale_type="MAJOR",
        chords=[Chord(root=1, quality="MAJOR", duration=1)]
    )
    mock_repository.find_by_id.return_value = expected_progression

    # Act
    result = await controller.get_progression(progression_id)

    # Assert
    assert result == expected_progression
    mock_repository.find_by_id.assert_called_once_with(progression_id)


@pytest.mark.asyncio
async def test_get_all_progressions(controller, mock_repository):
    """Test getting all progressions."""
    # Arrange
    expected_progressions = [
        ChordProgression(
            name="Test Progression 1",
            key="C",
            scale_type="MAJOR",
            chords=[Chord(root=1, quality="MAJOR", duration=1)]
        ),
        ChordProgression(
            name="Test Progression 2",
            key="D",
            scale_type="MINOR",
            chords=[Chord(root=1, quality="MINOR", duration=1)]
        )
    ]
    mock_repository.find_all.return_value = expected_progressions

    # Act
    result = await controller.get_all_progressions()

    # Assert
    assert result == expected_progressions
    mock_repository.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_create_progression(controller, mock_repository):
    """Test creating a progression."""
    # Arrange
    progression_data = {
        "name": "New Progression",
        "key": "E",
        "scale_type": "MAJOR",
        "chords": [{"root": 1, "quality": "MAJOR", "duration": 1}]
    }
    expected_progression = ChordProgression(**progression_data)
    mock_repository.create.return_value = expected_progression

    # Act
    result = await controller.create_progression(progression_data)

    # Assert
    assert result == expected_progression
    mock_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_progression(controller, mock_repository):
    """Test generating a progression."""
    # Arrange
    key = "F"
    scale_type = "MINOR"
    complexity = 0.7
    num_chords = 3
    
    # Mock the create method to return the generated progression
    def mock_create(progression):
        return progression
    
    mock_repository.create.side_effect = mock_create

    # Act
    result = await controller.generate_progression(key, scale_type, complexity, num_chords)

    # Assert
    assert result.name == f"Generated {key} {scale_type} Progression"
    assert result.key == key
    assert result.scale_type == scale_type
    assert len(result.chords) == num_chords
    mock_repository.create.assert_called_once()
