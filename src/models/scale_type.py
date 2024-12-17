"""Module defining scale types."""
from enum import Enum
from typing import List, Final
import logging
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)

class ScaleType(BaseModel):
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

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_intervals(self) -> List[int]:
        """Get the intervals for this scale type."""
        logger.debug(f"Getting intervals for scale type: {self.name}")
        return self.value

    def validate_degree(self, degree: int) -> bool:
        """Validate if a scale degree is valid for this scale type."""
        logger.debug(f"Validating degree: {degree} for scale type: {self.name}")
        if degree < 1 or degree > len(self.value) + 1:
            logger.error(f"Invalid scale degree: {degree}. Must be between 1 and {len(self.value) + 1}.")
            raise ValueError(f"Invalid scale degree: {degree}. Must be between 1 and {len(self.value) + 1}.")
        logger.info(f"Degree {degree} is valid for scale type: {self.name}")
        return True

    @property
    def degree_count(self) -> int:
        """Get the number of degrees in this scale type."""
        logger.debug(f"Getting degree count for scale type: {self.name}")
        return len(self.value)

    @property
    def is_diatonic(self) -> bool:
        """Check if the scale is diatonic (7 notes)."""
        logger.debug(f"Checking if scale type: {self.name} is diatonic")
        return self.degree_count == 7

    def get_scale_degrees(self) -> List[int]:
        """Get the scale degrees for this scale type."""
        logger.debug(f"Getting scale degrees for scale type: {self.name}")
        return list(range(1, self.degree_count + 1))
