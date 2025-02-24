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
from src.note_gen.models.note_pattern import NotePattern, NotePatternData
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from pymongo.database import Database
from typing import Any, List, Optional
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_quality import ChordQualityType
from src.note_gen.database.db import get_db_conn, MONGODB_URI
import os

import httpx

# In tests/models/test_fetch_import_patterns.py

@pytest.fixture
async def test_db_with_data(test_db):
    """Fixture to setup test database with sample data."""
    # Clear existing data
    if os.getenv('CLEAR_DB_AFTER_TESTS', '1') == '1':
        await test_db.chord_progressions.delete_many({})
    if os.getenv('CLEAR_DB_AFTER_TESTS', '1') == '1':
        await test_db.note_patterns.delete_many({})
    if os.getenv('CLEAR_DB_AFTER_TESTS', '1') == '1':
        await test_db.rhythm_patterns.delete_many({})

    # Sample note patterns to insert into the test database
    sample_patterns = [
        NotePattern(
            id='1',
            name='Basic triad arpeggio',
            description='...',
            tags=['test'],
            index='1',
            position='0',
            velocity=100.0,
            intervals=[],
            duration=3.0,
            pattern=[0, 4, 7],  # Add a valid pattern
            notes=[
                Note(note_name='C', octave=4, duration=1.0, velocity=100.0),
                Note(note_name='E', octave=4, duration=1.0, velocity=100.0),
                Note(note_name='G', octave=4, duration=1.0, velocity=100.0)
            ],
            data=NotePatternData(
                notes=[
                    {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100.0},
                    {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100.0},
                    {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100.0}
                ],
                duration=3.0,
                position=0.0,
                velocity=100.0,
                intervals=[],  # Ensure this is a list
                index=0,
                created_at=None,
                updated_at=None
            )
        ),
        NotePattern(
            id='2',
            name='Simple melody',
            description='Simple melody',
            tags=['test'],
            duration=1.0,
            index='2',
            position='0',
            velocity=100.0,
            intervals=[],
            pattern=[0, 2],  # Add a valid pattern
            notes=[Note(note_name='D', octave=4, duration=1.0, velocity=100.0)],
            data=NotePatternData(
                notes=[{'note_name': 'D', 'octave': 4, 'duration': 1.0, 'velocity': 100.0}],
                duration=1.0,
                position=0.0,
                velocity=100.0,
                intervals=[],  # Ensure this is a list
                index=0,
                created_at=None,
                updated_at=None
            )
        ),
    ]
    # Sample rhythm patterns to insert into the test database
    sample_rhythm_patterns = [
        RhythmPattern(
            id='1',
            name='Basic Rhythm',
            description='Simple four-beat rhythm',
            tags=['test'],
            pattern='1 1 1 1',  # Space-separated pattern of note durations
            complexity=5,
            data=RhythmPatternData(notes=[RhythmNote(position=0.0, duration=1.0, velocity=100.0), RhythmNote(position=1.0, duration=1.0, velocity=100.0)], duration=4.0)),
        RhythmPattern(
            id='2',
            name='Swing Rhythm',
            description='Swing feel rhythm',
            tags=['test'],
            pattern='1. 1/2 1. 1/2',  # Space-separated pattern with dotted notes and fractions
            complexity=5,
            data=RhythmPatternData(notes=[RhythmNote(position=0.0, duration=1.0, velocity=100.0, swing_ratio=0.5), RhythmNote(position=1.0, duration=1.0, velocity=100.0)], duration=4.0)),
    ]
    # Sample chord progressions to insert into the test database
    sample_chord_progressions = [
        ChordProgression(
            id='1',
            name='Simple I-IV-V',
            key='C',
            scale_type=ScaleType.MAJOR,
            scale_info=FakeScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100.0),
                scale_type=ScaleType.MAJOR
            ),
            chords=[
                Chord(root=Note(note_name='C', octave=4, duration=1.0, velocity=100.0), quality=ChordQualityType.MAJOR),  
                Chord(root=Note(note_name='F', octave=4, duration=1.0, velocity=100.0), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name='G', octave=4, duration=1.0, velocity=100.0), quality=ChordQualityType.MAJOR)
            ]
        ),
        ChordProgression(
            id='2',
            name='Minor ii-V-i',
            key='A',
            scale_type=ScaleType.MINOR,
            scale_info=FakeScaleInfo(
                root=Note(note_name='A', octave=4, duration=1.0, velocity=100.0),
                scale_type=ScaleType.MINOR
            ),
            chords=[
                Chord(root=Note(note_name='B', octave=4, duration=1.0, velocity=100.0), quality=ChordQualityType.DIMINISHED),
                Chord(root=Note(note_name='E', octave=4, duration=1.0, velocity=100.0), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name='A', octave=4, duration=1.0, velocity=100.0), quality=ChordQualityType.MINOR)
            ]
        ),
    ]
    
    # Insert sample_patterns into the test database
    for pattern in sample_patterns:
        await test_db.note_patterns.insert_one(pattern.model_dump())
    
    # Insert sample rhythm patterns into the test database
    for pattern in sample_rhythm_patterns:
        await test_db.rhythm_patterns.insert_one(pattern.model_dump())
    
    # Insert sample chord progressions into the test database
    for progression in sample_chord_progressions:
        await test_db.chord_progressions.insert_one(progression.model_dump())
    yield test_db

    # Cleanup
    if os.getenv("CLEAR_DB_AFTER_TESTS", "1") == "1":
        await test_db.chord_progressions.delete_many({})
        await test_db.note_patterns.delete_many({})
        await test_db.rhythm_patterns.delete_many({})

@pytest.mark.asyncio
async def test_fetch_note_patterns(test_db):
    """Test fetching note patterns."""
    async with get_db_conn() as conn:
        patterns = await fetch_note_patterns(conn.db)
        assert len(patterns) > 0
        assert patterns[0].data.notes == [{'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100.0}, {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100.0}, {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100.0}]
        assert isinstance(patterns[0].data.duration, float)
        assert isinstance(patterns[0].data.position, float)
        assert isinstance(patterns[0].data.velocity, float)

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(test_db):
    """Test fetching rhythm patterns."""
    async with get_db_conn() as conn:
        patterns = await fetch_rhythm_patterns(conn.db)
        assert len(patterns) > 0
        assert patterns[0].data.notes == [RhythmNote(position=0.0, duration=1.0, velocity=100.0), RhythmNote(position=1.0, duration=1.0, velocity=100.0)]

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id_not_found(test_db):
    """Test fetching non-existent chord progression."""
    async with get_db_conn() as conn:
        result = await fetch_chord_progression_by_id("nonexistent-id", conn.db)
        assert result is None

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id_not_found(test_db):
    """Test fetching non-existent note pattern."""
    async with get_db_conn() as conn:
        result = await fetch_note_pattern_by_id("nonexistent-id", conn.db)
        assert result is None

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id_not_found(test_db):
    """Test fetching non-existent rhythm pattern."""
    async with get_db_conn() as conn:
        result = await fetch_rhythm_pattern_by_id("nonexistent-id", conn.db)
        assert result is None
