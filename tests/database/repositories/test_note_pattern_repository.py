"""Tests for the note pattern repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.note_pattern_repository import NotePatternRepository
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.note import Note
from note_gen.core.enums import ScaleType, PatternDirection


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    collection = AsyncMock(spec=AsyncIOMotorCollection)
    return collection


@pytest.fixture
def sample_pattern():
    """Create a sample note pattern."""
    # Create notes
    notes = [
        Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60),
        Note(pitch="E", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=64),
        Note(pitch="G", octave=4, duration=1.0, velocity=64, position=2.0, stored_midi_number=67)
    ]

    # Create pattern data
    pattern_data = NotePatternData(
        intervals=[0, 4, 7],
        direction=PatternDirection.UP,
        scale_type=ScaleType.MAJOR
    )

    # Create a mock pattern directly
    pattern = NotePattern(
        id="507f1f77bcf86cd799439011",
        name="Test Pattern",
        pattern=notes,
        data=pattern_data,
        tags=["test", "triad"]
    )

    # Return the pattern
    return pattern


@pytest.fixture
def sample_pattern_dict(sample_pattern):
    """Create a sample pattern dict as it would be stored in MongoDB."""
    pattern_dict = sample_pattern.model_dump()
    pattern_dict["_id"] = ObjectId(pattern_dict["id"])
    del pattern_dict["id"]
    return pattern_dict


@pytest.fixture
def repository(mock_collection):
    """Create a repository instance."""
    return NotePatternRepository(mock_collection)


@pytest.mark.asyncio
async def test_init(mock_collection):
    """Test repository initialization."""
    repo = NotePatternRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_name(repository, mock_collection, sample_pattern_dict, sample_pattern):
    """Test finding a note pattern by name."""
    # Create a mock for the find_one method
    async def mock_find_one(*args, **kwargs):
        return sample_pattern_dict

    # Replace the find_one method with our mock
    mock_collection.find_one = mock_find_one

    # Call method
    result = await repository.find_by_name("Test Pattern")

    # Verify
    assert isinstance(result, NotePattern)
    assert result.id == sample_pattern.id
    assert result.name == sample_pattern.name


@pytest.mark.asyncio
async def test_find_by_name_not_found(repository, mock_collection):
    """Test finding a note pattern by name when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None

    # Call method
    result = await repository.find_by_name("Nonexistent")

    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Nonexistent"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_name_exception(repository, mock_collection):
    """Test finding a note pattern by name when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Database error")

    # Call method
    result = await repository.find_by_name("Test Pattern")

    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Pattern"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_scale_type(repository, mock_collection, sample_pattern_dict, sample_pattern):
    """Test finding note patterns by scale type."""
    # Create a mock cursor with an async to_list method
    class MockCursor:
        async def to_list(self, length=None):
            return [sample_pattern_dict]

    # Create a mock for the find method
    async def mock_find(*args, **kwargs):
        return MockCursor()

    # Replace the find method with our mock
    mock_collection.find = mock_find

    # Call method
    result = await repository.find_by_scale_type(ScaleType.MAJOR)

    # Verify
    assert len(result) == 1
    assert isinstance(result[0], NotePattern)
    assert result[0].id == sample_pattern.id
    assert result[0].name == sample_pattern.name


@pytest.mark.asyncio
async def test_find_by_complexity_range(repository, mock_collection, sample_pattern_dict, sample_pattern):
    """Test finding note patterns by complexity range."""
    # Create a mock cursor with an async to_list method
    class MockCursor:
        async def to_list(self, length=None):
            return [sample_pattern_dict]

    # Create a mock for the find method
    async def mock_find(*args, **kwargs):
        return MockCursor()

    # Replace the find method with our mock
    mock_collection.find = mock_find

    # Call method
    result = await repository.find_by_complexity_range(1.0, 5.0)

    # Verify
    assert len(result) == 1
    assert isinstance(result[0], NotePattern)
    assert result[0].id == sample_pattern.id
    assert result[0].name == sample_pattern.name


@pytest.mark.asyncio
async def test_find_by_tags(repository, mock_collection, sample_pattern_dict, sample_pattern):
    """Test finding note patterns by tags."""
    # Create a mock cursor with an async to_list method
    class MockCursor:
        async def to_list(self, length=None):
            return [sample_pattern_dict]

    # Create a mock for the find method
    async def mock_find(*args, **kwargs):
        return MockCursor()

    # Replace the find method with our mock
    mock_collection.find = mock_find

    # Call method
    result = await repository.find_by_tags(["triad"])

    # Verify
    assert len(result) == 1
    assert isinstance(result[0], NotePattern)
    assert result[0].id == sample_pattern.id
    assert result[0].name == sample_pattern.name
