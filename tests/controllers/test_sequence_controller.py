"""Tests for the sequence controller."""
import pytest
from unittest.mock import AsyncMock

from note_gen.controllers.sequence_controller import SequenceController
from note_gen.models.sequence import Sequence
from note_gen.models.note_sequence import NoteSequence
from note_gen.models.note import Note
from note_gen.core.enums import ChordQuality, ScaleType


@pytest.fixture
def mock_sequence_repository():
    """Create a mock sequence repository for testing."""
    repository = AsyncMock()
    repository.find_one = AsyncMock()
    repository.find_many = AsyncMock(return_value=[])
    repository.create = AsyncMock()
    repository.find_many = AsyncMock(return_value=[])
    return repository


@pytest.fixture
def mock_pattern_controller():
    """Create a mock pattern controller for testing."""
    controller = AsyncMock()
    controller.get_pattern_by_name = AsyncMock()
    return controller


@pytest.fixture
def mock_chord_progression_repository():
    """Create a mock chord progression repository for testing."""
    repository = AsyncMock()
    repository.find_many = AsyncMock(return_value=[])
    return repository


@pytest.fixture
def controller(mock_sequence_repository, mock_pattern_controller, mock_chord_progression_repository):
    """Create a controller instance for testing."""
    return SequenceController(
        mock_sequence_repository,
        mock_pattern_controller,
        mock_chord_progression_repository
    )


@pytest.mark.asyncio
async def test_get_sequence(controller, mock_sequence_repository):
    """Test getting a sequence by ID."""
    # Arrange
    sequence_id = "test_id"
    expected_sequence = Sequence(
        name="Test Sequence",
        metadata={"key": "value"}
    )
    mock_sequence_repository.find_one.return_value = expected_sequence

    # Act
    result = await controller.get_sequence(sequence_id)

    # Assert
    assert result == expected_sequence
    mock_sequence_repository.find_one.assert_called_once_with(sequence_id)


@pytest.mark.asyncio
async def test_get_all_sequences(controller, mock_sequence_repository):
    """Test getting all sequences."""
    # Arrange
    expected_sequences = [
        Sequence(
            name="Test Sequence 1",
            metadata={"key1": "value1"}
        ),
        Sequence(
            name="Test Sequence 2",
            metadata={"key2": "value2"}
        )
    ]
    mock_sequence_repository.find_many.return_value = expected_sequences

    # Act
    result = await controller.get_all_sequences()

    # Assert
    assert result == expected_sequences
    mock_sequence_repository.find_many.assert_called_once()


@pytest.mark.asyncio
async def test_create_sequence(controller, mock_sequence_repository):
    """Test creating a sequence."""
    # Arrange
    sequence_data = {
        "name": "New Sequence",
        "metadata": {"key": "value"}
    }
    expected_sequence = Sequence(**sequence_data)
    mock_sequence_repository.create.return_value = expected_sequence

    # Act
    result = await controller.create_sequence(sequence_data)

    # Assert
    assert result == expected_sequence
    mock_sequence_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_sequence(
    controller, mock_sequence_repository, mock_pattern_controller, mock_chord_progression_repository
):
    """Test generating a sequence."""
    # Arrange
    progression_name = "Test Progression"
    pattern_name = "Test Pattern"
    rhythm_pattern_name = "Test Rhythm"

    # Mock the chord progression
    from note_gen.models.chord_progression import ChordProgression
    from note_gen.models.chord import Chord

    progression = ChordProgression(
        name=progression_name,
        key="C",
        scale_type=ScaleType.MAJOR,
        chords=[Chord(root="C", quality=ChordQuality.MAJOR, duration=1)]
    )
    mock_chord_progression_repository.find_many.return_value = [progression]

    # Mock the patterns
    from note_gen.models.patterns import NotePattern, RhythmPattern, RhythmNote

    note_pattern = NotePattern(
        name=pattern_name,
        description="A test pattern",
        pattern=[Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60), Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)]
    )
    mock_pattern_controller.get_pattern_by_name.side_effect = lambda name, type: (
        note_pattern if name == pattern_name and type == "note" else None
    )

    rhythm_pattern = RhythmPattern(
        name=rhythm_pattern_name,
        description="A test rhythm",
        pattern=[RhythmNote(position=0.0, duration=1.0), RhythmNote(position=1.0, duration=1.0)]
    )
    mock_pattern_controller.get_pattern_by_name.side_effect = lambda name, type: (
        note_pattern if name == pattern_name and type == "note" else
        rhythm_pattern if name == rhythm_pattern_name and type == "rhythm" else
        None
    )

    # Mock the sequence creation
    expected_sequence = NoteSequence(
        name=f"Generated sequence from {progression_name}",
        notes=[],
        metadata={
            "progression_name": progression_name,
            "pattern_name": pattern_name,
            "rhythm_pattern_name": rhythm_pattern_name
        }
    )
    mock_sequence_repository.create.return_value = expected_sequence

    # Act
    result = await controller.generate_sequence(progression_name, pattern_name, rhythm_pattern_name)

    # Assert
    assert result == expected_sequence
    mock_chord_progression_repository.find_many.assert_called_once_with({"name": progression_name})
    mock_sequence_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_sequence_by_name(controller, mock_sequence_repository):
    """Test getting a sequence by name."""
    # Arrange
    sequence_name = "Test Sequence"
    expected_sequence = Sequence(
        name=sequence_name,
        metadata={"key": "value"}
    )
    mock_sequence_repository.find_many.return_value = [expected_sequence]

    # Act
    result = await controller.get_sequence_by_name(sequence_name)

    # Assert
    assert result == expected_sequence
    mock_sequence_repository.find_many.assert_called_once_with({"name": sequence_name})
