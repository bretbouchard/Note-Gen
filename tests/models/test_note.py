import pytest
from src.models.note import Note  # Import Note class directly
from src.models.note_sequence import NoteSequence
from src.models.chord import Chord
from src.models.scale_degree import ScaleDegree
from src.models.scale import Scale


def test_note_initialization() -> None:
    note = Note(name='C', octave=4, duration=1.0, velocity=100)  # Use Note directly
    assert note.name == 'C'
    assert note.octave == 4
    assert note.duration == 1.0
    assert note.velocity == 100


def test_invalid_note_name() -> None:
    with pytest.raises(ValueError):
        Note(name='H')  # Use Note directly


def test_invalid_octave() -> None:
    with pytest.raises(ValueError):
        Note(name='C', octave=10)  # Use Note directly


def test_midi_number() -> None:
    note = Note(name='C', octave=4)  # Use Note directly
    assert note.midi_number == 60  # Corrected to Middle C (C4)
    
    note = Note(name='C', accidental='#', octave=4)  # Use Note directly
    assert note.midi_number == 61  # C# in octave 4


def test_string_representation() -> None:
    note = Note(name='D', accidental='b', octave=5)  # Use Note directly
    assert str(note) == 'D flat in octave 5'


def test_note_equality() -> None:
    note1 = Note(name='E', octave=4)  # Use Note directly
    note2 = Note(name='E', octave=4)  # Use Note directly
    assert note1 == note2


def test_valid_durations() -> None:
    """Test initialization of Note with valid durations."""
    note1 = Note(name='C', octave=4, duration=2.0, velocity=100)
    note2 = Note(name='D', octave=4, duration=3.0, velocity=100)
    assert note1.duration == 2.0
    assert note2.duration == 3.0


def test_invalid_duration() -> None:
    """Test initialization of Note with invalid durations."""
    with pytest.raises(ValueError):
        Note(name='E', octave=4, duration=0, velocity=100)  # Duration cannot be zero
    with pytest.raises(ValueError):
        Note(name='F', octave=4, duration=-1, velocity=100)  # Duration cannot be negative