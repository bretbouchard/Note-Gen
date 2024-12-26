import pytest
import logging
from src.note_gen.models.musical_elements import Note , Chord
from src.note_gen.models.enums import ChordQualityType  
from src.note_gen.models.chord_base import ChordBase

# Configure logging to output to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_chord_creation() -> None:
    root = Note(name='C', octave=4)
    notes = [
        Note(name='C', octave=4),
        Note(name='E', octave=4),
        Note(name='G', octave=4)
    ]
    chord = Chord(root=root, notes=notes, quality=ChordQualityType.MAJOR)
    assert chord.root == root
    assert chord.notes is not None
    assert len(chord.notes) == 3
    assert all(isinstance(note, Note) for note in chord.notes)
    assert chord.notes[0].name == 'C'
    assert chord.notes[1].name == 'E'
    assert chord.notes[2].name == 'G'
    assert chord.quality == ChordQualityType.MAJOR
    assert chord.notes[0].octave == 4
    assert chord.notes[1].octave == 4
    assert chord.notes[2].octave == 4

def test_chord_validation() -> None:
    root = Note(name='C', octave=4)
    # Invalid chord - empty notes list
    with pytest.raises(ValueError):
        Chord(root=root, notes=[], quality=ChordQualityType.MAJOR)
    # Invalid chord - non-Note instance
    with pytest.raises(ValueError):
        Chord(root=root, notes=["not_a_note"], quality=ChordQualityType.MAJOR)

def test_chord_inversion() -> None:
    logging.debug("Starting test_chord_inversion")
    root = Note(name='C', octave=4)
    notes = [
        Note(name='C', octave=4),
        Note(name='E', octave=4),
        Note(name='G', octave=4)
    ]
    chord = Chord(root=root, notes=notes, quality=ChordQualityType.MAJOR, inversion=1)
    logging.debug(f"Chord inversion set to: {chord.inversion}")
    logging.debug(f"Initial notes list: {[note.name for note in chord.notes]}")
    assert chord.inversion == 1
    assert chord.notes is not None
    # Add assertion to check the expected notes based on inversion
    assert chord.notes == [Note(name='E', octave=4), Note(name='G', octave=4), Note(name='C', octave=5)]  # Example for 1st inversion
    assert chord.notes[0].octave == 4
    assert chord.notes[1].octave == 4
    assert chord.notes[2].octave == 5

def test_chord_from_base() -> None:
    base = ChordBase(
        root=Note(name='C', octave=4),  # Create a Note instance for C4
        intervals=[0, 4, 7]  # Major chord intervals
    )
    chord = Chord.from_base(base)
    assert chord.root is not None
    assert chord.root.name == 'C'
    assert chord.notes is not None
    assert len(chord.notes) == 3
    assert chord.notes[0].name == 'C'
    assert chord.notes[1].name == 'E'
    assert chord.notes[2].name == 'G'
    assert chord.quality == ChordQualityType.MAJOR
    assert chord.notes[0].octave == 4
    assert chord.notes[1].octave == 4
    assert chord.notes[2].octave == 4

def test_chord_quality_types() -> None:
    # Test different chord qualities
    major_chord = Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)])
    assert major_chord.quality == ChordQualityType.MAJOR
    assert major_chord.notes[0].octave == 4
    assert major_chord.notes[1].octave == 4
    assert major_chord.notes[2].octave == 4

    minor_chord = Chord(root=Note(name='A', octave=4), quality=ChordQualityType.MINOR, notes=[Note(name='A', octave=4), Note(name='C', octave=4), Note(name='E', octave=4)])
    assert minor_chord.quality == ChordQualityType.MINOR
    assert minor_chord.notes[0].octave == 4
    assert minor_chord.notes[1].octave == 4
    assert minor_chord.notes[2].octave == 4

    diminished_chord = Chord(root=Note(name='B', octave=4), quality=ChordQualityType.DIMINISHED, notes=[Note(name='B', octave=4), Note(name='D', octave=4), Note(name='F', octave=4)])
    assert diminished_chord.quality == ChordQualityType.DIMINISHED
    assert diminished_chord.notes[0].octave == 4
    assert diminished_chord.notes[1].octave == 4
    assert diminished_chord.notes[2].octave == 4

    augmented_chord = Chord(root=Note(name='C', octave=4), quality=ChordQualityType.AUGMENTED, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G#', octave=4)])
    assert augmented_chord.quality == ChordQualityType.AUGMENTED
    assert augmented_chord.notes[0].octave == 4
    assert augmented_chord.notes[1].octave == 4
    assert augmented_chord.notes[2].octave == 4

    half_diminished_chord = Chord(root=Note(name='D', octave=4), quality=ChordQualityType.HALF_DIMINISHED, notes=[Note(name='D', octave=4), Note(name='F', octave=4), Note(name='Ab', octave=4)])
    assert half_diminished_chord.quality == ChordQualityType.HALF_DIMINISHED
    assert half_diminished_chord.notes[0].octave == 4
    assert half_diminished_chord.notes[1].octave == 4
    assert half_diminished_chord.notes[2].octave == 4

    dominant_chord = Chord(root=Note(name='G', octave=4), quality=ChordQualityType.DOMINANT, notes=[Note(name='G', octave=4), Note(name='B', octave=4), Note(name='D', octave=4)])
    assert dominant_chord.quality == ChordQualityType.DOMINANT
    assert dominant_chord.notes[0].octave == 4
    assert dominant_chord.notes[1].octave == 4
    assert dominant_chord.notes[2].octave == 4

    major_seventh_chord = Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR_SEVENTH, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4), Note(name='B', octave=4)])
    assert major_seventh_chord.quality == ChordQualityType.MAJOR_SEVENTH
    assert major_seventh_chord.notes[0].octave == 4
    assert major_seventh_chord.notes[1].octave == 4
    assert major_seventh_chord.notes[2].octave == 4
    assert major_seventh_chord.notes[3].octave == 4

    minor_seventh_chord = Chord(root=Note(name='A', octave=4), quality=ChordQualityType.MINOR_SEVENTH, notes=[Note(name='A', octave=4), Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)])
    assert minor_seventh_chord.quality == ChordQualityType.MINOR_SEVENTH
    assert minor_seventh_chord.notes[0].octave == 4
    assert minor_seventh_chord.notes[1].octave == 4
    assert minor_seventh_chord.notes[2].octave == 4
    assert minor_seventh_chord.notes[3].octave == 4

    diminished_seventh_chord = Chord(root=Note(name='B', octave=4), quality=ChordQualityType.DIMINISHED_SEVENTH, notes=[Note(name='B', octave=4), Note(name='D', octave=4), Note(name='F', octave=4), Note(name='Ab', octave=4)])
    assert diminished_seventh_chord.quality == ChordQualityType.DIMINISHED_SEVENTH
    assert diminished_seventh_chord.notes[0].octave == 4
    assert diminished_seventh_chord.notes[1].octave == 4
    assert diminished_seventh_chord.notes[2].octave == 4
    assert diminished_seventh_chord.notes[3].octave == 4

    augmented_seventh_chord = Chord(root=Note(name='C', octave=4), quality=ChordQualityType.AUGMENTED_SEVENTH, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G#', octave=4), Note(name='B', octave=4)])
    assert augmented_seventh_chord.quality == ChordQualityType.AUGMENTED_SEVENTH
    assert augmented_seventh_chord.notes[0].octave == 4
    assert augmented_seventh_chord.notes[1].octave == 4
    assert augmented_seventh_chord.notes[2].octave == 4
    assert augmented_seventh_chord.notes[3].octave == 4