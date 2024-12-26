from __future__ import annotations
from typing import Dict, List, Optional, TYPE_CHECKING
from pydantic import ConfigDict
from src.note_gen.models.base_types import MusicalBase
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.enums import ChordQualityType
import logging

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)

# Mapping of Roman numerals to integer scale degrees
ROMAN_TO_INT = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "i": 1,
    "ii": 2,
    "iii": 3,
    "iv": 4,
    "v": 5,
    "vi": 6,
    "vii": 7,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
}

# Mapping of integers to Roman numerals
INT_TO_ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}

# Mapping of words to Roman numerals
WORD_TO_ROMAN = {
    "one": "I",
    "two": "II",
    "three": "III",
    "four": "IV",
    "five": "V",
    "six": "VI",
    "seven": "VII",
}

# Mapping of chord qualities to their intervals
# Mapping of chord qualities to their intervals
QUALITY_QUALITIES = {
    ChordQualityType.MAJOR,
    ChordQualityType.MINOR,
    ChordQualityType.DIMINISHED,
    ChordQualityType.AUGMENTED,
    ChordQualityType.DOMINANT_7,
    ChordQualityType.MAJOR_7,
    ChordQualityType.MINOR_7,
    ChordQualityType.DIMINISHED_7,
    ChordQualityType.HALF_DIMINISHED,
    ChordQualityType.HALF_DIMINISHED_7,
    ChordQualityType.SUS2,
    ChordQualityType.SUS4,
}

CHORD_INTERVALS: Dict[ChordQualityType, List[int]] = {
    ChordQualityType.MAJOR: [0, 4, 7],
    ChordQualityType.MINOR: [0, 3, 7],
    ChordQualityType.DIMINISHED: [0, 3, 6],
    ChordQualityType.AUGMENTED: [0, 4, 8],
    ChordQualityType.DOMINANT_7: [0, 4, 7, 10],
    ChordQualityType.MAJOR_7: [0, 4, 7, 11],
    ChordQualityType.MINOR_7: [0, 3, 7, 10],
    ChordQualityType.DIMINISHED_7: [0, 3, 6, 9],
    ChordQualityType.HALF_DIMINISHED: [0, 3, 6, 10],
    ChordQualityType.HALF_DIMINISHED_7: [0, 3, 6, 10],
    ChordQualityType.SUS2: [0, 2, 7],
    ChordQualityType.SUS4: [0, 5, 7],
}

CHORD_COUNT = {
    ChordQualityType.MAJOR: 3,
    ChordQualityType.MINOR: 3,
    ChordQualityType.DIMINISHED: 3,
    ChordQualityType.AUGMENTED: 3,
    ChordQualityType.DOMINANT_7: 4,
    ChordQualityType.MAJOR_7: 4,
    ChordQualityType.MINOR_7: 4,
    ChordQualityType.DIMINISHED_7: 4,
    ChordQualityType.HALF_DIMINISHED: 4,
    ChordQualityType.HALF_DIMINISHED_7: 4,
    ChordQualityType.AUGMENTED_7: 4,
    ChordQualityType.MAJOR_9: 5,
    ChordQualityType.MINOR_9: 5,
    ChordQualityType.DOMINANT_9: 5,
    ChordQualityType.MAJOR_11: 6,
    ChordQualityType.MINOR_11: 6,
    ChordQualityType.SUS2: 3,
    ChordQualityType.SUS4: 3,
    ChordQualityType.SEVEN_SUS4: 4,
}


class ChordBase(MusicalBase):
    """Base class for chord-related structures."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    root: Note
    intervals: List[int]
    duration: Optional[float] = None
    velocity: Optional[int] = None

    @property
    def notes(self) -> List[int]:
        """Get the notes as a list of intervals."""
        return [int(interval) for interval in self.intervals]

    def get_intervals(self, quality: ChordQualityType) -> List[int]:
        """Get the intervals for a given chord quality.

        Args:
            quality: The chord quality type to get intervals for.

        Returns:
            List[int]: The intervals for the chord quality.

        Raises:
            ValueError: If quality is not a ChordQualityType instance.
        """
        if not isinstance(quality, ChordQualityType):
            raise ValueError("Quality must be an instance of ChordQualityType")
        return CHORD_INTERVALS[quality]

    def __str__(self) -> str:
        return f"ChordBase(root={self.root.name} natural in octave {self.root.octave}, intervals={self.intervals})"
