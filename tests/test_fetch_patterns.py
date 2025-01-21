"""Tests for fetch_patterns.py"""

import pytest
from src.note_gen.fetch_patterns import (
    fetch_chord_progressions,
    fetch_chord_progression_by_id,
    fetch_rhythm_patterns,
    fetch_rhythm_pattern_by_id,
    fetch_note_patterns,
    fetch_note_pattern_by_id,
    process_chord_data
)
from src.note_gen.models.enums import ChordQualityType, ScaleType
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote, RhythmPatternData
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.musical_elements import Note

# Sample test data
# Update SAMPLE_CHORD_PROGRESSIONS in test_fetch_patterns.py
SAMPLE_CHORD_PROGRESSIONS = [
    {
        "id": "1",
        "name": "I-IV-V",
        "complexity": 1.0,
        "key": "C",  # Add this
        "scale_type": ScaleType.MAJOR,  # Add this
        "chords": [
            {
                "root": Note(note_name="C", octave=4, duration=1, velocity=100),
                "quality": ChordQualityType.MAJOR,
                "notes": [
                    Note(note_name="C", octave=4, duration=1, velocity=100),
                    Note(note_name="E", octave=4, duration=1, velocity=100),
                    Note(note_name="G", octave=4, duration=1, velocity=100)
                ]
            },
            {
                "root": Note(note_name="F", octave=4, duration=1, velocity=100),
                "quality": ChordQualityType.MAJOR,
                "notes": [
                    Note(note_name="F", octave=4, duration=1, velocity=100),
                    Note(note_name="A", octave=4, duration=1, velocity=100),
                    Note(note_name="C", octave=5, duration=1, velocity=100)
                ]
            },
            {
                "root": Note(note_name="G", octave=4, duration=1, velocity=100),
                "quality": ChordQualityType.MAJOR,
                "notes": [
                    Note(note_name="G", octave=4, duration=1, velocity=100),
                    Note(note_name="B", octave=4, duration=1, velocity=100),
                    Note(note_name="D", octave=5, duration=1, velocity=100)
                ]
            }
        ]
    }
]


SAMPLE_NOTE_PATTERNS = [
    {
        "id": "1",
        "name": "Simple Arpeggio",
        "data": [1, 3, 5],  # Scale degrees as integers
        "notes": [
            Note(note_name="C", octave=4, duration=1, velocity=100),  # Ensure duration is included
            Note(note_name="E", octave=4, duration=1, velocity=100),
            Note(note_name="G", octave=4, duration=1, velocity=100)
        ],
        "description": "Basic triad arpeggio",
        "tags": ["test"],
        "is_test": True
    }
]


SAMPLE_RHYTHM_PATTERNS = [
    {
        "id": "1",
        "name": "Basic Quarter Notes",
        "data": RhythmPatternData(
            notes=[
                RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False),
                RhythmNote(position=1.0, duration=1.0, velocity=100, is_rest=False),
                RhythmNote(position=2.0, duration=1.0, velocity=100, is_rest=False),
                RhythmNote(position=3.0, duration=1.0, velocity=100, is_rest=False)
            ],
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.0,
            swing_ratio=0.67,
            style="basic",
            default_duration=1.0,
            total_duration=4.0,
            accent_pattern=[],
            groove_type="straight",
            variation_probability=0.0,
            duration=4.0
        ),
        "description": "Basic quarter note pattern",
        "tags": ["test"],
        "complexity": 1.0,
        "style": "basic",
        "pattern": "",
        "is_test": True
    }
]

@pytest.mark.asyncio
async def test_fetch_chord_progressions(clean_test_db):
    db = clean_test_db
    result = await fetch_chord_progressions(db)
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id(clean_test_db):
    db = clean_test_db
    progression_id = "1"
    result = await fetch_chord_progression_by_id(progression_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(clean_test_db):
    db = clean_test_db
    result = await fetch_rhythm_patterns(db)
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(clean_test_db):
    db = clean_test_db
    pattern_id = "1"
    result = await fetch_rhythm_pattern_by_id(pattern_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_note_patterns(clean_test_db):
    db = clean_test_db
    result = await fetch_note_patterns(db)
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(clean_test_db):
    db = clean_test_db
    pattern_id = "1"
    result = await fetch_note_pattern_by_id(pattern_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_with_invalid_data(clean_test_db):
    db = clean_test_db
    # Insert invalid data directly into the test database
    await db.chord_progressions.insert_one({"id": "invalid_id", "name": "Invalid Chord Progression", "chords": []})
    with pytest.raises(ValueError, match="Invalid chord progression data"):  # Expecting a ValueError for invalid data
        await fetch_chord_progressions(db)

@pytest.mark.asyncio
async def test_fetch_chord_progressions_with_new_data(clean_test_db):
    db = clean_test_db
    result = await fetch_chord_progressions(db)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_note_patterns_with_new_data(clean_test_db):
    db = clean_test_db
    result = await fetch_note_patterns(db)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns_with_new_data(clean_test_db):
    db = clean_test_db
    result = await fetch_rhythm_patterns(db)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_process_chord_data() -> None:
    """Test processing chord data."""
    # Test valid chord data
    valid_data = {
        'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
        'quality': "major"
    }
    processed = process_chord_data(valid_data)
    assert processed['quality'] == "major"

    # Test invalid quality
    invalid_quality_data = {
        'root': {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
        'quality': 'INVALID'
    }
    processed = process_chord_data(invalid_quality_data)
    assert processed['quality'] == "major"  # Should default to major
