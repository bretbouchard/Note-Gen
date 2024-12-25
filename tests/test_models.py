import pytest
from src.note_gen.models.chord import Chord, ChordQualityType
from src.note_gen.models.note import Note
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.scale_degree import ScaleDegree

class TestChord:
    def test_create_chord(self) -> None:
        root_note = Note(name='C', octave=4)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR, notes=[root_note], bass=None, duration=None, velocity=None, inversion=0)  # Ensure all parameters are provided
        assert chord.root == root_note
        assert chord.quality == ChordQualityType.MAJOR

    def test_invalid_quality(self) -> None:
        root_note = Note(name='C', octave=4)
        with pytest.raises(ValueError, match='Invalid chord quality: invalid_quality'):
            Chord(root=root_note, quality='invalid_quality', notes=[root_note], bass=None, duration=None, velocity=None, inversion=0)  # Ensure all parameters are provided

    def test_invalid_root(self): 
        with pytest.raises(ValueError, match='Root must be a Note instance'):
            Chord(root=None, quality='major', notes=[], bass=None, duration=None, velocity=None, inversion=0)  # Ensure root is valid

class TestNoteModel:
    def test_create_note(self) -> None: 
        note = Note(name='C', octave=4)
        assert note.name == 'C'
        assert note.octave == 4

    def test_invalid_note_name(self) -> None:
        with pytest.raises(ValueError, match='Note name cannot be empty.'): 
            Note(name='', octave=4)

class TestNoteEvent:
    def test_create_note_event(self) -> None:
        note = Note(name='C', octave=4)
        event = NoteEvent(note=note, position=0.0, duration=1.0)
        assert event.note == note
        assert event.position == 0.0

    def test_invalid_position(self) -> None:
        note = Note(name='C', octave=4)
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
        note = Note(name='C', octave=4)
        scale_degree = ScaleDegree(degree=1, note=note)
        assert scale_degree.degree == 1
        assert scale_degree.note == note

    def test_invalid_scale_degree(self) -> None:
        note = Note(name='C', octave=4)
        with pytest.raises(ValueError, match='Degree must be between 1 and 7.'):
            ScaleDegree(degree=8, note=note)
