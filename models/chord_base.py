"""Module for defining the base properties of musical chords.

This module provides classes and functions that define the fundamental properties of musical chords, including their intervals, qualities, and relationships to scales. It serves as a foundation for more complex chord structures and manipulations.

The module contains the following key components:

- Mappings for Roman numerals to integer scale degrees (ROMAN_TO_INT)
- Mappings for integers to Roman numerals (INT_TO_ROMAN)
- Mappings for words to Roman numerals (WORD_TO_ROMAN)
- Mappings for chord qualities to their intervals (QUALITY_INTERVALS and CHORD_INTERVALS)
- A base class for chords (ChordBase) with attributes for notes, duration, and velocity

ChordBase Class
----------------

The `ChordBase` class encapsulates the basic properties of a chord, including its intervals and quality. It provides methods for manipulating and analyzing chord structures.

Usage
-----

To create a base chord, instantiate the `ChordBase` class with the desired notes, duration, and velocity:

```python
chord = ChordBase(notes=[Note("C"), Note("E"), Note("G")], duration=1.0, velocity=100)
print(chord)
```

This module is designed to be extensible, allowing for the addition of new properties and methods related to chord analysis as needed.

"""

from typing import Dict, List, Optional
from pydantic import BaseModel
from .note import Note
from .chord_quality import ChordQuality

# Mapping of Roman numerals to integer scale degrees
ROMAN_TO_INT = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7
}

# Mapping of integers to Roman numerals
INT_TO_ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"
}

# Mapping of words to Roman numerals
WORD_TO_ROMAN = {
    "one": "I", "two": "II", "three": "III", "four": "IV",
    "five": "V", "six": "VI", "seven": "VII"
}

# Mapping of chord qualities to their intervals
QUALITY_QUALITIES = {
    ChordQuality.major,
    ChordQuality.minor,
    ChordQuality.diminished,
    ChordQuality.augmented,
    ChordQuality.dominant7,
    ChordQuality.major7,
    ChordQuality.minor7,
    ChordQuality.diminished7,
    ChordQuality.half_diminished7,
    ChordQuality.sus2,
    ChordQuality.sus4
}

CHORD_INTERVALS: Dict[ChordQuality, List[int]] = {
    ChordQuality.major: [0, 4, 7],
    ChordQuality.minor: [0, 3, 7],
    ChordQuality.diminished: [0, 3, 6],
    ChordQuality.augmented: [0, 4, 8],
    ChordQuality.dominant7: [0, 4, 7, 10],
    ChordQuality.major7: [0, 4, 7, 11],
    ChordQuality.minor7: [0, 3, 7, 10],
    ChordQuality.diminished7: [0, 3, 6, 9],
    ChordQuality.half_diminished7: [0, 3, 6, 10],
    ChordQuality.sus2: [0, 2, 7],
    ChordQuality.sus4: [0, 5, 7]
}

CHORD_COUNT = {
    ChordQuality.major: 3,
    ChordQuality.minor: 3,
    ChordQuality.diminished: 3,
    ChordQuality.augmented: 3,
    ChordQuality.dominant7: 4,
    ChordQuality.major7: 4,
    ChordQuality.minor7: 4,
    ChordQuality.diminished7: 4,
    ChordQuality.half_diminished7: 4,
    ChordQuality.augmented7: 4,
    ChordQuality.major9: 5,
    ChordQuality.minor9: 5,
    ChordQuality.dominant9: 5,
    ChordQuality.major11: 6,
    ChordQuality.minor11: 6,
    ChordQuality.sus2: 3,
    ChordQuality.sus4: 3,
    ChordQuality.seven_sus4: 4
}

class ChordBase(BaseModel):
    """Base class for musical chords.

    This class defines the fundamental properties of a chord, including its intervals and qualities. It provides methods for manipulating and analyzing chord structures.

    Attributes:
        notes (List[Note]): A list of notes in the chord.
        duration (Optional[float]): The duration of the chord. Defaults to None.
        velocity (Optional[int]): The velocity of the chord. Defaults to None.

    The ChordBase class provides a foundation for working with chords, allowing for the creation of chords with specific notes, duration, and velocity.
    It serves as a base class for more specific chord types, enabling the creation of complex chord structures.

    Example:
        >>> chord = ChordBase(notes=[Note("C"), Note("E"), Note("G")], duration=1.0, velocity=100)
        >>> print(chord.notes)
        [Note("C"), Note("E"), Note("G")]
        >>> print(chord.duration)
        1.0
        >>> print(chord.velocity)
        100
    """
    notes: List[Note]
    duration: Optional[float] = None
    velocity: Optional[int] = None

    def get_intervals(self, quality: ChordQuality) -> List[int]:
        """Return the intervals that define the chord.

        Args:
            quality (ChordQuality): The quality of the chord (e.g., ChordQuality.major, ChordQuality.minor).

        Returns:
            List[int]: The intervals of the chord.
        """
        return CHORD_INTERVALS.get(quality, [])

    def __str__(self) -> str:
        """Return the string representation of the chord base.

        Returns:
            str: The string representation of the chord base.
        """
        return f"Chord with notes: {self.notes}, duration: {self.duration}, velocity: {self.velocity}"
