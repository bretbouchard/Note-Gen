"""Tests for NotePatternRepository."""
import pytest
import pytest_asyncio
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from note_gen.database.repositories.note_pattern import NotePatternRepository
from note_gen.models.patterns import NotePattern
from note_gen.models.note import Note


@pytest_asyncio.fixture
async def mock_database():
    """Create a mock MongoDB database."""
    database = MagicMock(spec=AsyncIOMotorDatabase)

    # Mock collection access
    mock_collection = MagicMock(spec=AsyncIOMotorCollection)
    database.__getitem__.return_value = mock_collection

    # Mock find method
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock()
    mock_collection.find = MagicMock(return_value=mock_cursor)

    return database, mock_collection


@pytest.fixture
def test_repository(mock_database):
    """Create a test repository."""
    database, _ = mock_database
    repo = NotePatternRepository(
        database=database,
        collection_name="note_patterns"
    )

    # Mock the _convert_to_model method to return a NotePattern directly
    original_convert = repo._convert_to_model

    def mock_convert(doc):
        if 'name' in doc:
            # Create a simple NotePattern with the same name
            note = Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60)
            return NotePattern(
                name=doc['name'],
                complexity=doc.get('complexity', 0.5),
                pattern=[note],
                data=doc.get('data', {"scale_type": "MAJOR"}),
                validation_level=doc.get('validation_level', None),
                skip_validation=True
            )
        return original_convert(doc)

    repo._convert_to_model = mock_convert
    return repo


@pytest.mark.asyncio
async def test_init(mock_database):
    """Test repository initialization."""
    database, _ = mock_database
    repo = NotePatternRepository(
        database=database,
        collection_name="note_patterns"
    )

    assert repo.database == database
    assert repo.collection == database["note_patterns"]
    assert repo.model_class == NotePattern


@pytest.mark.asyncio
async def test_find_by_complexity_range(test_repository, mock_database):
    """Test finding note patterns by complexity range."""
    _, mock_collection = mock_database

    # Create Note objects for the pattern
    note1 = Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60)
    note2 = Note(pitch="D", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=62)

    # Create a NotePattern object
    pattern1 = NotePattern(
        name="Simple Pattern",
        complexity=0.3,
        pattern=[note1],
        data={"scale_type": "MAJOR"},
        skip_validation=True
    )

    pattern2 = NotePattern(
        name="Medium Pattern",
        complexity=0.5,
        pattern=[note2],
        data={"scale_type": "MAJOR"},
        skip_validation=True
    )

    # Mock the cursor.to_list method to return documents
    mock_cursor = mock_collection.find.return_value
    mock_cursor.to_list.return_value = [
        pattern1.model_dump(),
        pattern2.model_dump()
    ]

    # Call the method
    results = await test_repository.find_by_complexity_range(0.2, 0.6)

    # Verify the results
    assert len(results) == 2
    assert all(isinstance(result, NotePattern) for result in results)
    assert results[0].name == "Simple Pattern"
    assert results[0].complexity == 0.3
    assert results[1].name == "Medium Pattern"
    assert results[1].complexity == 0.5

    # Verify the find method was called with the correct arguments
    mock_collection.find.assert_called_once_with({
        "complexity": {
            "$gte": 0.2,
            "$lte": 0.6
        }
    })
    mock_cursor.to_list.assert_called_once_with(None)


@pytest.mark.asyncio
async def test_find_by_scale_type(test_repository, mock_database):
    """Test finding note patterns by scale type."""
    _, mock_collection = mock_database

    # Create Note objects for the pattern
    note1 = Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60)
    note2 = Note(pitch="D", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=62)

    # Create a NotePattern object
    pattern1 = NotePattern(
        name="Major Pattern 1",
        complexity=0.3,
        pattern=[note1],
        data={"scale_type": "MAJOR"},
        skip_validation=True
    )

    pattern2 = NotePattern(
        name="Major Pattern 2",
        complexity=0.5,
        pattern=[note2],
        data={"scale_type": "MAJOR"},
        skip_validation=True
    )

    # Mock the cursor.to_list method to return documents
    mock_cursor = mock_collection.find.return_value
    mock_cursor.to_list.return_value = [
        pattern1.model_dump(),
        pattern2.model_dump()
    ]

    # Call the method
    results = await test_repository.find_by_scale_type("MAJOR")

    # Verify the results
    assert len(results) == 2
    assert all(isinstance(result, NotePattern) for result in results)
    assert results[0].name == "Major Pattern 1"
    assert results[0].data.scale_type == "MAJOR"
    assert results[1].name == "Major Pattern 2"
    assert results[1].data.scale_type == "MAJOR"

    # Verify the find method was called with the correct arguments
    mock_collection.find.assert_called_once_with({"data.scale_type": "MAJOR"})
    mock_cursor.to_list.assert_called_once_with(None)


@pytest.mark.asyncio
async def test_find_by_validation_level(test_repository, mock_database):
    """Test finding note patterns by validation level."""
    _, mock_collection = mock_database

    # Create Note objects for the pattern
    note1 = Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60)
    note2 = Note(pitch="D", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=62)

    # Create a NotePattern object
    pattern1 = NotePattern(
        name="Strict Pattern 1",
        complexity=0.3,
        pattern=[note1],
        data={"scale_type": "MAJOR"},
        validation_level="STRICT",
        skip_validation=True
    )

    pattern2 = NotePattern(
        name="Strict Pattern 2",
        complexity=0.5,
        pattern=[note2],
        data={"scale_type": "MINOR"},
        validation_level="STRICT",
        skip_validation=True
    )

    # Mock the cursor.to_list method to return documents
    mock_cursor = mock_collection.find.return_value
    mock_cursor.to_list.return_value = [
        pattern1.model_dump(),
        pattern2.model_dump()
    ]

    # Call the method
    results = await test_repository.find_by_validation_level("STRICT")

    # Verify the results
    assert len(results) == 2
    assert all(isinstance(result, NotePattern) for result in results)
    assert results[0].name == "Strict Pattern 1"
    assert results[0].validation_level == "STRICT"
    assert results[1].name == "Strict Pattern 2"
    assert results[1].validation_level == "STRICT"

    # Verify the find method was called with the correct arguments
    mock_collection.find.assert_called_once_with({"validation_level": "STRICT"})
    mock_cursor.to_list.assert_called_once_with(None)
