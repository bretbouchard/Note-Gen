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
    DOMINANT = "dominant"
    DOMINANT_7 = "dominant7"
    DIMINISHED_7 = "diminished7"
    DOMINANT_SEVENTH = "dominant_seventh"
    MAJOR_SEVENTH = "major_seventh"
    MINOR_SEVENTH = "minor_seventh"
    MAJOR_7 = "major_seventh"
    MINOR_7 = "minor_seventh"
    HALF_DIMINISHED = "half_diminished"
    HALF_DIMINISHED_7 = "half_diminished_seventh"
    AUGMENTED_7 = "augmented_seventh"
    AUGMENTED_SEVENTH = "augmented_seventh"
    DIMINISHED_SEVENTH = "diminished_seventh"
    MAJOR_9 = "major9"
    MINOR_9 = "minor9"
    DOMINANT_9 = "dominant9"
    MAJOR_11 = "major11"
    MINOR_11 = "minor11"
    SUS2 = "sus2"
    SUS4 = "sus4"
    SEVEN_SUS4 = "seven_sus4"
