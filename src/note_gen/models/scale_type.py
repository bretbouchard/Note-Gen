from enum import Enum
from typing import List
import logging

logger = logging.getLogger(__name__)


class ScaleType(str, Enum):
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

    def get_intervals(self) -> List[int]:
        """Get the intervals for this scale type."""
        intervals_map: dict[ScaleType, List[int]] = {
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
            ScaleType.CHROMATIC: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ScaleType.WHOLE_TONE: [2, 2, 2, 2, 2, 2],
        }
        logger.debug(f"Getting intervals for scale type: {self.name}")
        return intervals_map[self]

    def validate_degree(self, degree: int) -> bool:
        """Validate if a scale degree is valid for this scale type."""
        intervals = self.get_intervals()
        if degree < 1 or degree > len(intervals) + 1:
            logger.error(
                f"Invalid scale degree: {degree}. Must be between 1 and {len(intervals) + 1}."
            )
            raise ValueError(
                f"Invalid scale degree: {degree}. Must be between 1 and {len(intervals) + 1}."
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
