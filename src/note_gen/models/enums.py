from enum import Enum
from typing import List, Dict, ClassVar

# Move intervals dictionary outside the class
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
    "MINOR_PENTATONIC": [0, 3, 5, 7, 10],
    "MAJOR_PENTATONIC": [0, 2, 4, 7, 9],
    "BLUES": [0, 3, 5, 6, 7, 10],
    "CHROMATIC": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "HARMONIC_MAJOR": [0, 2, 4, 5, 7, 8, 11],
    "MELODIC_MAJOR": [0, 2, 4, 5, 7, 8, 10],
    "DOUBLE_HARMONIC_MAJOR": [0, 1, 4, 5, 7, 8, 11]
}

class ScaleType(Enum):
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
    MINOR_PENTATONIC = "MINOR_PENTATONIC"
    MAJOR_PENTATONIC = "MAJOR_PENTATONIC"
    HARMONIC_MAJOR = "HARMONIC_MAJOR"
    MELODIC_MAJOR = "MELODIC_MAJOR"
    DOUBLE_HARMONIC_MAJOR = "DOUBLE_HARMONIC_MAJOR"

    def get_intervals(self) -> List[int]:
        """Return the intervals for this scale type."""
        # Map common synonyms to their canonical names
        name_mapping = {
            "PENTATONIC_MAJOR": "MAJOR_PENTATONIC",
            "PENTATONIC_MINOR": "MINOR_PENTATONIC"
        }

        # Look up the canonical name if it's an alias
        scale_name = self.value  # Get the string value of the enum
        canonical_name = name_mapping.get(scale_name, scale_name)
        try:
            return SCALE_INTERVALS[canonical_name]  # Access directly through class
        except KeyError:
            raise ValueError(f"No intervals defined for scale type: {canonical_name}")

    @property
    def degree_count(self) -> int:
        """Return the number of degrees in the scale."""
        return len(self.get_intervals())

    def is_diatonic(self) -> bool:
        """Return whether this scale type is diatonic."""
        return self.value in self._DIATONIC_SCALES

    def validate_degree(self, degree: int) -> bool:
        """Validate if a degree number is valid for this scale type."""
        return 1 <= degree <= self.degree_count
