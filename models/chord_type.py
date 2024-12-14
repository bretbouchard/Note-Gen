"""Module defining chord types and their intervals."""
from enum import Enum
from typing import List, Final

class ChordType(Enum):
    """Enum representing different chord types and their intervals."""
    MAJOR: Final[List[int]] = [0, 4, 7]  # Major triad
    MINOR: Final[List[int]] = [0, 3, 7]  # Minor triad
    DIMINISHED: Final[List[int]] = [0, 3, 6]  # Diminished triad
    AUGMENTED: Final[List[int]] = [0, 4, 8]  # Augmented triad
    MAJOR7: Final[List[int]] = [0, 4, 7, 11]  # Major seventh
    MINOR7: Final[List[int]] = [0, 3, 7, 10]  # Minor seventh
    DOMINANT7: Final[List[int]] = [0, 4, 7, 10]  # Dominant seventh
    HALF_DIMINISHED7: Final[List[int]] = [0, 3, 6, 10]  # Half-diminished seventh
    DIMINISHED7: Final[List[int]] = [0, 3, 6, 9]  # Fully diminished seventh
