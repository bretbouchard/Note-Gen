"""Tests for the pattern controller."""
import pytest
from unittest.mock import AsyncMock

from note_gen.controllers.pattern_controller import PatternController
from note_gen.models.patterns import NotePattern, RhythmPattern
from note_gen.models.note import Note
from note_gen.models.patterns import RhythmNote


@pytest.fixture
def mock_note_pattern_repository():
    """Create a mock note pattern repository for testing."""
    repository = AsyncMock()
    repository.find_one = AsyncMock()
    repository.find_many = AsyncMock(return_value=[])
    repository.create = AsyncMock()
    repository.find_many = AsyncMock(return_value=[])
    return repository


@pytest.fixture
def mock_rhythm_pattern_repository():
    """Create a mock rhythm pattern repository for testing."""
    repository = AsyncMock()
    repository.find_one = AsyncMock()
    repository.find_many = AsyncMock(return_value=[])
    repository.create = AsyncMock()
    repository.find_many = AsyncMock(return_value=[])
    return repository


@pytest.fixture
def controller(mock_note_pattern_repository, mock_rhythm_pattern_repository):
    """Create a controller instance for testing."""
    return PatternController(mock_note_pattern_repository, mock_rhythm_pattern_repository)


@pytest.mark.asyncio
async def test_get_note_pattern(controller, mock_note_pattern_repository):
    """Test getting a note pattern by ID."""
    # Arrange
    pattern_id = "test_id"
    expected_pattern = NotePattern(
        name="Test Pattern",
        description="A test pattern",
        pattern=[Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60), Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)],
        tags=["test", "pattern"]
    )
    mock_note_pattern_repository.find_one.return_value = expected_pattern

    # Act
    result = await controller.get_note_pattern(pattern_id)

    # Assert
    assert result == expected_pattern
    mock_note_pattern_repository.find_one.assert_called_once_with(pattern_id)


@pytest.mark.asyncio
async def test_get_all_note_patterns(controller, mock_note_pattern_repository):
    """Test getting all note patterns."""
    # Arrange
    expected_patterns = [
        NotePattern(
            name="Test Pattern 1",
            description="A test pattern",
            pattern=[Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60), Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)],
            tags=["test", "pattern"]
        ),
        NotePattern(
            name="Test Pattern 2",
            description="Another test pattern",
            pattern=[Note(pitch="E", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=64), Note(pitch="F", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=65)],
            tags=["test", "pattern"]
        )
    ]
    mock_note_pattern_repository.find_many.return_value = expected_patterns

    # Act
    result = await controller.get_all_note_patterns()

    # Assert
    assert result == expected_patterns
    mock_note_pattern_repository.find_many.assert_called_once()


@pytest.mark.asyncio
async def test_create_note_pattern(controller, mock_note_pattern_repository):
    """Test creating a note pattern."""
    # Arrange
    pattern_data = {
        "name": "New Pattern",
        "description": "A new pattern",
        "pattern": [Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60), Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)],
        "tags": ["new", "pattern"]
    }
    expected_pattern = NotePattern(**pattern_data)
    mock_note_pattern_repository.create.return_value = expected_pattern

    # Act
    result = await controller.create_note_pattern(pattern_data)

    # Assert
    assert result == expected_pattern
    mock_note_pattern_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_rhythm_pattern(controller, mock_rhythm_pattern_repository):
    """Test getting a rhythm pattern by ID."""
    # Arrange
    pattern_id = "test_id"
    expected_pattern = RhythmPattern(
        name="Test Rhythm",
        description="A test rhythm",
        pattern=[RhythmNote(position=0.0, duration=1.0), RhythmNote(position=1.0, duration=1.0)]
    )
    mock_rhythm_pattern_repository.find_one.return_value = expected_pattern

    # Act
    result = await controller.get_rhythm_pattern(pattern_id)

    # Assert
    assert result == expected_pattern
    mock_rhythm_pattern_repository.find_one.assert_called_once_with(pattern_id)


@pytest.mark.asyncio
async def test_get_pattern_by_name_note(controller, mock_note_pattern_repository):
    """Test getting a note pattern by name."""
    # Arrange
    pattern_name = "Test Pattern"
    expected_pattern = NotePattern(
        name=pattern_name,
        description="A test pattern",
        pattern=[Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60), Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)],
        tags=["test", "pattern"]
    )
    mock_note_pattern_repository.find_many.return_value = [expected_pattern]

    # Act
    result = await controller.get_pattern_by_name(pattern_name, "note")

    # Assert
    assert result == expected_pattern
    mock_note_pattern_repository.find_many.assert_called_once_with({"name": pattern_name})


@pytest.mark.asyncio
async def test_get_pattern_by_name_rhythm(controller, mock_rhythm_pattern_repository):
    """Test getting a rhythm pattern by name."""
    # Arrange
    pattern_name = "Test Rhythm"
    expected_pattern = RhythmPattern(
        name=pattern_name,
        description="A test rhythm",
        pattern=[RhythmNote(position=0.0, duration=1.0), RhythmNote(position=1.0, duration=1.0)]
    )
    mock_rhythm_pattern_repository.find_many.return_value = [expected_pattern]

    # Act
    result = await controller.get_pattern_by_name(pattern_name, "rhythm")

    # Assert
    assert result == expected_pattern
    mock_rhythm_pattern_repository.find_many.assert_called_once_with({"name": pattern_name})
