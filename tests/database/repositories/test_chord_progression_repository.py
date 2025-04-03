"""Tests for ChordProgressionRepository."""
import pytest
import pytest_asyncio
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from note_gen.database.repositories.chord_progression import ChordProgressionRepository
from note_gen.models.chord_progression import ChordProgression


@pytest_asyncio.fixture
async def mock_database():
    """Create a mock MongoDB database."""
    database = MagicMock(spec=AsyncIOMotorDatabase)

    # Mock collection access
    mock_collection = MagicMock(spec=AsyncIOMotorCollection)
    database.__getitem__.return_value = mock_collection

    # Mock find_one method
    mock_collection.find_one = AsyncMock()

    # Mock find method
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock()
    mock_collection.find = MagicMock(return_value=mock_cursor)

    return database, mock_collection


@pytest.fixture
def test_repository(mock_database):
    """Create a test repository."""
    database, _ = mock_database
    repo = ChordProgressionRepository(
        database=database,
        collection_name="chord_progressions"
    )
    return repo


@pytest.mark.asyncio
async def test_init(mock_database):
    """Test repository initialization."""
    database, _ = mock_database
    repo = ChordProgressionRepository(
        database=database,
        collection_name="chord_progressions"
    )

    assert repo.database == database
    assert repo.collection == database["chord_progressions"]
    assert repo.model_class == ChordProgression


@pytest.mark.asyncio
async def test_find_by_name(test_repository, mock_database):
    """Test finding chord progression by name."""
    _, mock_collection = mock_database

    # Mock the find_one method to return a document
    mock_collection.find_one.return_value = {
        "name": "I-IV-V",
        "scale_type": "MAJOR",
        "chords": [
            {"root": "C", "quality": "MAJOR", "duration": 1.0},
            {"root": "F", "quality": "MAJOR", "duration": 1.0},
            {"root": "G", "quality": "MAJOR", "duration": 1.0}
        ]
    }

    # Call the method
    result = await test_repository.find_by_name("I-IV-V")

    # Verify the result
    assert isinstance(result, ChordProgression)
    assert result.name == "I-IV-V"
    assert result.scale_type == "MAJOR"
    assert len(result.chords) == 3

    # Verify the find_one method was called with the correct arguments
    mock_collection.find_one.assert_called_once_with({"name": "I-IV-V"})

    # Test with non-existent name
    mock_collection.find_one.reset_mock()
    mock_collection.find_one.return_value = None

    result = await test_repository.find_by_name("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_find_by_scale_type(test_repository, mock_database):
    """Test finding chord progressions by scale type."""
    _, mock_collection = mock_database

    # Mock the cursor.to_list method to return documents
    mock_cursor = mock_collection.find.return_value
    mock_cursor.to_list.return_value = [
        {
            "name": "I-IV-V",
            "scale_type": "MAJOR",
            "chords": [
                {"root": "C", "quality": "MAJOR", "duration": 1.0},
                {"root": "F", "quality": "MAJOR", "duration": 1.0},
                {"root": "G", "quality": "MAJOR", "duration": 1.0}
            ]
        },
        {
            "name": "I-V-vi-IV",
            "scale_type": "MAJOR",
            "chords": [
                {"root": "C", "quality": "MAJOR", "duration": 1.0},
                {"root": "G", "quality": "MAJOR", "duration": 1.0},
                {"root": "A", "quality": "MINOR", "duration": 1.0},
                {"root": "F", "quality": "MAJOR", "duration": 1.0}
            ]
        }
    ]

    # Call the method
    results = await test_repository.find_by_scale_type("MAJOR")

    # Verify the results
    assert len(results) == 2
    assert all(isinstance(result, ChordProgression) for result in results)
    assert results[0].name == "I-IV-V"
    assert results[0].scale_type == "MAJOR"
    assert results[1].name == "I-V-vi-IV"
    assert results[1].scale_type == "MAJOR"

    # Verify the find method was called with the correct arguments
    mock_collection.find.assert_called_once_with({"scale_type": "MAJOR"})
    mock_cursor.to_list.assert_called_once_with(None)
