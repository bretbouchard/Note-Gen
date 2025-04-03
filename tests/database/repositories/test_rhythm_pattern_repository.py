"""Tests for the rhythm pattern repository."""
import pytest
from unittest.mock import AsyncMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from note_gen.database.repositories.rhythm_pattern_repository import RhythmPatternRepository
from note_gen.models.patterns import RhythmPattern, RhythmNote


@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    collection = AsyncMock(spec=AsyncIOMotorCollection)
    return collection


@pytest.fixture
def sample_pattern():
    """Create a sample rhythm pattern."""
    # Create the pattern with dictionaries for rhythm notes
    # Create rhythm notes
    rhythm_notes = [
        RhythmNote(position=0.0, duration=1.0, velocity=64),
        RhythmNote(position=1.0, duration=0.5, velocity=64),
        RhythmNote(position=1.5, duration=0.5, velocity=64),
        RhythmNote(position=2.0, duration=1.0, velocity=64),
        RhythmNote(position=3.0, duration=1.0, velocity=64)
    ]

    # Create a rhythm pattern directly
    pattern = RhythmPattern(
        id="507f1f77bcf86cd799439011",
        name="Test Rhythm",
        pattern=rhythm_notes,
        time_signature=(4, 4),
        style="basic",
        total_duration=4.0
    )

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
    return RhythmPatternRepository(mock_collection)


@pytest.mark.asyncio
async def test_init(mock_collection):
    """Test repository initialization."""
    repo = RhythmPatternRepository(mock_collection)
    assert repo.collection is mock_collection


@pytest.mark.asyncio
async def test_find_by_name(repository, mock_collection, sample_pattern_dict, sample_pattern):
    """Test finding a rhythm pattern by name."""
    # Setup mock
    mock_collection.find_one.return_value = sample_pattern_dict

    # Call method
    result = await repository.find_by_name("Test Rhythm")

    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Rhythm"})
    assert isinstance(result, RhythmPattern)
    assert result.id == sample_pattern.id
    assert result.name == sample_pattern.name


@pytest.mark.asyncio
async def test_find_by_name_not_found(repository, mock_collection):
    """Test finding a rhythm pattern by name when not found."""
    # Setup mock
    mock_collection.find_one.return_value = None

    # Call method
    result = await repository.find_by_name("Nonexistent")

    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Nonexistent"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_name_exception(repository, mock_collection):
    """Test finding a rhythm pattern by name when an exception occurs."""
    # Setup mock
    mock_collection.find_one.side_effect = Exception("Database error")

    # Call method
    result = await repository.find_by_name("Test Rhythm")

    # Verify
    mock_collection.find_one.assert_called_once_with({"name": "Test Rhythm"})
    assert result is None


@pytest.mark.asyncio
async def test_find_by_time_signature(repository, mock_collection, sample_pattern_dict, sample_pattern):
    """Test finding rhythm patterns by time signature."""
    # Setup mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_pattern_dict]
    mock_collection.find.return_value = mock_cursor

    # Call method
    result = await repository.find_by_time_signature((4, 4))

    # Verify
    mock_collection.find.assert_called_once_with({"time_signature": [4, 4]})
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert len(result) == 1
    assert isinstance(result[0], RhythmPattern)
    assert result[0].id == sample_pattern.id
    assert result[0].name == sample_pattern.name


@pytest.mark.asyncio
async def test_find_by_style(repository, mock_collection, sample_pattern_dict, sample_pattern):
    """Test finding rhythm patterns by style."""
    # Setup mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_pattern_dict]
    mock_collection.find.return_value = mock_cursor

    # Call method
    result = await repository.find_by_style("basic")

    # Verify
    mock_collection.find.assert_called_once_with({"style": "basic"})
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert len(result) == 1
    assert isinstance(result[0], RhythmPattern)
    assert result[0].id == sample_pattern.id
    assert result[0].name == sample_pattern.name


@pytest.mark.asyncio
async def test_find_by_tags(repository, mock_collection, sample_pattern_dict, sample_pattern):
    """Test finding rhythm patterns by tags."""
    # Setup mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_pattern_dict]
    mock_collection.find.return_value = mock_cursor

    # Call method
    result = await repository.find_by_tags(["basic"])

    # Verify
    mock_collection.find.assert_called_once_with({"tags": {"$in": ["basic"]}})
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert len(result) == 1
    assert isinstance(result[0], RhythmPattern)
    assert result[0].id == sample_pattern.id
    assert result[0].name == sample_pattern.name
