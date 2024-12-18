from enum import Enum

class AccidentalType(Enum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

class ChordQualityType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT_7 = "dominant7"
    MAJOR_7 = "major7"
    MINOR_7 = "minor7"
    DIMINISHED_7 = "diminished7"
    HALF_DIMINISHED_7 = "half_diminished7"
    AUGMENTED_7 = "augmented7"
    MAJOR_9 = "major9"
    MINOR_9 = "minor9"
    DOMINANT_9 = "dominant9"
    MAJOR_11 = "major11"
    MINOR_11 = "minor11"
    SUS2 = "sus2"
    SUS4 = "sus4"
    SEVEN_SUS4 = "seven_sus4"