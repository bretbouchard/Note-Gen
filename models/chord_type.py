"""Module defining chord types and their intervals."""
from enum import Enum
from typing import List, Final

class ChordType(Enum):
    """Enum representing different chord types and their intervals.

    Each chord type corresponds to a specific set of intervals used to construct the chord.
    The intervals are represented as a list of semitone offsets from the root note.
    This enum provides a standardized way to work with different chord types in music theory.
    You can access the intervals for a specific chord type by using its enum value, 
    and then use these intervals to construct the chord in a specific key.

    Example:
        To construct a C major chord, you would use the intervals from ChordType.MAJOR, 
        starting from the note C (which is the root note).
    """
    MAJOR: Final[List[int]] = [0, 4, 7]  # Major triad
    MINOR: Final[List[int]] = [0, 3, 7]  # Minor triad
    DIMINISHED: Final[List[int]] = [0, 3, 6]  # Diminished triad
    AUGMENTED: Final[List[int]] = [0, 4, 8]  # Augmented triad
    MAJOR7: Final[List[int]] = [0, 4, 7, 11]  # Major seventh
    MINOR7: Final[List[int]] = [0, 3, 7, 10]  # Minor seventh
    DOMINANT7: Final[List[int]] = [0, 4, 7, 10]  # Dominant seventh
    HALF_DIMINISHED7: Final[List[int]] = [0, 3, 6, 10]  # Half-diminished seventh
    DIMINISHED7: Final[List[int]] = [0, 3, 6, 9]  # Fully diminished seventh
