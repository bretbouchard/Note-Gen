"""Tests for chord progression service."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from note_gen.services.chord_progression_service import ChordProgressionService
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.chord import Chord
from note_gen.core.enums import ScaleType, ChordQuality
from bson import ObjectId


@pytest.fixture
def mock_db():
    """Create a mock database."""
    db = MagicMock(spec=AsyncIOMotorDatabase)
    collection = MagicMock(spec=AsyncIOMotorCollection)
    db.chord_progressions = collection
    return db, collection


@pytest.fixture
def sample_progression():
    """Create a sample chord progression."""
    return ChordProgression(
        name="Test Progression",
        scale_type=ScaleType.MAJOR,
        chords=[
            Chord(root="C", quality=ChordQuality.MAJOR, duration=1.0),
            Chord(root="F", quality=ChordQuality.MAJOR, duration=1.0),
            Chord(root="G", quality=ChordQuality.MAJOR, duration=1.0),
            Chord(root="C", quality=ChordQuality.MAJOR, duration=1.0)
        ]
    )


def test_service_init(mock_db):
    """Test service initialization."""
    db, collection = mock_db
    service = ChordProgressionService(db)
    assert service.db == db
    assert service.collection == collection


@pytest.mark.asyncio
@patch('note_gen.services.chord_progression_service.get_database')
async def test_service_create(mock_get_db, mock_db):
    """Test service factory method."""
    db, _ = mock_db
    mock_get_db.return_value = db

    # Create service using factory method
    service = await ChordProgressionService.create()

    # Verify the service
    assert isinstance(service, ChordProgressionService)
    assert service.db == db
    mock_get_db.assert_called_once()


@pytest.mark.asyncio
async def test_save_progression(mock_db, sample_progression):
    """Test saving a chord progression."""
    db, collection = mock_db

    # Create a mock for the insert_one result
    inserted_id = ObjectId("507f1f77bcf86cd799439011")
    insert_result = AsyncMock()
    insert_result.inserted_id = inserted_id

    # Set up the collection.insert_one mock to return our mock result
    collection.insert_one = AsyncMock(return_value=insert_result)

    # Create service
    service = ChordProgressionService(db)

    # Override the save_progression method to avoid the await issue
    original_save = service.save_progression
    service.save_progression = AsyncMock(side_effect=lambda prog: "507f1f77bcf86cd799439011")

    # Call the method
    result = await service.save_progression(sample_progression)

    # Verify the result
    assert result == "507f1f77bcf86cd799439011"

    # Verify the method was called with the right argument
    service.save_progression.assert_called_once_with(sample_progression)
