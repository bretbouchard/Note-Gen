from enum import Enum
from typing import List, Dict, ClassVar

class ChordQualityType(str, Enum):
    """Enum representing different chord qualities."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    DIMINISHED = "DIMINISHED"
    AUGMENTED = "AUGMENTED"
    MAJOR7 = "MAJOR7"
    MINOR7 = "MINOR7"
    DOMINANT7 = "DOMINANT7"
    DIMINISHED7 = "DIMINISHED7"
    HALF_DIMINISHED7 = "HALF_DIMINISHED7"
    MINOR_MAJOR7 = "MINOR_MAJOR7"
    AUGMENTED7 = "AUGMENTED7"
    SUSPENDED2 = "SUSPENDED2"
    SUSPENDED4 = "SUSPENDED4"

    @classmethod
    def get_chord_intervals(cls) -> Dict[str, List[int]]:
        """Get the intervals for all chord qualities."""
        return {
            cls.MAJOR.value: [0, 4, 7],
            cls.MINOR.value: [0, 3, 7],
            cls.DIMINISHED.value: [0, 3, 6],
            cls.AUGMENTED.value: [0, 4, 8],
            cls.MAJOR7.value: [0, 4, 7, 11],
            cls.MINOR7.value: [0, 3, 7, 10],
            cls.DOMINANT7.value: [0, 4, 7, 10],
            cls.DIMINISHED7.value: [0, 3, 6, 9],
            cls.HALF_DIMINISHED7.value: [0, 3, 6, 10],
            cls.MINOR_MAJOR7.value: [0, 3, 7, 11],
            cls.AUGMENTED7.value: [0, 4, 8, 10],
            cls.SUSPENDED2.value: [0, 2, 7],
            cls.SUSPENDED4.value: [0, 5, 7]
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
        # Convert to uppercase for consistency
        quality_str = quality_str.upper()
        
        # First try direct mapping
        try:
            return cls(quality_str)
        except ValueError:
            pass
            
        # Try aliases
        aliases = cls.get_quality_aliases()
        if quality_str in aliases:
            return cls(aliases[quality_str])
            
        raise ValueError(f"Unrecognized chord quality: {quality_str}")
