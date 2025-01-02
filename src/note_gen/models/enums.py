from enum import Enum, StrEnum

class AccidentalType(StrEnum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

class ChordQualityType(StrEnum):
    """Enum for chord quality types."""
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT = "dominant"
    DOMINANT_7 = "dominant7"
    MAJOR_7 = "major7"
    MINOR_7 = "minor7"
    DIMINISHED_7 = "diminished7"
    HALF_DIMINISHED_7 = "half_diminished7"
    AUGMENTED_7 = "augmented7"
    MAJOR_SEVENTH = "major7"  # Alias for MAJOR_7
    MINOR_SEVENTH = "minor7"  # Alias for MINOR_7
    DIMINISHED_SEVENTH = "diminished7"  # Alias for DIMINISHED_7
    MAJOR_9 = "major9"
    MINOR_9 = "minor9"
    DOMINANT_9 = "dominant9"
    MAJOR_11 = "major11"
    MINOR_11 = "minor11"
    SUS2 = "sus2"
    SUS4 = "sus4"

    @property
    def quality_type(self) -> "ChordQualityType":
        """Get the chord quality type."""
        return self
