"""Tests for the import/export controller."""
import pytest
import json
import io
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile

from note_gen.controllers.import_export_controller import ImportExportController
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.note_sequence import NoteSequence
from note_gen.models.note import Note
from note_gen.core.enums import ScaleType, PatternDirection


@pytest.fixture
def mock_repositories():
    """Create mock repositories."""
    chord_progression_repository = AsyncMock()
    note_pattern_repository = AsyncMock()
    rhythm_pattern_repository = AsyncMock()
    sequence_repository = AsyncMock()
    
    return {
        "chord_progression_repository": chord_progression_repository,
        "note_pattern_repository": note_pattern_repository,
        "rhythm_pattern_repository": rhythm_pattern_repository,
        "sequence_repository": sequence_repository
    }


@pytest.fixture
def controller(mock_repositories):
    """Create an import/export controller instance."""
    return ImportExportController(
        mock_repositories["chord_progression_repository"],
        mock_repositories["note_pattern_repository"],
        mock_repositories["rhythm_pattern_repository"],
        mock_repositories["sequence_repository"]
    )


@pytest.fixture
def sample_chord_progressions():
    """Create sample chord progressions."""
    return [
        ChordProgression(
            id="507f1f77bcf86cd799439011",
            name="Test Progression 1",
            key="C",
            scale_type="MAJOR",
            chords=[]
        ),
        ChordProgression(
            id="507f1f77bcf86cd799439012",
            name="Test Progression 2",
            key="G",
            scale_type="MINOR",
            chords=[]
        )
    ]


@pytest.fixture
def sample_note_patterns():
    """Create sample note patterns."""
    return [
        NotePattern(
            id="507f1f77bcf86cd799439013",
            name="Test Pattern 1",
            complexity=3.0,
            tags=["test", "pattern"],
            data=NotePatternData(
                notes=[Note(pitch=60, duration=1.0, velocity=100)],
                scale_type=ScaleType.MAJOR,
                direction=PatternDirection.ASCENDING
            )
        ),
        NotePattern(
            id="507f1f77bcf86cd799439014",
            name="Test Pattern 2",
            complexity=4.0,
            tags=["test", "pattern"],
            data=NotePatternData(
                notes=[Note(pitch=62, duration=1.0, velocity=100)],
                scale_type=ScaleType.MINOR,
                direction=PatternDirection.DESCENDING
            )
        )
    ]


@pytest.fixture
def sample_rhythm_patterns():
    """Create sample rhythm patterns."""
    return [
        RhythmPattern(
            id="507f1f77bcf86cd799439015",
            name="Test Rhythm 1",
            time_signature=[4, 4],
            notes=[RhythmNote(position=0, duration=1.0, velocity=100)]
        ),
        RhythmPattern(
            id="507f1f77bcf86cd799439016",
            name="Test Rhythm 2",
            time_signature=[3, 4],
            notes=[RhythmNote(position=0, duration=0.5, velocity=100)]
        )
    ]


@pytest.mark.asyncio
async def test_create(mock_repositories):
    """Test the create factory method."""
    controller = await ImportExportController.create(
        mock_repositories["chord_progression_repository"],
        mock_repositories["note_pattern_repository"],
        mock_repositories["rhythm_pattern_repository"],
        mock_repositories["sequence_repository"]
    )
    
    assert isinstance(controller, ImportExportController)
    assert controller.chord_progression_repository is mock_repositories["chord_progression_repository"]
    assert controller.note_pattern_repository is mock_repositories["note_pattern_repository"]
    assert controller.rhythm_pattern_repository is mock_repositories["rhythm_pattern_repository"]
    assert controller.sequence_repository is mock_repositories["sequence_repository"]


@pytest.mark.asyncio
async def test_export_chord_progressions_json(controller, sample_chord_progressions, mock_repositories):
    """Test exporting chord progressions to JSON."""
    # Setup mock
    mock_repositories["chord_progression_repository"].find_all.return_value = sample_chord_progressions
    
    # Call method
    result = await controller.export_chord_progressions(format="json")
    
    # Verify
    mock_repositories["chord_progression_repository"].find_all.assert_called_once()
    assert isinstance(result, str)
    
    # Parse the JSON and verify content
    data = json.loads(result)
    assert len(data) == 2
    assert data[0]["name"] == "Test Progression 1"
    assert data[1]["name"] == "Test Progression 2"


@pytest.mark.asyncio
async def test_export_chord_progressions_csv(controller, sample_chord_progressions, mock_repositories):
    """Test exporting chord progressions to CSV."""
    # Setup mock
    mock_repositories["chord_progression_repository"].find_all.return_value = sample_chord_progressions
    
    # Call method
    result = await controller.export_chord_progressions(format="csv")
    
    # Verify
    mock_repositories["chord_progression_repository"].find_all.assert_called_once()
    assert isinstance(result, bytes)
    
    # Check CSV content
    csv_content = result.decode()
    assert "name,key,scale_type" in csv_content
    assert "Test Progression 1,C,MAJOR" in csv_content
    assert "Test Progression 2,G,MINOR" in csv_content


@pytest.mark.asyncio
async def test_export_note_patterns_json(controller, sample_note_patterns, mock_repositories):
    """Test exporting note patterns to JSON."""
    # Setup mock
    mock_repositories["note_pattern_repository"].find_all.return_value = sample_note_patterns
    
    # Call method
    result = await controller.export_note_patterns(format="json")
    
    # Verify
    mock_repositories["note_pattern_repository"].find_all.assert_called_once()
    assert isinstance(result, str)
    
    # Parse the JSON and verify content
    data = json.loads(result)
    assert len(data) == 2
    assert data[0]["name"] == "Test Pattern 1"
    assert data[1]["name"] == "Test Pattern 2"


@pytest.mark.asyncio
async def test_export_rhythm_patterns_json(controller, sample_rhythm_patterns, mock_repositories):
    """Test exporting rhythm patterns to JSON."""
    # Setup mock
    mock_repositories["rhythm_pattern_repository"].find_all.return_value = sample_rhythm_patterns
    
    # Call method
    result = await controller.export_rhythm_patterns(format="json")
    
    # Verify
    mock_repositories["rhythm_pattern_repository"].find_all.assert_called_once()
    assert isinstance(result, str)
    
    # Parse the JSON and verify content
    data = json.loads(result)
    assert len(data) == 2
    assert data[0]["name"] == "Test Rhythm 1"
    assert data[1]["name"] == "Test Rhythm 2"


@pytest.mark.asyncio
async def test_import_chord_progressions_json(controller, mock_repositories):
    """Test importing chord progressions from JSON."""
    # Create test data
    test_data = [
        {
            "name": "Imported Progression 1",
            "key": "D",
            "scale_type": "MAJOR",
            "chords": []
        },
        {
            "name": "Imported Progression 2",
            "key": "A",
            "scale_type": "MINOR",
            "chords": []
        }
    ]
    
    # Create a mock file
    json_content = json.dumps(test_data)
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.json"
    mock_file.read = AsyncMock(return_value=json_content.encode())
    
    # Setup repository mock
    mock_repositories["chord_progression_repository"].save = AsyncMock(return_value="123")
    
    # Call method
    result = await controller.import_chord_progressions(mock_file)
    
    # Verify
    assert result == 2
    assert mock_repositories["chord_progression_repository"].save.call_count == 2


@pytest.mark.asyncio
async def test_import_note_patterns_json(controller, mock_repositories):
    """Test importing note patterns from JSON."""
    # Create test data
    test_data = [
        {
            "name": "Imported Pattern 1",
            "complexity": 2.0,
            "tags": ["imported"],
            "data": {
                "notes": [{"pitch": 64, "duration": 1.0, "velocity": 100}],
                "scale_type": "MAJOR",
                "direction": "ASCENDING"
            }
        }
    ]
    
    # Create a mock file
    json_content = json.dumps(test_data)
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.json"
    mock_file.read = AsyncMock(return_value=json_content.encode())
    
    # Setup repository mock
    mock_repositories["note_pattern_repository"].save = AsyncMock(return_value="123")
    
    # Call method
    result = await controller.import_note_patterns(mock_file)
    
    # Verify
    assert result == 1
    mock_repositories["note_pattern_repository"].save.assert_called_once()


@pytest.mark.asyncio
async def test_import_unsupported_format(controller):
    """Test importing from an unsupported format."""
    # Create a mock file
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.txt"
    mock_file.read = AsyncMock(return_value=b"test content")
    
    # Call method and verify exception
    with pytest.raises(ValueError) as excinfo:
        await controller.import_chord_progressions(mock_file)
    
    assert "Unsupported file format" in str(excinfo.value)
