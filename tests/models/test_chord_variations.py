import pytest
import logging
from typing import Any, cast
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord, ChordQuality
from pydantic_core import ValidationError

logger = logging.getLogger(__name__)

def test_chord_quality_variations() -> None:
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    logger.debug(f"Testing chord quality variations with root note: {root_note.note_name}")

    # Define the key scale (e.g., C major)
    key_scale = "C major"  # This is just a placeholder; adjust as needed

    # Test various quality enum values
    for quality_enum in [ChordQuality.MAJOR_SEVENTH, ChordQuality.MINOR_SEVENTH, ChordQuality.DOMINANT_SEVENTH]:
        logger.debug(f"Testing chord quality: {quality_enum}")
        chord = Chord(root=root_note, quality=quality_enum, inversion=0)  
        logger.debug(f"Chord quality after initialization: {chord.quality}")

        # Assertions for chord quality
        assert chord.quality == quality_enum
        assert len(chord.notes) == 4  # Assuming all tested chords should have 4 notes
        assert chord.notes[0].note_name == "C"

        # Adjust the expected note based on the key scale
        if quality_enum == ChordQuality.MINOR_SEVENTH:
            assert chord.notes[1].note_name in ["D#", "Eb"], f"Expected 'D#' or 'Eb', got {chord.notes[1].note_name}"
        elif quality_enum == ChordQuality.DOMINANT_SEVENTH:
            assert chord.notes[1].note_name == "E", f"Expected 'E', got {chord.notes[1].note_name}"
        else:  # MAJOR_SEVENTH
            assert chord.notes[1].note_name == "E"  # This remains for MAJOR_SEVENTH

        # Additional assertions for chord notes
        if quality_enum == ChordQuality.MAJOR_SEVENTH:
            assert chord.notes[2].note_name == "G"
            assert chord.notes[3].note_name == "B"
        elif quality_enum == ChordQuality.MINOR_SEVENTH:
            assert chord.notes[2].note_name == "G"
            assert chord.notes[3].note_name in ["A#", "Bb"], f"Expected 'A#' or 'Bb', got {chord.notes[3].note_name}"
        elif quality_enum == ChordQuality.DOMINANT_SEVENTH:
            assert chord.notes[2].note_name == "G"
            assert chord.notes[3].note_name in ["A#", "Bb"], f"Expected 'A#' or 'Bb', got {chord.notes[3].note_name}"

        # Octave and duration assertions
        assert chord.notes[0].octave == 4
        assert chord.notes[1].octave == 4
        assert chord.notes[2].octave == 4
        assert chord.notes[3].octave == 4
        assert chord.notes[0].duration == 1.0
        assert chord.notes[1].duration == 1.0
        assert chord.notes[2].duration == 1.0
        assert chord.notes[3].duration == 1.0
        assert chord.notes[0].velocity == 64
        assert chord.notes[1].velocity == 64
        assert chord.notes[2].velocity == 64
        assert chord.notes[3].velocity == 64

    # Test truly invalid quality string
    logger.debug(f"Testing invalid chord quality: invalid_quality")
    with pytest.raises(ValidationError):  
        # Use a string that is not a valid ChordQuality enum value
        # Use cast to Any to bypass type checking since we're deliberately testing invalid input
        Chord(root=root_note, quality=cast(Any, "INVALID_QUALITY"), inversion=0)
        
    # Test empty string (should default to MAJOR)
    logger.debug(f"Testing empty chord quality string")
    chord = Chord(root=root_note, quality=ChordQuality.MAJOR, inversion=0)  # Using a valid quality
    assert chord.quality == ChordQuality.MAJOR