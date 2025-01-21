import pytest
from src.note_gen.fetch_patterns import (
    fetch_chord_progressions,
    fetch_note_patterns,
    fetch_rhythm_patterns,
    fetch_chord_progression_by_id,
    fetch_note_pattern_by_id,
    fetch_rhythm_pattern_by_id,
)
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern
from pymongo.database import Database
from typing import Any

from tests.conftest import MockDatabase

import httpx

# In tests/models/test_fetch_import_patterns.py

@pytest.fixture
async def mock_db_with_data(mock_db: MockDatabase) -> MockDatabase:
    # Sample note patterns to insert into the mock database
    sample_patterns = [
        NotePattern(id='1', name='Simple Arpeggio', description='Basic triad arpeggio', tags=['test'], notes=[{'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100}]),
        NotePattern(id='2', name='Basic Melody', description='Simple melody', tags=['test'], notes=[{'note_name': 'D', 'octave': 4, 'duration': 1.0, 'velocity': 100}]),
    ]
    # Insert sample data into the mock database
    await mock_db.insert_many('note_patterns', [pattern.model_dump() for pattern in sample_patterns])
    return mock_db

@pytest.mark.asyncio
async def test_fetch_note_patterns(mock_db_with_data: MockDatabase) -> None:
    result = await fetch_note_patterns(mock_db_with_data)
    assert len(result) > 0
    for pattern in result:
        # Ensure each pattern contains valid notes
        for note in pattern.notes:
            assert hasattr(note, 'note_name')
            assert hasattr(note, 'octave')
            assert hasattr(note, 'duration')

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(mock_db_with_data: MockDatabase) -> None:
    result = await fetch_rhythm_patterns(mock_db_with_data)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id(mock_db_with_data: MockDatabase) -> None:
    progressions = await fetch_chord_progressions(mock_db_with_data)
    assert len(progressions) > 0
    test_id = progressions[0].id
    result = await fetch_chord_progression_by_id(test_id, mock_db_with_data)
    assert isinstance(result, ChordProgression)
    assert result.id == test_id

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(mock_db_with_data: MockDatabase) -> None:
    patterns = await fetch_note_patterns(mock_db_with_data)
    assert len(patterns) > 0
    test_id = patterns[0].id
    result = await fetch_note_pattern_by_id(test_id, mock_db_with_data)
    assert isinstance(result, NotePattern)
    assert result.id == test_id

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(mock_db_with_data: MockDatabase) -> None:
    patterns = await fetch_rhythm_patterns(mock_db_with_data)
    assert len(patterns) > 0
    test_id = patterns[0].id
    result = await fetch_rhythm_pattern_by_id(test_id, mock_db_with_data)
    assert isinstance(result, RhythmPattern)
    assert result.id == test_id

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_not_found(mock_db_with_data: MockDatabase) -> None:
    result = await fetch_chord_progression_by_id("nonexistent-id", mock_db_with_data)
    assert result is None

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id_not_found(mock_db_with_data: MockDatabase) -> None:
    result = await fetch_note_pattern_by_id("nonexistent-id", mock_db_with_data)
    assert result is None

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id_not_found(mock_db_with_data: MockDatabase) -> None:
    result = await fetch_rhythm_pattern_by_id("nonexistent-id", mock_db_with_data)
    assert result is None
