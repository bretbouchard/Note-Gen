import pytest
import logging
from src.note_gen.models.note import Note
from src.note_gen.models.musical_elements import Chord, ChordQualityType
from pydantic import Field, ValidationError


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_create_chord() -> None:
    logger.debug("Starting test_create_chord")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
    logger.debug(f"Created chord: {chord}")
    assert chord.root.note_name == "C"
    assert chord.quality == ChordQualityType.MAJOR

def test_invalid_quality() -> None:
    logger.debug("Starting test_invalid_quality")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    invalid_quality = "invalid_quality"
    
    with pytest.raises(ValueError) as exc_info:
        Chord(root=root_note, quality=invalid_quality)
    
    assert "Invalid quality: 'invalid_quality'" in str(exc_info.value)

 
def test_invalid_root() -> None:
    class InvalidNote(Note):
        def __init__(self, note_name: str = "C4", octave: int = 4, duration: float = 1.0, velocity: int = 100):
            super().__init__(note_name=note_name, octave=octave, duration=duration, velocity=velocity)

    # Now we match the *actual* Pydantic error message about 'Unrecognized note name'
    with pytest.raises(ValidationError, match="Invalid note name: InvalidNoteName"):  
        Chord.from_quality(root=InvalidNote(note_name="InvalidNoteName", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)

def test_chord_diminished_quality() -> None:
    logger.debug("Starting test_chord_diminished_quality")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    logger.debug(f"Created root note: {root_note}")
    
    chord = Chord.from_quality(root=root_note, quality=ChordQualityType.DIMINISHED)
    logger.debug(f"Created chord: {chord}")
    logger.debug(f"Chord notes: {chord.notes}")
    
    assert chord.quality == ChordQualityType.DIMINISHED
    assert len(chord.notes) == 3  # Diminished chord should have 3 notes
    assert chord.notes[0].note_name == "C"
    assert chord.notes[1].note_name == "Eb"
    assert chord.notes[2].note_name == "Gb"

def test_chord_inversion() -> None:
    logger.debug("Starting test_chord_inversion")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    logger.debug(f"Created root note: {root_note}")
    
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR, inversion=1)
    logger.debug(f"Created chord: {chord}")
    logger.debug(f"Chord notes: {chord.notes}")
    
    assert len(chord.notes) == 3  # Major chord should have 3 notes
    assert chord.notes[0].note_name == "E"
    assert chord.notes[1].note_name == "G"
    assert chord.notes[2].note_name == "C"


def test_chord_invalid_inversion() -> None:
    logger.debug("Starting test_chord_invalid_inversion")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    
    with pytest.raises(ValueError) as exc_info:
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR, inversion=-1)
    
    assert "Inversion cannot be negative" in str(exc_info.value)




def test_chord_major_with_seventh() -> None:
    logger.debug("Starting test_chord_major_with_seventh")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    logger.debug(f"Created root note: {root_note}")
    
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR_7)
    logger.debug(f"Created chord: {chord}")
    logger.debug(f"Chord notes: {chord.notes}")
    
    assert len(chord.notes) == 4  # Major 7th chord should have 4 notes
    assert chord.notes[0].note_name == "C"
    assert chord.notes[1].note_name == "E"
    assert chord.notes[2].note_name == "G"
    assert chord.notes[3].note_name == "B"


def test_chord_transposition() -> None:
    """Test that a chord can be transposed."""
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.MINOR)
    transposed_chord = chord.transpose(2)  # Transpose up by 2 semitones
    assert transposed_chord.root.note_name == "D"