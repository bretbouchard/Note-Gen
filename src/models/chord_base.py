from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from .note import Note
from .chord_quality import ChordQuality
import logging

logger = logging.getLogger(__name__)

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
    """Base class for chord-related structures."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    root: int
    intervals: List[int]
    duration: Optional[float] = None
    velocity: Optional[int] = None

    @property
    def notes(self) -> List[int]:
        """Get the list of notes in the chord."""
        return [self.root + interval for interval in self.intervals]

    def get_intervals(self, quality: ChordQuality) -> List[int]:
        """Return the intervals that define the chord."""
        if isinstance(quality, ChordQuality):
            return CHORD_INTERVALS[quality]  # Ensure this returns List[int]
        else:
            logger.error("Quality must be an instance of ChordQuality")
            raise ValueError("Quality must be an instance of ChordQuality")

    def __str__(self) -> str:
        """Return the string representation of the chord base."""
        return f"ChordBase(root={self.root}, intervals={self.intervals})"