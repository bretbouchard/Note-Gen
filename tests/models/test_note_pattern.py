"""Tests for note pattern models."""

from typing import List
import pytest
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.note_pattern import NotePattern


def test_note_pattern_creation() -> None:
    """Test creating a valid note pattern."""
    notes = [
        Note.from_name('C4'),
        Note.from_name('E4'),
        Note.from_name('G4')
    ]
    pattern = NotePattern(name="Test Pattern", data=[0, 4, 7], notes=notes)
    assert len(pattern.notes) == 3
    assert pattern.notes[0].note_name == 'C'
    assert pattern.notes[0].octave == 4
    assert pattern.notes[1].note_name == 'E'
    assert pattern.notes[1].octave == 4
    assert pattern.notes[2].note_name == 'G'
    assert pattern.notes[2].octave == 4


def test_invalid_note_pattern() -> None:
    """Test creating a note pattern with invalid notes."""
    with pytest.raises(ValueError):
        NotePattern(name="Test Pattern", data=[0, 4, 7], notes=["not a note"])


def test_note_pattern_total_duration() -> None:
    """Test calculating total duration of a note pattern."""
    notes = [
        Note.from_name('C4', duration=1.0),
        Note.from_name('E4', duration=0.5),
        Note.from_name('G4', duration=0.25)
    ]
    pattern = NotePattern(name="Test Pattern", data=[0, 4, 7], notes=notes)
    assert pattern.total_duration == 1.75


def test_invalid_note_data() -> None:
    """Test creating a note pattern with invalid note data."""
    with pytest.raises(ValueError):
        NotePattern(name="Test Pattern", data=["invalid"], notes=[])


def test_empty_notes() -> None:
    """Test creating a note pattern with empty notes list."""
    pattern = NotePattern(name="Test Pattern", data=[0, 4, 7])
    assert len(pattern.notes) == 0


def test_invalid_note_type() -> None:
    """Test creating a note pattern with invalid note type."""
    with pytest.raises(ValueError):
        NotePattern(name="Test Pattern", data=[0, 4, 7], notes=[123])  # type: ignore
