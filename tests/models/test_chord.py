import logging
import pytest
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.enums import ChordQualityType
from pydantic import ValidationError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_create_chord() -> None:
    root_note = Note.from_name("C4")
    chord = Chord.from_quality(root=root_note, quality=ChordQualityType.MAJOR)
    assert chord.root.note_name == "C"
    assert chord.quality == ChordQualityType.MAJOR


def test_invalid_quality() -> None:
    root_note = Note.from_name("C4")
    invalid_quality = "invalid_quality"
    logger.debug(f"Sending root_note={root_note}, quality={invalid_quality}")

    with pytest.raises(ValidationError):
        Chord(root=root_note, quality=invalid_quality)

def test_invalid_root() -> None:
    with pytest.raises(ValueError, match="Root must be a valid Note instance."):
        Chord.from_quality(root=None, quality=ChordQualityType.MAJOR)


def test_chord_diminished_quality() -> None:
    root_note = Note.from_name("C4")
    chord = Chord.from_quality(root=root_note, quality=ChordQualityType.DIMINISHED)
    assert chord.quality == ChordQualityType.DIMINISHED
    assert chord.notes[0].note_name == "C"
    assert chord.notes[1].note_name in {"Eb", "D#"}
    assert chord.notes[2].note_name in {"Gb", "F#"}


def test_chord_inversion() -> None:
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR, inversion=1)
    assert chord.notes[0].note_name == "E"
    assert chord.notes[1].note_name == "G"
    assert chord.notes[2].note_name == "C"

def test_chord_invalid_inversion() -> None:
    """Test that an invalid inversion raises an error."""
    root_note = Note.from_name("C4")
    with pytest.raises(ValueError, match=r"Input should be greater than or equal to 0"):
        Chord(root=root_note, quality=ChordQualityType.MAJOR, inversion=-1)

def test_chord_major_with_seventh() -> None:
    """Test that a major chord with a seventh is constructed correctly."""
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR_7)
    assert chord.quality == ChordQualityType.MAJOR_7
    assert chord.notes[3].note_name == "B"  # Check the 7th

def test_chord_transposition() -> None:
    """Test that a chord can be transposed."""
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.MINOR)
    transposed_chord = chord.transpose(2)  # Transpose up by 2 semitones
    assert transposed_chord.root.note_name == "D"