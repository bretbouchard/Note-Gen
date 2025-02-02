from enum import Enum
from typing import List, Dict

# Scale intervals from root note
SCALE_INTERVALS = {
    "MAJOR": [0, 2, 4, 5, 7, 9, 11],
    "MINOR": [0, 2, 3, 5, 7, 8, 10],
    "HARMONIC_MINOR": [0, 2, 3, 5, 7, 8, 11],
    "MELODIC_MINOR": [0, 2, 3, 5, 7, 9, 11],
    "DORIAN": [0, 2, 3, 5, 7, 9, 10],
    "PHRYGIAN": [0, 1, 3, 5, 7, 8, 10],
    "LYDIAN": [0, 2, 4, 6, 7, 9, 11],
    "MIXOLYDIAN": [0, 2, 4, 5, 7, 9, 10],
    "LOCRIAN": [0, 1, 3, 5, 6, 8, 10],
    "MAJOR_PENTATONIC": [0, 2, 4, 7, 9],
    "MINOR_PENTATONIC": [0, 3, 5, 7, 10],
    "CHROMATIC": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "HARMONIC_MAJOR": [0, 2, 4, 5, 7, 8, 11],
    "MELODIC_MAJOR": [0, 2, 4, 5, 7, 8, 10],
    "DOUBLE_HARMONIC_MAJOR": [0, 1, 4, 5, 7, 8, 11]
}

class ScaleType(str, Enum):
    """Enum representing different types of musical scales."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    HARMONIC_MINOR = "HARMONIC_MINOR"
    MELODIC_MINOR = "MELODIC_MINOR"
    DORIAN = "DORIAN"
    PHRYGIAN = "PHRYGIAN"
    LYDIAN = "LYDIAN"
    MIXOLYDIAN = "MIXOLYDIAN"
    LOCRIAN = "LOCRIAN"
    MAJOR_PENTATONIC = "MAJOR_PENTATONIC"
    MINOR_PENTATONIC = "MINOR_PENTATONIC"
    CHROMATIC = "CHROMATIC"
    HARMONIC_MAJOR = "HARMONIC_MAJOR"
    MELODIC_MAJOR = "MELODIC_MAJOR"
    DOUBLE_HARMONIC_MAJOR = "DOUBLE_HARMONIC_MAJOR"

    def get_intervals(self) -> List[int]:
        """Get the intervals for this scale type.
        
        Returns:
            List[int]: The intervals for this scale type, starting from 0 (root)
            
        Raises:
            KeyError: If the scale type is not found in SCALE_INTERVALS
        """
        try:
            return SCALE_INTERVALS[self.value]
        except KeyError:
            raise KeyError(f"No intervals defined for scale type: {self.value}")
