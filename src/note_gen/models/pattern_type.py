from enum import Enum
from typing import List
import logging

logger = logging.getLogger(__name__)


class PatternType(str, Enum):
    """Enum representing different pattern types."""

    ASCENDING = "ascending"
    DESCENDING = "descending"
    ASCENDING_DESCENDING = "ascending_descending"
    DESCENDING_ASCENDING = "descending_ascending"
    RANDOM = "random"

    def get_pattern(self, notes: List[str]) -> List[str]:
        """Generate a pattern from the given notes."""
        logger.debug(f"Generating {self.value} pattern")

        if not notes:
            raise ValueError("Cannot generate pattern from an empty list of notes.")

        match self:
            case PatternType.ASCENDING:
                return notes
            case PatternType.DESCENDING:
                return list(reversed(notes))
            case PatternType.ASCENDING_DESCENDING:
                return notes + list(reversed(notes[:-1]))
            case PatternType.DESCENDING_ASCENDING:
                reversed_notes = list(reversed(notes))
                return reversed_notes + notes[1:]
            case PatternType.RANDOM:
                import random

                shuffled = notes.copy()
                random.shuffle(shuffled)
                return shuffled
            case _:
                raise ValueError(f"Unknown pattern type: {self.value}")
