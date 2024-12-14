"""Module defining scale types."""
from enum import Enum
from typing import List, Final

class ScaleType(Enum):
    """Enum representing different scale types."""
    MAJOR: Final[List[int]] = [2, 2, 1, 2, 2, 2, 1]  # Major scale intervals
    NATURAL_MINOR: Final[List[int]] = [2, 1, 2, 2, 1, 2, 2]  # Natural minor scale intervals
    HARMONIC_MINOR: Final[List[int]] = [2, 1, 2, 2, 1, 3, 1]  # Harmonic minor scale intervals
    MELODIC_MINOR: Final[List[int]] = [2, 1, 2, 2, 2, 2, 1]  # Melodic minor scale intervals
    DORIAN: Final[List[int]] = [2, 1, 2, 2, 2, 1, 2]  # Dorian mode intervals
    PHRYGIAN: Final[List[int]] = [1, 2, 2, 2, 1, 2, 2]  # Phrygian mode intervals
    LYDIAN: Final[List[int]] = [2, 2, 2, 1, 2, 2, 1]  # Lydian mode intervals
    MIXOLYDIAN: Final[List[int]] = [2, 2, 1, 2, 2, 1, 2]  # Mixolydian mode intervals
    LOCRIAN: Final[List[int]] = [1, 2, 2, 1, 2, 2, 2]  # Locrian mode intervals
    PENTATONIC_MAJOR: Final[List[int]] = [2, 2, 3, 2, 3]  # Major pentatonic scale intervals
    PENTATONIC_MINOR: Final[List[int]] = [3, 2, 2, 3, 2]  # Minor pentatonic scale intervals
    BLUES: Final[List[int]] = [3, 2, 1, 1, 3, 2]  # Blues scale intervals
    CHROMATIC: Final[List[int]] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # Chromatic scale intervals
    WHOLE_TONE: Final[List[int]] = [2, 2, 2, 2, 2, 2]  # Whole tone scale intervals

    def get_intervals(self) -> List[int]:
        """Get the intervals for this scale type."""
        return self.value

    def validate_degree(self, degree: int) -> bool:
        """Validate if a scale degree is valid for this scale type."""
        return 1 <= degree <= len(self.value) + 1

    @property
    def degree_count(self) -> int:
        """Get the number of degrees in this scale type."""
        return len(self.value)

    @property
    def is_diatonic(self) -> bool:
        """Check if the scale is diatonic (7 notes)."""
        return self.degree_count == 7

    def get_scale_degrees(self) -> List[int]:
        """Get the scale degrees for this scale type."""
        return list(range(1, self.degree_count + 1))
