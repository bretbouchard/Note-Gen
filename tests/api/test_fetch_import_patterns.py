import pytest
from src.note_gen.fetch_patterns import (
    fetch_chord_progressions,
    fetch_note_patterns,
    fetch_rhythm_patterns,
    fetch_chord_progression_by_id,
    fetch_note_pattern_by_id,
    fetch_rhythm_pattern_by_id,
)
from src.note_gen.models.patterns import ChordProgression, NotePattern, NotePatternData, RhythmPattern, RhythmPatternData, RhythmNote
from pymongo.database import Database
from typing import Any, List, Optional
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.core.enums import ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.database.db import get_db_conn, MONGODB_URI
import os

import httpx

# In tests/models/test_fetch_import_patterns.py

@pytest.fixture(scope="function")
async def test_db_with_data():
    """Fixture to setup test database with sample data."""
    db = await get_db_conn()
    
    # Clear existing data
    await db.chord_progressions.delete_many({})
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})

    # Create sample data
    sample_rhythm_pattern = RhythmPattern(
        name="Test Rhythm Pattern",
        pattern_data=RhythmPatternData(
            notes=[
                RhythmNote(duration=1.0, is_rest=False),
                RhythmNote(duration=0.5, is_rest=True)
            ]
        )
    )

    sample_note_pattern = NotePattern(
        name="Test Note Pattern",
        pattern_data=NotePatternData(
            notes=[
                Note(note_name="C", octave=4, duration=1.0, velocity=64),
                Note(note_name="E", octave=4, duration=0.5, velocity=64)
            ]
        )
    )

    # Insert sample data
    await db.rhythm_patterns.insert_one(sample_rhythm_pattern.model_dump())
    await db.note_patterns.insert_one(sample_note_pattern.model_dump())

    return db

@pytest.mark.asyncio
async def test_fetch_note_patterns():
    db = await get_db_conn()  # This returns a coroutine
    db = await db  # Await the coroutine to get the actual database connection
    patterns = await fetch_note_patterns(db)
    assert len(patterns) > 0
    assert isinstance(patterns[0], NotePattern)

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns():
    db = await get_db_conn()  # This returns a coroutine
    db = await db  # Await the coroutine to get the actual database connection
    patterns = await fetch_rhythm_patterns(db)
    assert len(patterns) > 0
    assert isinstance(patterns[0], RhythmPattern)

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_not_found(test_db):
    """Test fetching non-existent chord progression."""
    # Use the test_db directly since it's already a database connection
    result = await fetch_chord_progression_by_id("nonexistent-id", test_db)
    assert result is None

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id_not_found(test_db):
    """Test fetching non-existent note pattern."""
    # Use the test_db directly since it's already a database connection
    result = await fetch_note_pattern_by_id("nonexistent-id", test_db)
    assert result is None

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id_not_found(test_db):
    """Test fetching non-existent rhythm pattern."""
    # Use the test_db directly since it's already a database connection
    result = await fetch_rhythm_pattern_by_id("nonexistent-id", test_db)
    assert result is None
