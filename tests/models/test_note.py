import pytest
from src.models import note, note_sequence
from src.models import chord
from src.models import scale_degree
from src.models import scale


def test_note_initialization() -> None:
    note = note.Note(name='C', octave=4, duration=1.0, velocity=100)
    assert note.name == 'C'
    assert note.octave == 4
    assert note.duration == 1.0
    assert note.velocity == 100


def test_invalid_note_name() -> None:
    with pytest.raises(ValueError):
        note.Note(name='H', )  # Invalid note name


def test_invalid_octave() -> None:
    with pytest.raises(ValueError):
        note.Note(name='C',  octave=10)  # Invalid octave


def test_midi_number() -> None:
    note = note.Note(name='C', octave=4)
    assert note.midi_number == 60  # Corrected to Middle C (C4)
    
    note = note.Note(name='C', accidental='#', octave=4)
    assert note.midi_number == 61  # C# in octave 4


def test_string_representation() -> None:
    note = note.Note(name='D', accidental='b', octave=5)  # Setting accidental to flat
    assert str(note) == 'D flat in octave 5'


def test_note_equality() -> None:
    note1 = note.Note(name='E',  octave=4)
    note2 = note.Note(name='E',  octave=4)
    assert note1 == note2
