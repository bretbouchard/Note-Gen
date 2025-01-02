"""Test note model."""

import pytest
from src.note_gen.models.note import Note


def test_note_initialization() -> None:
    """Test initialization of Note with valid data."""
    note = Note.from_name('C4')
    assert note.note_name == 'C'  # Correct assertion for base note name
    assert note.octave == 4


def test_invalid_note_name() -> None:
    """Test initialization of Note with invalid note name."""
    with pytest.raises(ValueError):
        Note.from_name('H')  # H is not a valid note name


def test_valid_octaves() -> None:
    """Test initialization of Note with valid octaves."""
    valid_octaves = [0, 4, 8] 
    for octave in valid_octaves:
        note = Note.from_name(f'C{octave}')
        assert note.octave == octave


def test_invalid_octave() -> None:
    """Test initialization of Note with invalid octave."""
    invalid_octaves = [-1, 9, 12]  # Invalid octaves
    for octave in invalid_octaves:
        with pytest.raises(ValueError):
            Note.from_name(f'C{octave}')  # Attempt to create a Note with an invalid octave


def test_midi_number() -> None:
    """Test MIDI number calculation."""
    note = Note.from_name('C4')
    assert note.midi_number == 60  # C4 is MIDI note 60


def test_string_representation() -> None:
    """Test string representation of Note."""
    note = Note.from_name('C#5')
    assert str(note) == 'C#5'


def test_note_equality() -> None:
    """Test note equality."""
    note1 = Note.from_name('C4')
    note2 = Note.from_name('C4')
    note3 = Note.from_name('D4')
    assert note1 == note2
    assert note1 != note3
    assert note1.note_name == note2.note_name
    assert note1.octave == note2.octave


def test_valid_durations() -> None:
    """Test initialization of Note with valid durations."""
    valid_durations = [0.0, 0.5, 1.0, 2.0]
    for duration in valid_durations:
        note = Note.from_name('C4', duration=duration)
        assert note.duration == duration


def test_invalid_duration() -> None:
    """Test initialization of Note with invalid duration."""
    with pytest.raises(ValueError):
        Note.from_name('C4', duration=-1.0)  # Negative duration is invalid