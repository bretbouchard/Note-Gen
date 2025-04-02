"""Core accessors for musical elements."""
from typing import List, Tuple
from src.note_gen.core.constants import (
    NOTES,
    NOTE_TO_SEMITONE,
    SCALE_INTERVALS
)
from src.note_gen.core.enums import ScaleType

class NoteAccessor:
    """Accessor for note-related operations."""

    @staticmethod
    def get_note_semitone(note_name: str) -> int:
        """Get semitone value for a note name."""
        semitone = NOTE_TO_SEMITONE.get(note_name)
        if semitone is None:
            raise ValueError(f"Invalid note name: {note_name}")
        return int(semitone)

    @staticmethod
    def get_notes() -> List[str]:
        """Get list of valid note names."""
        return list(NOTES)

    @staticmethod
    def validate_note_name(note_name: str) -> bool:
        """Validate if a note name is valid."""
        return note_name in NOTES

    @staticmethod
    def normalize_note_name(note_name: str) -> str:
        """
        Normalize a note name to standard format.

        Args:
            note_name: Note name to normalize (e.g., 'C', 'C#', 'Db')

        Returns:
            Normalized note name

        Raises:
            ValueError: If note name is invalid
        """
        if not note_name:
            raise ValueError("Note name cannot be empty")

        # Remove any whitespace and capitalize
        normalized = note_name.strip().upper()

        # Check if the normalized note is in NOTES or is a flat equivalent
        if normalized not in NOTES and normalized not in NOTE_TO_SEMITONE:
            raise ValueError(f"Invalid note name: {note_name}")

        return normalized

    @staticmethod
    def get_midi_number(note_name: str, octave: int) -> int:
        """
        Convert note name and octave to MIDI number.

        Args:
            note_name: Note name (e.g., 'C', 'C#')
            octave: Octave number

        Returns:
            MIDI note number

        Raises:
            ValueError: If note name or octave is invalid
        """
        normalized_note = NoteAccessor.normalize_note_name(note_name)
        semitone = NoteAccessor.get_note_semitone(normalized_note)

        # Type checking is handled by the type annotation
        # This is just a runtime check for extra safety
        if not isinstance(octave, int):
            raise ValueError("Octave must be an integer")

        if not (0 <= octave <= 8):
            raise ValueError("Octave must be between 0 and 8")

        # MIDI note number calculation: (octave + 1) * 12 + semitone
        midi_number = (octave + 1) * 12 + semitone

        return midi_number

class ScaleDegreeAccessor:
    """Accessor for scale degree operations."""

    @staticmethod
    def get_scale_degree(degree: int, scale_type: ScaleType) -> int:
        """Get semitone value for a scale degree in a given scale."""
        intervals = SCALE_INTERVALS[scale_type.value]
        if 1 <= degree <= len(intervals):
            return int(intervals[degree - 1])
        return 0

    @staticmethod
    def validate_degree(degree: int, scale_type: ScaleType) -> bool:
        """Validate if a scale degree is valid for the given scale type."""
        return 1 <= degree <= len(SCALE_INTERVALS[scale_type.value])

class ScaleAccessor:
    """Accessor for scale-related operations."""

    @staticmethod
    def get_scale_intervals(scale_type: ScaleType) -> Tuple[int, ...]:
        """Get intervals for a scale type."""
        intervals = SCALE_INTERVALS[scale_type.value]
        # Ensure the return type is correct
        return tuple(int(i) for i in intervals)

    # Remove  as it belongs in Scale/ScaleInfo classes

class MusicTheoryAccessor:
    """Accessor for general music theory operations."""

    @staticmethod
    def get_interval(note1: str, note2: str) -> int:
        """Get interval between two notes in semitones."""
        semitone1 = NoteAccessor.get_note_semitone(note1)
        semitone2 = NoteAccessor.get_note_semitone(note2)
        return (semitone2 - semitone1) % 12

    @staticmethod
    def is_consonant_interval(interval: int) -> bool:
        """Check if an interval is consonant."""
        consonant_intervals = {0, 3, 4, 7, 8, 9}  # Unison, thirds, perfect fourth/fifth, sixths
        return interval in consonant_intervals
