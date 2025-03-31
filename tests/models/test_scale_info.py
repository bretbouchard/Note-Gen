"""Test scale info functionality."""
from typing import List
import pytest
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.core.enums import ScaleType

def test_scale_info_basic() -> None:
    """Test basic scale info functionality."""
    scale_info = ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    
    # Test note validation
    assert scale_info.is_note_in_scale(
        Note(
            pitch="C",
            octave=4,
            duration=1.0,
            velocity=64,
            position=0.0
        )
    )
    
    # Test scale degree to note conversion
    assert scale_info.get_scale_degree("C") == 1
    assert scale_info.get_scale_degree("G") == 5

def test_scale_info_complex() -> None:
    """Test more complex scale info scenarios."""
    scale_info = ScaleInfo(key="F#", scale_type=ScaleType.MINOR)
    
    # Test note validation
    assert scale_info.is_note_in_scale(
        Note(
            pitch="F#",
            octave=4,
            duration=1.0,
            velocity=64,
            position=0.0
        )
    )

def test_scale_info_invalid_input() -> None:
    """Test invalid input handling."""
    scale_info = ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    
    # Test invalid note
    assert not scale_info.is_note_in_scale(
        Note(
            pitch="C#",
            octave=4,
            duration=1.0,
            velocity=64,
            position=0.0
        )
    )

def test_scale_info_edge_cases() -> None:
    """Test edge cases."""
    scale_info = ScaleInfo(key="Bb", scale_type=ScaleType.MAJOR)
    assert scale_info.key == "Bb"

def test_get_scale_notes() -> None:
    """Test getting scale notes."""
    # Test major scale
    scale_info = ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    major_notes = scale_info.get_scale_notes()
    expected_major = ["C", "D", "E", "F", "G", "A", "B"]
    assert [note.pitch for note in major_notes] == expected_major

    # Test minor scale
    scale_info = ScaleInfo(key="A", scale_type=ScaleType.MINOR)
    minor_notes = scale_info.get_scale_notes()
    expected_minor = ["A", "B", "C", "D", "E", "F", "G"]
    assert [note.pitch for note in minor_notes] == expected_minor

    # Test with sharps
    scale_info = ScaleInfo(key="G", scale_type=ScaleType.MAJOR)
    sharp_notes = scale_info.get_scale_notes()
    expected_sharp = ["G", "A", "B", "C", "D", "E", "F#"]
    assert [note.pitch for note in sharp_notes] == expected_sharp
