import pytest
import logging
from pydantic import ValidationError
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.musical_elements import ChordQualityType

# Configure logging to output to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def are_enharmonic(note1: str, note2: str) -> bool:
    """Check if two note names are enharmonically equivalent."""
    enharmonic_pairs = {
        'C#': 'Db',
        'D#': 'Eb',
        'F#': 'Gb',
        'G#': 'Ab',
        'A#': 'Bb',
        # Add the reverse mappings
        'Db': 'C#',
        'Eb': 'D#',
        'Gb': 'F#',
        'Ab': 'G#',
        'Bb': 'A#'
    }
    return note1 == note2 or note1 == enharmonic_pairs.get(note2) or note2 == enharmonic_pairs.get(note1)


def test_create_chord() -> None:
    logger.debug("Starting test_create_chord")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    logger.debug(f"Created root note: {root_note.note_name}, octave: {root_note.octave}, duration: {root_note.duration}, velocity: {root_note.velocity}")
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
    logger.debug(f"Created chord: {chord}")
    logger.debug(f"Chord root note name: {chord.root.note_name}, quality: {chord.quality}")
    assert chord.root.note_name == "C"
    assert chord.quality == ChordQualityType.MAJOR


def test_chord_initialization() -> None:
    chord = Chord(root=Note(note_name='C', octave=4), quality=ChordQualityType.MAJOR)
    logger.debug(f"Chord initialized with quality: {chord.quality}")
    logger.debug(f"Chord notes: {[note.note_name for note in chord.notes]}")
    assert chord.quality == ChordQualityType.MAJOR  # Ensure quality is set correctly


def test_chord_diminished_quality() -> None:
    print("Starting test_chord_diminished_quality")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    chord = Chord.from_quality(root=root_note, quality='diminished')  # Pass as string

    # Assert quality
    assert chord.quality == ChordQualityType.DIMINISHED
    # Assert count of notes
    assert len(chord.notes) == 3  # Diminished chord should have 3 notes
    # Assert specific properties of the notes
    assert chord.notes[0].note_name == "C"
    assert are_enharmonic(chord.notes[1].note_name, "Eb")  # Accept both Eb and D#
    assert are_enharmonic(chord.notes[2].note_name, "Gb")  # Accept both Gb and F#


def test_chord_inversion() -> None:
    print("Starting test_chord_inversion")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    chord = Chord(root=root_note, quality=ChordQualityType.MAJOR, inversion=1)
    print(f"Chord notes before assertion: {chord.notes}")
    logger.debug(f"Chord inversion: {chord.inversion}")
    logger.debug(f"Chord notes after inversion: {[note.note_name for note in chord.notes]}")
    assert len(chord.notes) == 3  # Major chord should have 3 notes
    assert chord.notes[0].note_name == "E"  # Expecting the first note to be E
    assert chord.notes[1].note_name == "G"  # Expecting the second note to be G
    assert chord.notes[2].note_name == "C"  # Expecting the third note to be C


def test_chord_invalid_inversion() -> None:
    print("Starting test_chord_invalid_inversion")
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    with pytest.raises(ValueError) as exc_info:
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR, inversion=-1)
    assert "Inversion cannot be negative" in str(exc_info.value)


def test_chord_MAJOR_with_seventh() -> None:
    print("Starting test_chord_MAJOR_with_seventh")
    root_note = Note.from_name("C4", duration=1.0, velocity=100)  # Change velocity to 100
    chord = Chord(root=root_note, quality='maj7')  # Pass as string

    logger.debug(f"Chord created: {chord}")
    logger.debug(f"Chord quality: {chord.quality}")
    logger.debug(f"Chord notes before assertion: {chord.notes}")

    # Assert quality
    assert chord.quality == ChordQualityType.MAJOR7  # Changed from MAJOR_7
    assert len(chord.notes) == 4  # Major 7 chord should have 4 notes
    assert chord.notes[0].note_name == "C"
    assert chord.notes[1].note_name == "E"
    assert chord.notes[2].note_name == "G"
    assert chord.notes[3].note_name == "B"
    assert chord.notes[0].octave == 4  # Assert octave
    assert chord.notes[1].octave == 4  # Assert octave
    assert chord.notes[2].octave == 4  # Assert octave
    assert chord.notes[3].octave == 4  # Assert octave
    assert chord.notes[0].duration == 1.0  # Assert duration
    assert chord.notes[1].duration == 1.0  # Assert duration
    assert chord.notes[2].duration == 1.0  # Assert duration
    assert chord.notes[3].duration == 1.0  # Assert duration
    assert chord.notes[0].velocity == 100  # Assert velocity
    assert chord.notes[1].velocity == 100  # Assert velocity
    assert chord.notes[2].velocity == 100  # Assert velocity
    assert chord.notes[3].velocity == 100  # Assert velocity


def test_chord_transposition() -> None:
    print("Starting test_chord_transposition")
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.MINOR)
    transposed_chord = chord.transpose(2)  # Transpose up by 2 semitones
    logger.debug(f"Transposed chord: {transposed_chord}")
    logger.debug(f"Transposed chord notes: {[note.note_name for note in transposed_chord.notes]}")
    assert transposed_chord.root.note_name == "D"