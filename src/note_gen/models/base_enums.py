from enum import Enum, StrEnum
from typing import List

class AccidentalType(StrEnum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

class ChordQuality(str, Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    DIMINISHED = "DIMINISHED"
    AUGMENTED = "AUGMENTED"
    DOMINANT = "DOMINANT"
    DOMINANT_SEVENTH = "DOMINANT7"
    MAJOR_SEVENTH = "MAJ7"
    MINOR_SEVENTH = "MIN7"
    HALF_DIMINISHED = "HALF_DIMINISHED"
    HALF_DIMINISHED_SEVENTH = "HALF_DIMINISHED7"
    DIMINISHED_SEVENTH = "DIM7"
    MINOR_NINTH = "MIN9"
    MAJOR_NINTH = "MAJ9"
    FULL_DIMINISHED = "FULL_DIMINISHED"

    @classmethod
    def from_string(cls, value: str) -> 'ChordQuality':
        """Convert string representation to ChordQuality."""
        value = value.upper().strip()
        mapping = {
            "M": "MAJOR",
            "MAJ": "MAJOR",
            "MIN": "MINOR",
            "m": "MINOR",
            "DIM": "DIMINISHED",
            "°": "DIMINISHED",
            "AUG": "AUGMENTED",
            "+": "AUGMENTED",
            "DOM": "DOMINANT",
            "DOM7": "DOMINANT7",
            "MAJ7": "MAJOR_SEVENTH",
            "MIN7": "MINOR_SEVENTH",
            "m7": "MINOR_SEVENTH",
            "HALF_DIM": "HALF_DIMINISHED",
            "ø": "HALF_DIMINISHED",
            "HALF_DIM7": "HALF_DIMINISHED7",
            "ø7": "HALF_DIMINISHED7",
            "DIM7": "DIMINISHED_SEVENTH",
            "°7": "DIMINISHED_SEVENTH",
            "MIN9": "MINOR_NINTH",
            "m9": "MINOR_NINTH",
            "MAJ9": "MAJOR_NINTH",
            "M9": "MAJOR_NINTH"
        }
        value = mapping.get(value, value)
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid chord quality: {value}")

    def get_intervals(self) -> list[int]:
        """Get the intervals for this chord quality."""
        intervals_map = {
            self.MAJOR: [0, 4, 7],
            self.MINOR: [0, 3, 7],
            self.DIMINISHED: [0, 3, 6],
            self.AUGMENTED: [0, 4, 8],
            self.DOMINANT: [0, 4, 7, 10],
            self.DOMINANT_SEVENTH: [0, 4, 7, 10],
            self.MAJOR_SEVENTH: [0, 4, 7, 11],
            self.MINOR_SEVENTH: [0, 3, 7, 10],
            self.HALF_DIMINISHED: [0, 3, 6, 10],
            self.HALF_DIMINISHED_SEVENTH: [0, 3, 6, 10],
            self.DIMINISHED_SEVENTH: [0, 3, 6, 9],
            self.MINOR_NINTH: [0, 3, 7, 10, 14],
            self.MAJOR_NINTH: [0, 4, 7, 11, 14],
            self.FULL_DIMINISHED: [0, 3, 6, 9]
        }
        return intervals_map[self]