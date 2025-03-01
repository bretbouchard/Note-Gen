from enum import Enum
from typing import List, Dict, ClassVar
from pydantic import BaseModel, ConfigDict
import logging

logger = logging.getLogger(__name__)

class ChordQualityType(str, Enum):
    """Enum representing different chord qualities."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    DIMINISHED = "DIMINISHED"
    AUGMENTED = "AUGMENTED"
    MAJOR7 = "MAJOR7"
    MINOR7 = "MINOR7"
    DOMINANT7 = "DOMINANT7"
    DOMINANT = "DOMINANT"
    DIMINISHED7 = "DIMINISHED7"
    HALF_DIMINISHED7 = "HALF_DIMINISHED7"
    MINOR_MAJOR7 = "MINOR_MAJOR7"
    AUGMENTED7 = "AUGMENTED7"
    SUSPENDED2 = "SUSPENDED2"
    SUSPENDED4 = "SUSPENDED4"
    SUSPENDED = "SUSPENDED"
    MAJOR9 = "MAJOR9"
    MINOR9 = "MINOR9"
    DOMINANT9 = "DOMINANT9"
    MAJOR11 = "MAJOR11"
    MINOR11 = "MINOR11"
    DOMINANT11 = "DOMINANT11"
    SUS2 = "SUS2"
    SUS4 = "SUS4"
    SEVEN_SUS4 = "SEVEN_SUS4"
    FLAT5 = "FLAT5"
    FLAT7 = "FLAT7"
    SHARP5 = "SHARP5"
    SHARP7 = "SHARP7"

    @classmethod
    def get_chord_intervals(cls) -> Dict[str, List[int]]:
        """Get the intervals for all chord qualities."""
        return {
            cls.MAJOR.value: [0, 4, 7],
            cls.MINOR.value: [0, 3, 7],
            cls.DIMINISHED.value: [0, 3, 6],
            cls.AUGMENTED.value: [0, 4, 8],
            cls.DOMINANT.value: [0, 4, 7],
            cls.MAJOR7.value: [0, 4, 7, 11],
            cls.MINOR7.value: [0, 3, 7, 10],
            cls.DOMINANT7.value: [0, 4, 7, 10],
            cls.DIMINISHED7.value: [0, 3, 6, 9],
            cls.HALF_DIMINISHED7.value: [0, 3, 6, 10],
            cls.MINOR_MAJOR7.value: [0, 3, 7, 11],
            cls.AUGMENTED7.value: [0, 4, 8, 10],
            cls.SUSPENDED2.value: [0, 2, 7],
            cls.SUSPENDED4.value: [0, 5, 7],
            cls.SUSPENDED.value: [0, 5, 7],
            cls.MAJOR9.value: [0, 4, 7, 11, 14],
            cls.MINOR9.value: [0, 3, 7, 10, 14],
            cls.DOMINANT9.value: [0, 4, 7, 10, 14],
            cls.MAJOR11.value: [0, 4, 7, 11, 14],
            cls.MINOR11.value: [0, 3, 7, 10, 14],
            cls.DOMINANT11.value: [0, 4, 7, 10, 14, 17],
            cls.SUS2.value: [0, 2, 7],
            cls.SUS4.value: [0, 5, 7],
            cls.SEVEN_SUS4.value: [0, 5, 7, 10],
            cls.FLAT5.value: [0, 4, 6],
            cls.FLAT7.value: [0, 4, 7, 9],
            cls.SHARP5.value: [0, 4, 8],
            cls.SHARP7.value: [0, 4, 7, 11]
        }

    @classmethod
    def get_quality_aliases(cls) -> Dict[str, str]:
        """Get the aliases for all chord qualities."""
        return {
            "MAJ": cls.MAJOR.value,
            "MIN": cls.MINOR.value,
            "DIM": cls.DIMINISHED.value,
            "AUG": cls.AUGMENTED.value,
            "MAJ7": cls.MAJOR7.value,
            "MIN7": cls.MINOR7.value,
            "DOM7": cls.DOMINANT7.value,
            "DIM7": cls.DIMINISHED7.value,
            "HALFDIM7": cls.HALF_DIMINISHED7.value,
            "MINMAJ7": cls.MINOR_MAJOR7.value,
            "AUG7": cls.AUGMENTED7.value,
            "SUS": cls.SUSPENDED.value,
            "SUS2": cls.SUSPENDED2.value,
            "SUS4": cls.SUSPENDED4.value,
            # Additional common variations
            "7": cls.DOMINANT7.value,
            "M7": cls.MAJOR7.value,
            "m7": cls.MINOR7.value,
            "dim7": cls.DIMINISHED7.value,
            "aug7": cls.AUGMENTED7.value
        }

    def get_intervals(self) -> List[int]:
        """Get the intervals for this chord quality."""
        intervals = self.get_chord_intervals()
        return intervals[self.value]

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQualityType':
        """Convert a string representation to a ChordQualityType.

        Args:
            quality_str: String representation of the chord quality (e.g., 'maj', 'min', 'dim')

        Returns:
            ChordQualityType: The corresponding chord quality type

        Raises:
            ValueError: If the quality string is not recognized
        """
        # Log the input string
        logger.debug(f"Input string for conversion: {quality_str}")

        # Convert to uppercase for consistency
        quality_str = quality_str.upper()

        # First try direct mapping
        try:
            return cls(quality_str)
        except ValueError:
            pass

        aliases = {
            # Case-sensitive aliases
            'm': cls.MINOR,
            'M': cls.MAJOR,
            'dim': cls.DIMINISHED,
            'aug': cls.AUGMENTED,
            '7': cls.DOMINANT7,
            'ø7': cls.HALF_DIMINISHED7,
            '°': cls.DIMINISHED,
            '+': cls.AUGMENTED,
            # Uppercase aliases
            'MAJ': cls.MAJOR,
            'MAJOR': cls.MAJOR,
            'MIN': cls.MINOR,
            'MINOR': cls.MINOR,
            'DIM': cls.DIMINISHED,
            'AUG': cls.AUGMENTED,
            'DOM': cls.DOMINANT,
            'DOM7': cls.DOMINANT7,
            'MAJ7': cls.MAJOR7,
            'MIN7': cls.MINOR7,
            'DIM7': cls.DIMINISHED7,
            'SUS2': cls.SUS2,
            'SUS4': cls.SUS4,
            '7SUS4': cls.SEVEN_SUS4,
            # Mixed case aliases
            'maj': cls.MAJOR,
            'min': cls.MINOR,
            'maj7': cls.MAJOR7,
            'min7': cls.MINOR7,
            'm7': cls.MINOR7,
            'dim7': cls.DIMINISHED7,
            'aug7': cls.AUGMENTED7,
            'sus2': cls.SUS2,
            'sus4': cls.SUS4,
            '7sus4': cls.SEVEN_SUS4,
            'b5': cls.FLAT5,
            '#5': cls.SHARP5,
            'b7': cls.FLAT7,
            '#7': cls.SHARP7,
        }

        # Check if the quality_str matches any alias
        if quality_str in aliases:
            chord_quality = aliases[quality_str]
            # Log the output value
            logger.debug(f"Converted '{quality_str}' to {chord_quality}")
            return chord_quality

        # If not recognized, raise an error
        raise ValueError(f"Unrecognized chord quality: {quality_str}")

class ChordQuality(BaseModel):
    quality_type: ChordQualityType = ChordQualityType.MAJOR

    class Config:
        arbitrary_types_allowed = True
