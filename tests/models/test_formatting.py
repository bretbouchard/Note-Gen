import pytest
from src.note_gen.core.enums import ScaleType, ChordQuality, PatternDirection
from src.note_gen.core.constants import (
    COMMON_PROGRESSIONS,
    NOTE_PATTERNS,
    RHYTHM_PATTERNS
)
from src.note_gen.models.note import Note
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.models.patterns import NotePattern


def test_format_chord_progression_valid() -> None:
    """Test formatting valid chord progressions"""
    progression = COMMON_PROGRESSIONS["I-IV-V"]


def test_note_formatting() -> None:
    # Test note string representation
    note = Note(note_name="C", octave=4)
    assert str(note) == "C4"
    
    # Test note with accidental
    note = Note(note_name="C#", octave=4)
    assert str(note) == "C#4"
    
    # Test note with flat preference
    note = Note(note_name="Db", octave=4, prefer_flats=True)
    assert str(note) == "Db4"

def test_rhythm_pattern_formatting() -> None:
    pattern = RhythmPattern(
        name="Test Pattern",
        pattern=[1.0, 0.5, 0.5, 1.0],
        time_signature="4/4",
        description="Test description",
        complexity=0.5,
        data={}
    )
    expected_str = "Test Pattern (4/4): [1.0, 0.5, 0.5, 1.0]"
    assert str(pattern) == expected_str

def test_note_pattern_formatting() -> None:
    notes = [
        Note(note_name="C", octave=4),
        Note(note_name="E", octave=4),
        Note(note_name="G", octave=4)
    ]
    pattern = NotePattern(
        name="Test Pattern",
        pattern=notes,
        direction="up",
        description="Test description",
        complexity=0.5,
        data={}
    )
    expected_str = "Test Pattern: [C4, E4, G4] (up)"
    assert str(pattern) == expected_str
