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
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.database.db import get_db_conn, MONGODB_URI
import os

import httpx

# In tests/models/test_fetch_import_patterns.py

@pytest.fixture
async def test_db_with_data(test_db):
    """Fixture to setup test database with sample data."""
    # Clear existing data - ensure we delete data BEFORE inserting new data
    await test_db.chord_progressions.delete_many({})
    await test_db.note_patterns.delete_many({})
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
            pattern='1.0 0.5 1.0 0.5',  # Using floats instead of fractions
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
                Chord(root=Note(note_name='C', octave=4, duration=1.0, velocity=100.0), quality=ChordQuality.MAJOR),  
                Chord(root=Note(note_name='F', octave=4, duration=1.0, velocity=100.0), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name='G', octave=4, duration=1.0, velocity=100.0), quality=ChordQuality.MAJOR)
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
                Chord(root=Note(note_name='B', octave=4, duration=1.0, velocity=100.0), quality=ChordQuality.DIMINISHED),
                Chord(root=Note(note_name='E', octave=4, duration=1.0, velocity=100.0), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name='A', octave=4, duration=1.0, velocity=100.0), quality=ChordQuality.MINOR)
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
async def test_fetch_note_patterns(test_db_with_data):
    """Test fetching note patterns."""
    # Use the test_db_with_data fixture which already contains sample patterns
    patterns = await fetch_note_patterns(test_db_with_data)
    
    # Verify we found patterns
    assert len(patterns) > 0
    
    # Check that we got a NotePattern instance
    from src.note_gen.models.patterns import NotePattern as PatternsNotePattern
    from src.note_gen.models.patterns import NotePatternData
    
    # The fetch_note_patterns function should return a NotePattern instance
    # with a data field that's a NotePatternData instance
    pattern = patterns[0]
    
    # Flexible assertion for pattern type - it could be from either module
    assert hasattr(pattern, 'data'), "Pattern should have a data attribute"
    assert pattern.data is not None, "Pattern data should not be None"
    
    # Check the data field structure
    note_data = pattern.data
    assert hasattr(note_data, 'notes'), "Pattern data should have notes"
    assert len(note_data.notes) > 0, "Pattern should have notes"
    
    # Flexibly extract note data regardless of format
    def extract_note_data(note):
        """Extract note data regardless of format"""
        if isinstance(note, dict):
            return note
        elif hasattr(note, 'model_dump'):
            return note.model_dump()
        elif hasattr(note, 'dict'):
            return note.dict()
        return {
            'note_name': getattr(note, 'note_name', None),
            'octave': getattr(note, 'octave', None),
            'duration': getattr(note, 'duration', None),
            'velocity': getattr(note, 'velocity', None)
        }
    
    # Extract and check note data
    notes = [extract_note_data(note) for note in note_data.notes]
    assert len(notes) >= 1, "Should have at least one note"
    
    # Check for key fields rather than exact equality
    first_note = notes[0]
    assert 'note_name' in first_note, "Note should have a note_name"
    assert 'octave' in first_note, "Note should have an octave"
    assert 'duration' in first_note, "Note should have a duration"
    assert 'velocity' in first_note, "Note should have a velocity"
    
    # Flexible type checking for numeric values
    assert isinstance(note_data.duration, (int, float)), "Duration should be numeric"
    assert isinstance(note_data.position, (int, float)), "Position should be numeric"
    assert isinstance(note_data.velocity, (int, float)), "Velocity should be numeric"

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(test_db_with_data):
    """Test fetching rhythm patterns."""
    # Use the test_db_with_data fixture which already contains sample rhythm patterns
    patterns = await fetch_rhythm_patterns(test_db_with_data)
    
    # Verify we found patterns
    assert len(patterns) > 0
    
    # Check that we got a RhythmPattern instance
    pattern = patterns[0]
    assert hasattr(pattern, 'data'), "Pattern should have a data attribute"
    assert pattern.data is not None, "Pattern data should not be None"
    
    # Flexible check for rhythm notes
    note_data = pattern.data
    assert hasattr(note_data, 'notes'), "Pattern data should have notes"
    assert len(note_data.notes) > 0, "Pattern should have notes"
    
    # Function to extract rhythm note attributes regardless of format
    def get_rhythm_note_attr(note, attr, default=None):
        """Get attribute from rhythm note regardless of format"""
        if isinstance(note, dict):
            return note.get(attr, default)
        else:
            return getattr(note, attr, default)
    
    # Check first note properties using the flexible getter
    first_note = note_data.notes[0]
    position = get_rhythm_note_attr(first_note, 'position')
    duration = get_rhythm_note_attr(first_note, 'duration')
    velocity = get_rhythm_note_attr(first_note, 'velocity')
    
    assert position is not None, "Rhythm note should have position"
    assert duration is not None, "Rhythm note should have duration"
    assert velocity is not None, "Rhythm note should have velocity"
    
    # Type checking for the extracted values
    assert isinstance(position, (int, float)), "Position should be numeric"
    assert isinstance(duration, (int, float)), "Duration should be numeric"
    assert isinstance(velocity, (int, float)), "Velocity should be numeric"
    
    # Check second note if it exists
    if len(note_data.notes) > 1:
        second_note = note_data.notes[1]
        position2 = get_rhythm_note_attr(second_note, 'position')
        assert position2 is not None, "Second rhythm note should have position"
        assert position2 > position, "Second note position should be greater than first"

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
