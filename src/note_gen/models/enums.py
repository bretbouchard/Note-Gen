from typing import List, Optional, Dict, Union, Any
from enum import Enum, StrEnum
import logging

logger = logging.getLogger(__name__)

class AccidentalType(StrEnum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

class ScaleDegree(Enum):
    TONIC = 1
    SUPERTONIC = 2
    MEDIANT = 3
    SUBDOMINANT = 4
    DOMINANT = 5
    SUBMEDIANT = 6
    LEADING_TONE = 7

    def __str__(self) -> str:
        return str(self.value)

class ScaleType(StrEnum):
    """Enum representing different scale types."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    HARMONIC_MINOR = "HARMONIC_MINOR"
    MELODIC_MINOR = "MELODIC_MINOR"
    DORIAN = "DORIAN"
    PHRYGIAN = "PHRYGIAN"
    LYDIAN = "LYDIAN"
    MIXOLYDIAN = "MIXOLYDIAN"
    LOCRIAN = "LOCRIAN"
    PENTATONIC_MAJOR = "PENTATONIC_MAJOR"
    PENTATONIC_MINOR = "PENTATONIC_MINOR"
    BLUES = "BLUES"
    CHROMATIC = "CHROMATIC"
    WHOLE_TONE = "WHOLE_TONE"
    MINOR_PENTATONIC = "MINOR_PENTATONIC"
    MAJOR_PENTATONIC = "MAJOR_PENTATONIC"
    HARMONIC_MAJOR = "HARMONIC_MAJOR"
    MELODIC_MAJOR = "MELODIC_MAJOR"
    DOUBLE_HARMONIC_MAJOR = "DOUBLE_HARMONIC_MAJOR"

    def __str__(self) -> str:
        return self.value

    def get_intervals(self) -> List[int]:
        """Get the intervals for this scale type."""
        absolute_intervals_map = {
            ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11],
            ScaleType.MINOR: [0, 2, 3, 5, 7, 8, 10],
            ScaleType.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
            ScaleType.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11],
            ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
            ScaleType.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
            ScaleType.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
            ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
            ScaleType.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
            ScaleType.PENTATONIC_MAJOR: [0, 2, 4, 7, 9],
            ScaleType.PENTATONIC_MINOR: [0, 3, 5, 7, 10],
            ScaleType.BLUES: [0, 3, 5, 6, 7, 10],
            ScaleType.CHROMATIC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            ScaleType.WHOLE_TONE: [0, 2, 4, 6, 8, 10],
            ScaleType.MINOR_PENTATONIC: [0, 3, 5, 7, 10],
            ScaleType.MAJOR_PENTATONIC: [0, 2, 4, 7, 9],
            ScaleType.HARMONIC_MAJOR: [0, 2, 4, 5, 7, 8, 11],
            ScaleType.MELODIC_MAJOR: [0, 2, 4, 5, 7, 8, 10],
            ScaleType.DOUBLE_HARMONIC_MAJOR: [0, 1, 4, 5, 7, 8, 11],
        }

        if self not in absolute_intervals_map:
            raise ValueError(f"No intervals defined for scale type: {self}")
        
        # Convert absolute intervals to relative intervals
        absolute_intervals = absolute_intervals_map[self]
        relative_intervals = []
        for i in range(1, len(absolute_intervals)):
            relative_intervals.append(absolute_intervals[i] - absolute_intervals[i-1])
        
        logger.debug(f"Getting intervals for scale type: {self}")
        return relative_intervals

    @classmethod
    def degree_count(cls, scale_type: Optional['ScaleType'] = None) -> int:
        """Returns the number of degrees for each scale type."""
        scale_degrees = {
            cls.MAJOR: 7,
            cls.MINOR: 7,
            cls.HARMONIC_MINOR: 7,
            cls.MELODIC_MINOR: 7,
            cls.DORIAN: 7,
            cls.PHRYGIAN: 7,
            cls.LYDIAN: 7,
            cls.MIXOLYDIAN: 7,
            cls.LOCRIAN: 7,
            cls.PENTATONIC_MAJOR: 5,
            cls.PENTATONIC_MINOR: 5,
            cls.BLUES: 6,
            cls.CHROMATIC: 12,
            cls.WHOLE_TONE: 6,
            cls.MINOR_PENTATONIC: 5,
            cls.MAJOR_PENTATONIC: 5,
            cls.HARMONIC_MAJOR: 7,
            cls.MELODIC_MAJOR: 7,
            cls.DOUBLE_HARMONIC_MAJOR: 7,
        }
        if scale_type is None:
            scale_type = cls.MAJOR  # or any other default scale type you prefer

        return scale_degrees[scale_type]

class CustomValidationError(Exception):
    """Custom exception for validation errors."""
    pass