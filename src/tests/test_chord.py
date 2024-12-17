import pytest
from models.chord import Chord, ChordQuality
from models.note import Note


def test_chord_creation():
    root = Note(note_name="C", midi_number=60)
    chord = Chord(root=root, quality=ChordQuality.major, notes=[root])
    assert chord.root == root
    assert chord.quality == ChordQuality.major


def test_chord_equality():
    root1 = Note(note_name="C", midi_number=60)
    root2 = Note(note_name="C", midi_number=60)
    chord1 = Chord(root=root1, quality=ChordQuality.major, notes=[root1])
    chord2 = Chord(root=root2, quality=ChordQuality.major, notes=[root2])
    assert chord1 == chord2


def test_chord_invalid_notes():
    with pytest.raises(ValueError):
        Chord(root=None, quality=ChordQuality.major, notes=[])  # No root or notes
