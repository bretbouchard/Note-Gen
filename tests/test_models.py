"""Tests for musical models."""

from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.scale_degree import ScaleDegree

import pytest

class TestChord:
    def test_create_chord(self) -> None:
        root_note = Note.from_name('C4')
        chord = Chord.from_quality(root=root_note, quality=ChordQualityType.MAJOR)
        assert chord.root.note_name == 'C'
        assert chord.quality == ChordQualityType.MAJOR

    def test_invalid_quality(self) -> None:
        root_note = Note.from_name('C4')
        with pytest.raises(ValueError, match="Input should be 'major', 'minor', 'diminished', 'augmented'"):
            Chord.from_quality(root=root_note, quality='invalid_quality')

    def test_invalid_root(self) -> None:
        with pytest.raises(ValueError, match="Input should be a valid dictionary or instance of Note"):
            Chord.from_quality(root=None, quality=ChordQualityType.MAJOR)

class TestNoteModel:
    def test_create_note(self) -> None:
        note = Note.from_name('C4')
        assert note.note_name == 'C'
        assert note.octave == 4

    def test_invalid_note_name(self) -> None:
        with pytest.raises(ValueError, match="Invalid note name"):
            Note.from_name('')

class TestNoteEvent:
    def test_create_note_event(self) -> None:
        note = Note.from_name('C4')
        event = NoteEvent(note=note, position=0.0, duration=1.0)
        assert event.note == note
        assert event.position == 0.0

    def test_invalid_position(self) -> None:
        note = Note.from_name('C4')
        with pytest.raises(ValueError, match='Position cannot be negative.'):
            NoteEvent(note=note, position=-1.0)

class TestNotePattern:
    def test_create_note_pattern(self) -> None:
        pattern = NotePattern(name='Test Pattern', data=[1, 2, 3])
        assert pattern.name == 'Test Pattern'
        assert pattern.data == [1, 2, 3]

    def test_invalid_data(self) -> None:
        with pytest.raises(ValueError):
            NotePattern(name='Invalid Pattern', data=None)

class TestScaleDegree:
    def test_create_scale_degree(self) -> None:
        note = Note.from_name('C4')
        scale_degree = ScaleDegree(degree=1, note=note)
        assert scale_degree.degree == 1
        assert scale_degree.note == note

    def test_invalid_scale_degree(self) -> None:
        note = Note.from_name('C4')
        with pytest.raises(ValueError, match='Degree must be between 1 and 7.'):
            ScaleDegree(degree=8, note=note)
