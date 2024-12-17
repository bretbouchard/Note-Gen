import pytest
from models.chord_progression import ChordProgression
from models.chord import Chord
from models.note import Note


def test_add_chord():
    progression = ChordProgression()
    chord = Chord(root=Note(note_name="C", midi_number=60), quality="major", notes=[Note(note_name="C", midi_number=60)])
    progression.add_chord(chord)
    assert progression.get_all_chords() == [chord]


def test_get_chord_at():
    progression = ChordProgression()
    chord = Chord(root=Note(note_name="C", midi_number=60), quality="major", notes=[Note(note_name="C", midi_number=60)])
    progression.add_chord(chord)
    assert progression.get_chord_at(0) == chord


def test_validate_chords():
    progression = ChordProgression()
    chord = Chord(root=Note(note_name="C", midi_number=60), quality="major", notes=[Note(note_name="C", midi_number=60)])
    progression.add_chord(chord)
    assert progression.validate_chords() is None  # Should not raise an error
