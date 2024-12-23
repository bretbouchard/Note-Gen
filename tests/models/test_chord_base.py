import pytest
from src.note_gen.models.chord_base import ChordBase
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ChordQualityType


def test_chord_base_initialization():
    root_note = Note(name='C', octave=4)
    chord_base = ChordBase(root=root_note, intervals=[0, 4, 7])
    assert chord_base.root == root_note
    assert chord_base.intervals == [0, 4, 7]


def test_chord_base_get_intervals():
    root_note = Note(name='C', octave=4)
    chord_base = ChordBase(root=root_note, intervals=[0, 4, 7])
    intervals = chord_base.get_intervals(ChordQualityType.MAJOR)
    assert intervals == [0, 4, 7]


def test_chord_base_str():
    root_note = Note(name='C', octave=4)
    chord_base = ChordBase(root=root_note, intervals=[0, 4, 7])
    assert str(chord_base) == "ChordBase(root=C natural in octave 4, intervals=[0, 4, 7])"
