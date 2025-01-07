from typing import List 
from enum import Enum, StrEnum

class AccidentalType(StrEnum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"



class ChordQualityType(str, Enum):
    """Enum for chord quality types in UPPERCASE so `ChordQualityType[quality.upper()]` works."""

    MAJOR = "major"                # "major".upper() -> "MAJOR" => ChordQualityType["MAJOR"]
    MINOR = "minor"                # "minor".upper() -> "MINOR" => ChordQualityType["MINOR"]
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT = "dominant"
    DOMINANT_7 = "dominant7"       # "dominant7".upper() -> "DOMINANT7" => KeyError unless you rename to DOMINANT7 or handle underscores
    MAJOR_7 = "major7"             # "major7".upper() -> "MAJOR7" => we must name the member "MAJOR7" if we want bracket-lookup to work
    MINOR_7 = "minor7"
    DIMINISHED_7 = "diminished7"
    HALF_DIMINISHED_7 = "half_diminished7"
    AUGMENTED_7 = "augmented7"
    MAJOR_SEVENTH = "major7"
    MINOR_SEVENTH = "minor7"
    DIMINISHED_SEVENTH = "diminished7"
    MAJOR_9 = "major9"
    MINOR_9 = "minor9"
    DOMINANT_9 = "dominant9"
    MAJOR_11 = "major11"
    MINOR_11 = "minor11"
    SUS2 = "sus2"
    SUS4 = "sus4"
    HALF_DIMINISHED = "half_diminished"
    AUGMENTED_SEVENTH = "augmented_seventh"
    SEVEN_SUS4 = "seven_sus4"
    AUGMENTED_DIMINISHED = "augmented_diminished"
    AUGMENTED_DIMINISHED_7 = "augmented_diminished_7"

    def get_intervals(self) -> List[int]:
        return {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
        }[self]


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