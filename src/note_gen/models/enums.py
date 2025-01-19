from typing import List, Optional
from enum import Enum, StrEnum

class AccidentalType(StrEnum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"



class ChordQualityType(StrEnum):
    """Enum for chord quality types in UPPERCASE so `ChordQualityType[quality.upper()]` works."""

    # Basic triads
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    
    DOMINANT_7 = "7"
    DOMINANT = "7"  # Alias for DOMINANT_7
    MAJOR_7 = "maj7"
    MINOR_7 = "m7"
    DIMINISHED_7 = "dim7"
    HALF_DIMINISHED_7 = "m7b5"
    AUGMENTED_7 = "aug7"
    MAJOR_9 = "maj9"
    MINOR_9 = "m9"
    DOMINANT_9 = "9"
    MAJOR_11 = "maj11"
    MINOR_11 = "m11"
    DOMINANT_11 = "11"
    SUS2 = "sus2"
    SUS4 = "sus4"
    SEVEN_SUS4 = "7sus4"
    FLAT_5 = "b5"
    FLAT_7 = "b7"
    SHARP_5 = "#5"
    SHARP_7 = "#7"
    
    def _missing_(cls, value: object) -> Optional['ChordQualityType']:
        """Override to provide a default behavior for missing values."""
        return None

    def get_intervals(self) -> List[int]:
        """Get the semitone intervals for this chord quality."""
        intervals = {
            # Basic triads
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            
            # Seventh chords
            ChordQualityType.DOMINANT_7: [0, 4, 7, 10],
            ChordQualityType.DOMINANT: [0, 4, 7, 10],
            ChordQualityType.MAJOR_7: [0, 4, 7, 11],
            ChordQualityType.MINOR_7: [0, 3, 7, 10],
            ChordQualityType.DIMINISHED_7: [0, 3, 6, 9],
            ChordQualityType.HALF_DIMINISHED_7: [0, 3, 6, 10],
            ChordQualityType.AUGMENTED_7: [0, 4, 8, 10],
            
            # Extended chords
            ChordQualityType.MAJOR_9: [0, 4, 7, 11, 14],
            ChordQualityType.MINOR_9: [0, 3, 7, 10, 14],
            ChordQualityType.DOMINANT_9: [0, 4, 7, 10, 14],
            ChordQualityType.MAJOR_11: [0, 4, 7, 11, 14, 17],
            ChordQualityType.MINOR_11: [0, 3, 7, 10, 14, 17],
            ChordQualityType.DOMINANT_11: [0, 4, 7, 10, 14, 17],
            
            # Suspended chords
            ChordQualityType.SUS2: [0, 2, 7],
            ChordQualityType.SUS4: [0, 5, 7],
            ChordQualityType.SEVEN_SUS4: [0, 5, 7, 10],
            
            # Altered chords
            ChordQualityType.FLAT_5: [0, 4, 6],
            ChordQualityType.FLAT_7: [0, 4, 7, 9],
            ChordQualityType.SHARP_5: [0, 4, 8],
            ChordQualityType.SHARP_7: [0, 4, 7, 11],
        }
        return intervals.get(self, [0, 4, 7])  # Default to major triad if not found


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