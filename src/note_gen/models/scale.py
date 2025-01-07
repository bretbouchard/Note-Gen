from typing import List
from src.note_gen.models.note import Note
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ScaleType(Enum):
    """Enum representing different scale types."""
    MAJOR = "major"
    NATURAL_MINOR = "natural_minor"
    HARMONIC_MINOR = "harmonic_minor"
    MELODIC_MINOR = "melodic_minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    LOCRIAN = "locrian"
    PENTATONIC_MAJOR = "pentatonic_major"
    PENTATONIC_MINOR = "pentatonic_minor"
    BLUES = "blues"
    CHROMATIC = "chromatic"
    WHOLE_TONE = "whole_tone"
    MINOR_PENTATONIC = "minor_pentatonic"
    MAJOR_PENTATONIC = "major_pentatonic"
    NEAPOLITAN_MAJOR = "neapolitan_major"
    NEAPOLITAN_MINOR = "neapolitan_minor"
    HARMONIC_MAJOR = "harmonic_major"
    MELODIC_MAJOR = "melodic_major"
    DOUBLE_HARMONIC_MAJOR = "double_harmonic_major"
    BYZANTINE = "byzantine"
    HUNGARIAN_MINOR = "hungarian_minor"
    HUNGARIAN_MAJOR = "hungarian_major"
    ROMANIAN_MINOR = "romanian_minor"
    ULTRAPHRYGIAN = "ultraphrygian"
    YONANAI = "yonanai"
    JAPANESE = "japanese"
    INDIAN = "indian"
    CHINESE = "chinese"
    BALINESE = "balinese"
    PERSIAN = "persian"
    HARMONIC_MINOR_VARIANT = "harmonic_minor_variant"
    MELODIC_MINOR_VARIANT = "melodic_minor_variant"
    HARMONIC_MAJOR_VARIANT = "harmonic_major_variant"
    MELODIC_MAJOR_VARIANT = "melodic_major_variant"

    def get_intervals(self) -> List[int]:
        """Get the intervals for this scale type."""
        intervals_map = {
            ScaleType.MAJOR: [2, 2, 1, 2, 2, 2, 1],
            ScaleType.NATURAL_MINOR: [2, 1, 2, 2, 1, 2, 2],
            ScaleType.HARMONIC_MINOR: [2, 1, 2, 2, 1, 3, 1],
            ScaleType.MELODIC_MINOR: [2, 1, 2, 2, 2, 2, 1],
            ScaleType.DORIAN: [2, 1, 2, 2, 2, 1, 2],
            ScaleType.PHRYGIAN: [1, 2, 2, 2, 1, 2, 2],
            ScaleType.LYDIAN: [2, 2, 2, 1, 2, 2, 1],
            ScaleType.MIXOLYDIAN: [2, 2, 1, 2, 2, 1, 2],
            ScaleType.LOCRIAN: [1, 2, 2, 1, 2, 2, 2],
            ScaleType.PENTATONIC_MAJOR: [2, 2, 3, 2, 3],
            ScaleType.PENTATONIC_MINOR: [3, 2, 2, 3, 2],
            ScaleType.BLUES: [3, 2, 1, 1, 3, 2],
            ScaleType.CHROMATIC: [1]*12,
            ScaleType.WHOLE_TONE: [2]*6,
            ScaleType.MINOR_PENTATONIC: [3, 2, 2, 3, 2],
            ScaleType.MAJOR_PENTATONIC: [2, 2, 3, 2, 3],
            ScaleType.NEAPOLITAN_MAJOR: [1, 2, 2, 2, 2, 2, 1],
            ScaleType.NEAPOLITAN_MINOR: [1, 2, 2, 2, 1, 2, 2],
            ScaleType.HARMONIC_MAJOR: [2, 2, 1, 2, 1, 3, 1],
            ScaleType.MELODIC_MAJOR: [2, 2, 1, 2, 2, 2, 1],
            ScaleType.DOUBLE_HARMONIC_MAJOR: [1, 3, 1, 2, 1, 3, 1],
            ScaleType.BYZANTINE: [1, 3, 1, 2, 1, 3, 1],
            ScaleType.HUNGARIAN_MINOR: [2, 1, 3, 1, 1, 3, 1],
            ScaleType.HUNGARIAN_MAJOR: [3, 1, 1, 2, 1, 3, 1],
            ScaleType.ROMANIAN_MINOR: [2, 1, 3, 1, 2, 1, 2],
            ScaleType.ULTRAPHRYGIAN: [1, 4, 1, 2, 1, 2, 1],
            ScaleType.YONANAI: [2, 2, 1, 4, 1, 2],
            ScaleType.JAPANESE: [1, 4, 1, 4, 2],
            ScaleType.INDIAN: [1, 2, 2, 2, 1, 2, 2],
            ScaleType.CHINESE: [4, 2, 1, 4, 1],
            ScaleType.BALINESE: [1, 2, 1, 4, 1, 3],
            ScaleType.PERSIAN: [1, 3, 1, 1, 2, 3, 1],
            ScaleType.HARMONIC_MINOR_VARIANT: [2, 1, 2, 2, 1, 4, 1],
            ScaleType.MELODIC_MINOR_VARIANT: [2, 1, 2, 2, 2, 2, 1],
            ScaleType.HARMONIC_MAJOR_VARIANT: [2, 2, 1, 2, 1, 4, 1],
            ScaleType.MELODIC_MAJOR_VARIANT: [2, 2, 1, 2, 2, 2, 1],
        }
        logger.debug(f"Getting intervals for scale type: {self.name}")
        return intervals_map[self]

    def validate_degree(self, degree: int) -> bool:
        """Validate if a scale degree is valid for this scale type."""
        intervals = self.get_intervals()
        if degree < 1 or degree > len(intervals):
            raise ValueError(
                f"Invalid scale degree: {degree}. Must be between 1 and {len(intervals)}."
            )
        return True

    @property
    def degree_count(self) -> int:
        """Get the number of degrees in this scale type."""
        return len(self.get_intervals())

    @property
    def is_diatonic(self) -> bool:
        """Check if the scale is diatonic (7 notes)."""
        return self.degree_count == 7

    def get_scale_degrees(self) -> List[int]:
        """Get the scale degrees for this scale type."""
        return list(range(1, len(self.get_intervals()) + 1))


class Scale:
    """A scale with a root note and a ScaleType."""
    def __init__(self, root: Note, scale_type: ScaleType):
        self.root = root
        self.scale_type = scale_type
        self.intervals = scale_type.get_intervals()

    def get_notes(self) -> List[Note]:
        notes = [self.root]
        current_midi = self.root.midi_number
        for interval in self.intervals:
            current_midi += interval
            notes.append(Note.from_midi(current_midi))
        return notes

    def get_scale_degree(self, degree: int) -> Note:
        if not (1 <= degree <= len(self.intervals)):
            raise ValueError(f"Scale degree must be between 1 and {len(self.intervals)}.")
        
        return self.get_notes()[degree - 1]
    
    def get_degree_of_note(self, note: Note) -> int:
        """Return which scale degree (1-based) this note is in the current scale.
        Raise an error if it's not found or doesn't align exactly with a scale tone."""
        notes_in_scale = self.get_notes()  # returns List[Note]
        for i, scale_note in enumerate(notes_in_scale, start=1):
            # Compare MIDI numbers or names
            if scale_note.midi_number == note.midi_number:
                return i
        raise ValueError(f"{note} not found in {self.scale_type} scale with root {self.root}")