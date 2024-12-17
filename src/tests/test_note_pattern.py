import pytest
from models.note_pattern import NotePattern


def test_note_pattern_creation():
    pattern = NotePattern(name="Simple Triad", data=[0, 2, 4])
    assert pattern.name == "Simple Triad"
    assert pattern.data == [0, 2, 4]


def test_note_pattern_get_notes():
    pattern = NotePattern(name="Simple Triad", data=[0, 2, 4])
    notes = pattern.get_notes()
    assert len(notes) == 3  # Assuming it generates 3 notes
