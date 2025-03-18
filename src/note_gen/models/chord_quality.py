from enum import Enum
from typing import List, Dict

class ChordQuality(Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    DIMINISHED = "DIMINISHED"
    AUGMENTED = "AUGMENTED"
    DOMINANT = "DOMINANT"
    DOMINANT_SEVENTH = "DOMINANT_SEVENTH"
    MAJOR_SEVENTH = "MAJOR_SEVENTH"
    MINOR_SEVENTH = "MINOR_SEVENTH"
    FULL_DIMINISHED = "FULL_DIMINISHED"
    HALF_DIMINISHED = "HALF_DIMINISHED"
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
    SUSPENDED = "SUSPENDED"

    def get_intervals(self) -> List[int]:
        """Return the semitone intervals for the chord quality."""
        intervals_map = {
            ChordQuality.MAJOR: [0, 4, 7],
            ChordQuality.MINOR: [0, 3, 7],
            ChordQuality.DIMINISHED: [0, 3, 6],
            ChordQuality.AUGMENTED: [0, 4, 8],
            ChordQuality.DOMINANT: [0, 4, 7],
            ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
            ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
            ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
            ChordQuality.FULL_DIMINISHED: [0, 3, 6, 9],
            ChordQuality.HALF_DIMINISHED: [0, 3, 6, 10],
            ChordQuality.MAJOR9: [0, 4, 7, 11, 14],
            ChordQuality.MINOR9: [0, 3, 7, 10, 14],
            ChordQuality.DOMINANT9: [0, 4, 7, 10, 14],
            ChordQuality.MAJOR11: [0, 4, 7, 11, 14, 17],
            ChordQuality.MINOR11: [0, 3, 7, 10, 14, 17],
            ChordQuality.DOMINANT11: [0, 4, 7, 10, 14, 17],
            ChordQuality.SUS2: [0, 2, 7],
            ChordQuality.SUS4: [0, 5, 7],
            ChordQuality.SEVEN_SUS4: [0, 5, 7, 10],
            ChordQuality.FLAT5: [0, 4, 6],
            ChordQuality.FLAT7: [0, 4, 7, 9],
            ChordQuality.SHARP5: [0, 4, 8],
            ChordQuality.SHARP7: [0, 4, 7, 11],
            ChordQuality.SUSPENDED: [0, 5, 7],
        }
        if self not in intervals_map:
            raise ValueError(f"Invalid chord quality: {self}")
        return intervals_map[self]

    def __str__(self) -> str:
        """Return the string representation of the chord quality."""
        return self.value

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQuality':
        """Convert a string representation to ChordQuality."""
        # Convert input to lowercase for case-insensitive comparison
        quality_str_lower = quality_str.lower()
        
        quality_map = {
            '': cls.MAJOR,
            'm': cls.MINOR,
            'M': cls.MAJOR,  # Added explicit mapping for 'M'
            'min': cls.MINOR,
            'maj': cls.MAJOR,
            'major': cls.MAJOR,
            'minor': cls.MINOR,
            'dim': cls.DIMINISHED,
            'diminished': cls.DIMINISHED,
            '°': cls.DIMINISHED,
            '+': cls.AUGMENTED,
            'aug': cls.AUGMENTED,
            'augmented': cls.AUGMENTED,
            '7': cls.DOMINANT_SEVENTH,
            'maj7': cls.MAJOR_SEVENTH,
            'major7': cls.MAJOR_SEVENTH,
            'm7': cls.MINOR_SEVENTH,
            'min7': cls.MINOR_SEVENTH,
            'minor7': cls.MINOR_SEVENTH,
            '°7': cls.FULL_DIMINISHED,
            'dim7': cls.FULL_DIMINISHED,
            'diminished7': cls.FULL_DIMINISHED,
            'ø7': cls.HALF_DIMINISHED,
            'm7b5': cls.HALF_DIMINISHED,
            'dominant': cls.DOMINANT,
            'dominant7': cls.DOMINANT_SEVENTH,
        }

        # First try exact match (for case-sensitive symbols like 'M')
        if quality_str in quality_map:
            return quality_map[quality_str]

        # Then try case-insensitive match
        for key, value in quality_map.items():
            if quality_str_lower == key.lower():
                return value

        # If no match found, try matching against enum values directly
        try:
            return cls[quality_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid chord quality: {quality_str}")
