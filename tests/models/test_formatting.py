import unittest
from src.note_gen.models.note import Note
from src.note_gen.models.rhythm import RhythmNote, RhythmPattern
from src.note_gen.core.constants import COMMON_PROGRESSIONS
from src.note_gen.core.enums import ChordQuality, ScaleType
from src.note_gen.models.chord import Chord, ChordProgressionItem
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale import ScaleInfo

"""Test formatting utilities."""

def test_format_chord_progression_valid() -> None:
    """Test formatting valid chord progressions"""
    # Create scale info
    scale_info = ScaleInfo(key="C", scale_type=ScaleType.MAJOR).model_dump()
    
    # Create chord progression items
    progression = ChordProgression(
        name="I-IV-V",
        key="C",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info,
        items=[
            {
                "chord": {
                    "root": "C",
                    "quality": ChordQuality.MAJOR,
                    "duration": 1.0,
                    "velocity": 64
                },
                "duration": 1.0,
                "position": 0.0
            },
            {
                "chord": {
                    "root": "F",
                    "quality": ChordQuality.MAJOR,
                    "duration": 1.0,
                    "velocity": 64
                },
                "duration": 1.0,
                "position": 1.0
            },
            {
                "chord": {
                    "root": "G",
                    "quality": ChordQuality.MAJOR,
                    "duration": 1.0,
                    "velocity": 64
                },
                "duration": 1.0,
                "position": 2.0
            }
        ]
    )
    
    formatted = str(progression)
    assert "C" in formatted
    assert "F" in formatted
    assert "G" in formatted


def test_note_formatting() -> None:
    """Test note string formatting with pitch."""
    # Test basic note string representation
    note = Note(pitch="C", octave=4)
    assert str(note) == "C4"
    
    # Test note with sharp accidental
    note = Note(pitch="C#", octave=4)
    assert str(note) == "C#4"
    
    # Test note with flat
    note = Note(pitch="Db", octave=4, prefer_flats=True)
    assert str(note) == "Db4"


class TestFormatting(unittest.TestCase):
    def test_rhythm_pattern_formatting(self):
        """Test rhythm pattern formatting with proper pitch usage."""
        notes = [
            RhythmNote(
                note=Note(pitch="C", octave=4),
                position=0.0,
                duration=1.0
            ),
            RhythmNote(
                note=Note(pitch="E", octave=4),
                position=1.0,
                duration=1.0
            ),
            RhythmNote(
                note=Note(pitch="G", octave=4),
                position=2.0,
                duration=1.0
            ),
            RhythmNote(
                note=Note(pitch="C", octave=5),
                position=3.0,
                duration=1.0
            )
        ]
        
        pattern = RhythmPattern(
            name="Test Pattern",
            pattern=notes,  # Changed from notes to pattern
            time_signature=(4, 4),
            description="Test pattern"
        )
        
        self.assertEqual(len(pattern.pattern), 4)  # Changed from notes to pattern
        first_note = pattern.pattern[0]  # Changed from notes to pattern
        self.assertEqual(str(first_note.note), "C4")
        self.assertEqual(first_note.note.pitch, "C")
        self.assertEqual(first_note.note.octave, 4)


def test_note_pattern_formatting() -> None:
    """Test note pattern string formatting."""
    note = Note(pitch="C", octave=4)
    assert str(note) == "C4"
    assert note.pitch == "C"
    assert note.octave == 4

    # Test with accidentals
    sharp_note = Note(pitch="F#", octave=3)
    assert str(sharp_note) == "F#3"
    assert sharp_note.pitch == "F#"
    
    flat_note = Note(pitch="Bb", octave=5)
    assert str(flat_note) == "Bb5"
    assert flat_note.pitch == "Bb"
