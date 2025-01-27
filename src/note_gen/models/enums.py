from typing import List, Optional
from enum import Enum, StrEnum

class AccidentalType(StrEnum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

class ChordQualityType(Enum):
    """Enum for chord quality types."""
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT_7 = "dominant_7"
    MAJOR_7 = "major_7"
    MINOR_7 = "minor_7"
    DIMINISHED_7 = "diminished_7"
    HALF_DIMINISHED_7 = "half_diminished_7"
    AUGMENTED_7 = "augmented_7"
    MAJOR_9 = "major_9"
    MINOR_9 = "minor_9"
    DOMINANT_9 = "dominant_9"
    MAJOR_11 = "major_11"
    MINOR_11 = "minor_11"
    DOMINANT_11 = "dominant_11"
    SUS2 = "sus2"
    SUS4 = "sus4"
    SEVEN_SUS4 = "seven_sus4"
    FLAT_5 = "flat_5"
    FLAT_7 = "flat_7"
    SHARP_5 = "sharp_5"
    SHARP_7 = "sharp_7"
    DOMINANT = "dominant"

    @classmethod
    def get_scale_intervals(cls, quality_type: 'ChordQualityType') -> List[int]:
        intervals = {
            cls.MAJOR: [0, 4, 7],
            cls.MINOR: [0, 3, 7],
            cls.DIMINISHED: [0, 3, 6],
            cls.AUGMENTED: [0, 4, 8],
            cls.DOMINANT_7: [0, 4, 7, 10],
            cls.DOMINANT: [0, 4, 7, 10],
            cls.MAJOR_7: [0, 4, 7, 11],
            cls.MINOR_7: [0, 3, 7, 10],
            cls.DIMINISHED_7: [0, 3, 6, 9],
            cls.HALF_DIMINISHED_7: [0, 3, 6, 10],
            cls.AUGMENTED_7: [0, 4, 8, 10],
            cls.MAJOR_9: [0, 4, 7, 11, 14],
            cls.MINOR_9: [0, 3, 7, 10, 14],
            cls.DOMINANT_9: [0, 4, 7, 10, 14],
            cls.MAJOR_11: [0, 4, 7, 11, 14, 17],
            cls.MINOR_11: [0, 3, 7, 10, 14, 17],
            cls.DOMINANT_11: [0, 4, 7, 10, 14, 17],
            cls.SUS2: [0, 2, 7],
            cls.SUS4: [0, 5, 7],
            cls.SEVEN_SUS4: [0, 5, 7, 10],
            cls.FLAT_5: [0, 4, 6],
            cls.FLAT_7: [0, 4, 7, 9],
            cls.SHARP_5: [0, 4, 8],
            cls.SHARP_7: [0, 4, 7, 11],
        }
        return intervals.get(quality_type, None)

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQualityType':
        if not quality_str:
            raise ValueError("Quality string cannot be empty")
        try:
            return cls[quality_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid quality string: {quality_str}")

    def __str__(self):
        if self == ChordQualityType.DOMINANT_7:
            return "7"
        if self == ChordQualityType.MAJOR_7:
            return "maj7"
        if self == ChordQualityType.MINOR_7:
            return "m7"
        return self.value


class ScaleDegree(Enum):
    TONIC = 1
    SUPERTONIC = 2
    MEDIANT = 3
    SUBDOMINANT = 4
    DOMINANT = 5
    SUBMEDIANT = 6
    LEADING_TONE = 7


class ScaleType(Enum):
    """Enum representing different scale types."""
    MINOR = "minor"
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