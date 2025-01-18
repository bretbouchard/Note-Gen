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

import httpx

# In tests/models/test_fetch_import_patterns.py

@pytest.mark.asyncio
async def test_fetch_note_patterns(mock_db: Database[Any]) -> None:
    async with httpx.AsyncClient() as client:
        result = await fetch_note_patterns(mock_db)
        assert len(result) > 0
        for pattern in result:
            # Ensure each pattern contains valid notes
            for note in pattern.notes:
                assert hasattr(note, "note_name")
                assert hasattr(note, "octave")
                assert hasattr(note, "duration")

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(mock_db: Database[Any]) -> None:
    async with httpx.AsyncClient() as client:
        result = await fetch_rhythm_patterns(mock_db)
        assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id(mock_db: Database[Any]) -> None:
    # Get first chord progression's ID
    progressions = await fetch_chord_progressions(mock_db)
    assert len(progressions) > 0
    test_id = progressions[0].id
    
    # Using mock database
    async with httpx.AsyncClient() as client:
        result = await fetch_chord_progression_by_id(test_id, mock_db)
        assert isinstance(result, ChordProgression)
        assert result.id == test_id

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(mock_db: Database[Any]) -> None:
    # Get first note pattern's ID
    patterns = await fetch_note_patterns(mock_db)
    assert len(patterns) > 0
    test_id = patterns[0].id
    
    # Using mock database
    async with httpx.AsyncClient() as client:
        result = await fetch_note_pattern_by_id(test_id, mock_db)
        assert isinstance(result, NotePattern)
        assert result.id == test_id

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(mock_db: Database[Any]) -> None:
    # Get first rhythm pattern's ID
    patterns = await fetch_rhythm_patterns(mock_db)
    assert len(patterns) > 0
    test_id = patterns[0].id
    
    # Using mock database
    async with httpx.AsyncClient() as client:
        result = await fetch_rhythm_pattern_by_id(test_id, mock_db)
        assert isinstance(result, RhythmPattern)
        assert result.id == test_id

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_not_found(mock_db: Database[Any]) -> None:
    async with httpx.AsyncClient() as client:
        result = await fetch_chord_progression_by_id("nonexistent-id", mock_db)
        assert result is None

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id_not_found(mock_db: Database[Any]) -> None:
    async with httpx.AsyncClient() as client:
        result = await fetch_note_pattern_by_id("nonexistent-id", mock_db)
        assert result is None

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id_not_found(mock_db: Database[Any]) -> None:
    async with httpx.AsyncClient() as client:
        result = await fetch_rhythm_pattern_by_id("nonexistent-id", mock_db)
        assert result is None
