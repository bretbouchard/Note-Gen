"""Tests for the sequence repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.sequence_repository import SequenceRepository
from note_gen.models.sequence import Sequence
from note_gen.models.note_sequence import NoteSequence
from note_gen.models.note import Note


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    collection = AsyncMock(spec=AsyncIOMotorCollection)
    return collection


@pytest.fixture
def sample_sequence():
    """Create a sample sequence."""
    # Create a sequence directly
    return Sequence(
        id="507f1f77bcf86cd799439011",
        name="Test Sequence",
        metadata={"tags": ["test", "sequence"]}
    )


@pytest.fixture
def sample_note_sequence():
    """Create a sample note sequence."""
    # Create notes
    notes = [
        Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60),
        Note(pitch="E", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=64),
        Note(pitch="G", octave=4, duration=1.0, velocity=64, position=2.0, stored_midi_number=67)
    ]

    # Create a note sequence directly
    return NoteSequence(
        id="507f1f77bcf86cd799439012",
        name="Test Note Sequence",
        notes=notes,
        note_pattern_name="Triad",
        rhythm_pattern_name="Basic 4/4",
        progression_name="I-IV-V",
        metadata={"tags": ["test", "note_sequence"]}
    )


@pytest.fixture
def sample_sequence_dict(sample_sequence):
    """Create a sample sequence dict as it would be stored in MongoDB."""
    seq_dict = sample_sequence.model_dump()
    seq_dict["_id"] = ObjectId(seq_dict["id"])
    del seq_dict["id"]
    return seq_dict


@pytest.fixture
def sample_note_sequence_dict(sample_note_sequence):
    """Create a sample note sequence dict as it would be stored in MongoDB."""
    seq_dict = sample_note_sequence.model_dump()
    seq_dict["_id"] = ObjectId(seq_dict["id"])
    del seq_dict["id"]
    return seq_dict


@pytest.fixture
def repository(mock_collection):
    """Create a repository instance."""
    return SequenceRepository(mock_collection)


@pytest.mark.asyncio
async def test_init(mock_collection):
    """Test repository initialization."""
    repo = SequenceRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_name(repository, mock_collection, sample_sequence_dict, sample_sequence):
    """Test finding a sequence by name."""
    # Setup mock
    mock_collection.find_one.return_value = sample_sequence_dict

    # Call method
    result = await repository.find_by_name("Test Sequence")

    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Sequence"})
    assert isinstance(result, Sequence)
    assert result.id == sample_sequence.id
    assert result.name == sample_sequence.name


@pytest.mark.asyncio
async def test_find_by_name_not_found(repository, mock_collection):
    """Test finding a sequence by name when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None

    # Call method
    result = await repository.find_by_name("Nonexistent")

    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Nonexistent"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_name_exception(repository, mock_collection):
    """Test finding a sequence by name when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Database error")

    # Call method
    result = await repository.find_by_name("Test Sequence")

    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Sequence"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_pattern_name(repository, mock_collection, sample_note_sequence_dict, sample_note_sequence):
    """Test finding sequences by pattern name."""
    # Setup mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_note_sequence_dict]
    mock_collection.find.return_value = mock_cursor

    # Call method
    result = await repository.find_by_pattern_name("Triad")

    # Verify
    mock_collection.find.assert_called_once_with({
        "$or": [
            {"note_pattern_name": "Triad"},
            {"rhythm_pattern_name": "Triad"}
        ]
    })
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert len(result) == 1
    assert isinstance(result[0], NoteSequence)
    assert result[0].id == sample_note_sequence.id
    assert result[0].name == sample_note_sequence.name


@pytest.mark.asyncio
async def test_find_by_progression_name(repository, mock_collection, sample_note_sequence_dict, sample_note_sequence):
    """Test finding sequences by progression name."""
    # Setup mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_note_sequence_dict]
    mock_collection.find.return_value = mock_cursor

    # Call method
    result = await repository.find_by_progression_name("I-IV-V")

    # Verify
    mock_collection.find.assert_called_once_with({"progression_name": "I-IV-V"})
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert len(result) == 1
    assert isinstance(result[0], NoteSequence)
    assert result[0].id == sample_note_sequence.id
    assert result[0].name == sample_note_sequence.name


@pytest.mark.asyncio
async def test_find_by_tags(repository, mock_collection, sample_sequence_dict, sample_sequence):
    """Test finding sequences by tags."""
    # Setup mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_sequence_dict]
    mock_collection.find.return_value = mock_cursor

    # Call method
    result = await repository.find_by_tags(["test"])

    # Verify
    mock_collection.find.assert_called_once_with({"metadata.tags": {"$in": ["test"]}})
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert len(result) == 1
    assert isinstance(result[0], Sequence)
    assert result[0].id == sample_sequence.id
    assert result[0].name == sample_sequence.name


@pytest.mark.asyncio
async def test_convert_to_model_note_sequence(repository, sample_note_sequence_dict):
    """Test converting a dictionary to a NoteSequence model."""
    # Call method
    result = repository._convert_to_model(sample_note_sequence_dict)

    # Verify
    assert isinstance(result, NoteSequence)
    assert result.name == sample_note_sequence_dict["name"]
    assert len(result.notes) == len(sample_note_sequence_dict["notes"])


@pytest.mark.asyncio
async def test_convert_to_model_none(repository):
    """Test converting None to a model."""
    # Call method and verify
    with pytest.raises(ValueError, match="Data cannot be None"):
        repository._convert_to_model(None)
