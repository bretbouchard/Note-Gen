from __future__ import annotations
import pytest
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.chord_quality import ChordQualityType
from pydantic_core import ValidationError


def test_create_chord() -> None:
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
    assert chord.root.note_name == "C"
    assert chord.quality == ChordQualityType.MAJOR


def test_chord_initialization() -> None:
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
    assert len(chord.notes) == 3
    assert chord.notes[0].note_name == "C"
    assert chord.notes[1].note_name == "E"
    assert chord.notes[2].note_name == "G"


def test_chord_diminished_quality() -> None:
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.DIMINISHED)
    assert len(chord.notes) == 3
    assert chord.notes[0].note_name == "C"
    
    # Use enharmonic conversion
    assert Chord._enharmonic_note_name(chord.notes[1].note_name) == "Eb"
    assert Chord._enharmonic_note_name(chord.notes[2].note_name) == "Gb"


def test_chord_inversion() -> None:
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR, inversion=1)
    assert chord.inversion == 1
    assert chord.notes[0].note_name == "E"
    assert chord.notes[1].note_name == "G"
    assert chord.notes[2].note_name == "C"


def test_chord_invalid_inversion() -> None:
    root_note = Note.from_name("C4")
    with pytest.raises(ValidationError) as exc_info:
        Chord(root=root_note, quality=ChordQualityType.MAJOR, inversion=-1)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] in ['value_error', 'greater_than_equal']


def test_chord_MAJOR_with_seventh() -> None:
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR7)
    assert len(chord.notes) == 4
    assert chord.notes[0].note_name == "C"
    assert chord.notes[1].note_name == "E"
    assert chord.notes[2].note_name == "G"
    assert chord.notes[3].note_name == "B"


def test_chord_transposition() -> None:
    root_note = Note.from_name("C4")
    chord1 = Chord(root=root_note, quality=ChordQualityType.MINOR)
    
    transposed_root = Note.from_name("D4")
    chord2 = Chord(root=transposed_root, quality=ChordQualityType.MINOR)
    
    assert chord2.root.note_name == "D"
    assert chord2.notes[0].note_name == "D"
    assert chord2.notes[1].note_name == "F"
    assert chord2.notes[2].note_name == "A"