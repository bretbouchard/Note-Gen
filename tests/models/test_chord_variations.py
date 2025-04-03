import logging
from note_gen.models.note import Note
from note_gen.models.chord import Chord
from note_gen.core.enums import ChordQuality

logger = logging.getLogger(__name__)

def test_chord_quality_variations() -> None:
    """Test different chord qualities and their note generation."""
    root_note = "C"  # Use string instead of Note object
    logger.debug(f"Testing chord quality variations with root note: {root_note}")

    # Define the key scale (e.g., C major)
    key_scale = "C major"  # This is just a placeholder; adjust as needed

    # Test various quality enum values
    for quality_enum in [ChordQuality.MAJOR_SEVENTH, ChordQuality.MINOR_SEVENTH, ChordQuality.DOMINANT_SEVENTH]:
        logger.debug(f"Testing chord quality: {quality_enum}")
        chord = Chord(root=root_note, quality=quality_enum)
        
        # Get the notes and verify the chord structure
        notes = chord.get_notes()
        
        # Verify number of notes matches the chord quality
        expected_notes = len(Chord.QUALITY_INTERVALS[quality_enum])
        assert len(notes) == expected_notes, f"Expected {expected_notes} notes for {quality_enum}, got {len(notes)}"
        
        # Verify the intervals are correct
        intervals = Chord.QUALITY_INTERVALS[quality_enum]
        base_midi = notes[0].midi_number
        for i, note in enumerate(notes):
            expected_midi = base_midi + intervals[i]
            assert note.midi_number == expected_midi, \
                f"Note {i} in {quality_enum} chord should be {expected_midi} semitones above root, got {note.midi_number - base_midi}"
