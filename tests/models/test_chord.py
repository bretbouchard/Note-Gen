from typing import Any
import pytest
import logging
from src.models.chord import Chord
from src.models.note import Note
from src.models.chord_quality import ChordQuality
from src.models.enums import ChordQualityType  # This is the correct enum
from src.models.chord_base import ChordBase

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
    assert chord.quality == ChordQualityType.MAJOR

def test_chord_validation() -> None:
    root = Note(name='C', octave=4)
    # Invalid chord - empty notes list
    with pytest.raises(ValueError):
        Chord(root=root, notes=[], quality=ChordQualityType.MAJOR)

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
    assert chord.notes[0].name == 'E'
    logging.debug(f"Final notes list: {[note.name for note in chord.notes]}")
    logging.debug("Finished test_chord_inversion")

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
    assert chord.quality == ChordQualityType.MAJOR