"""Module for defining musical pattern types."""
from enum import Enum

class PatternType(str, Enum):
    """Enum representing different types of musical patterns."""
    SCALE = "scale"
    ARPEGGIO = "arpeggio"
    MELODIC = "melodic"
    RHYTHMIC = "rhythmic"
    CHROMATIC = "chromatic"

    @property
    def requires_scale(self) -> bool:
        """Check if this pattern type requires a scale context."""
        return self in {
            PatternType.SCALE,
            PatternType.MELODIC,
            PatternType.ARPEGGIO
        }

    @property
    def requires_chord(self) -> bool:
        """Check if this pattern type requires a chord context."""
        return self in {PatternType.ARPEGGIO}

    @property
    def allows_repetition(self) -> bool:
        """Check if this pattern type allows note repetition."""
        return self in {
            PatternType.MELODIC,
            PatternType.RHYTHMIC
        }
