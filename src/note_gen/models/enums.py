from typing import List, Optional
from enum import Enum, StrEnum
import logging

class AccidentalType(StrEnum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

class ChordQualityType(str, Enum):
    """Enum for chord quality types."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT_7 = "dominant_7"
    MAJOR_7 = "MAJOR_7"
    MINOR_7 = "MINOR_7"
    DIMINISHED_7 = "diminished_7"
    HALF_DIMINISHED_7 = "half_diminished_7"
    AUGMENTED_7 = "augmented_7"
    MAJOR_9 = "MAJOR_9"
    MINOR_9 = "MINOR_9"
    DOMINANT_9 = "dominant_9"
    MAJOR_11 = "MAJOR_11"
    MINOR_11 = "MINOR_11"
    DOMINANT_11 = "dominant_11"
    SUS2 = "sus2"
    SUS4 = "sus4"
    SEVEN_SUS4 = "seven_sus4"
    FLAT_5 = "flat_5"
    FLAT_7 = "flat_7"
    SHARP_5 = "sharp_5"
    SHARP_7 = "sharp_7"
    DOMINANT = "dominant"

    # Define _ALIASES as a class variable
    _ALIASES = {
        "major": "MAJOR",
        "minor": "MINOR",
        "dim": "diminished",
        "diminished": "diminished",
        "aug": "augmented",
        "augmented": "augmented",
        "dom7": "dominant_7",
        "7": "dominant_7",
        "maj7": "MAJOR_7",
        "min7": "MINOR_7",
        "m7": "MINOR_7",
        "dim7": "diminished_7",
        "half_dim7": "half_diminished_7",
        "aug7": "augmented_7",
        "maj9": "MAJOR_9",
        "min9": "MINOR_9",
        "m9": "MINOR_9",
        "dom9": "dominant_9",
        "9": "dominant_9",
        "maj11": "MAJOR_11",
        "min11": "MINOR_11",
        "m11": "MINOR_11",
        "dom11": "dominant_11",
        "11": "dominant_11",
        "sus2": "sus2",
        "sus4": "sus4",
        "7sus4": "seven_sus4",
        "b5": "flat_5",
        "b7": "flat_7",
        "#5": "sharp_5",
        "#7": "sharp_7",
        "dom": "dominant"
    }

    def get_intervals(self) -> List[int]:
        INTERVALS = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            ChordQualityType.DOMINANT: [0, 4, 7, 10],
            ChordQualityType.DOMINANT_7: [0, 4, 7, 10],
            ChordQualityType.MAJOR_7: [0, 4, 7, 11],
            ChordQualityType.MINOR_7: [0, 3, 7, 10],
            ChordQualityType.DIMINISHED_7: [0, 3, 6, 9],
            ChordQualityType.HALF_DIMINISHED_7: [0, 3, 6, 10],
            ChordQualityType.MAJOR_9: [0, 4, 7, 11, 14],
            ChordQualityType.MINOR_9: [0, 3, 7, 10, 13],
            ChordQualityType.DOMINANT_9: [0, 4, 7, 10, 14],
            ChordQualityType.AUGMENTED_7: [0, 4, 8, 10],  # Added missing intervals
        }
        if self not in INTERVALS:
            logging.error(f"KeyError: '{self.value}' not found in INTERVALS.")
            raise KeyError(f"'{self.value}' is not a valid chord quality type.")
        return INTERVALS[self]

    @classmethod
    def from_string(cls, quality_string: str) -> 'ChordQualityType':
        """Convert a string to a ChordQualityType."""
        logging.debug(f"Processing quality string: '{quality_string}' of type {type(quality_string)}")
        quality_string = quality_string.lower()
        
        # Define aliases as a regular dictionary
        aliases = {
            'major': cls.MAJOR,
            'minor': cls.MINOR,
            'dim': cls.DIMINISHED,
            'diminished': cls.DIMINISHED,
            'aug': cls.AUGMENTED,
            '+': cls.AUGMENTED,
            '7': cls.DOMINANT_7,
            'maj7': cls.MAJOR_7,
            'm7': cls.MINOR_7,
            'dim7': cls.DIMINISHED_7,
            'ø7': cls.HALF_DIMINISHED_7,
            'm7b5': cls.HALF_DIMINISHED_7,
            # ... add other aliases as needed
        }

        if quality_string in aliases:
            return aliases[quality_string]
            
        try:
            return cls(quality_string.upper())
        except ValueError:
            raise ValueError(f"Invalid chord quality: {quality_string}")

    @classmethod
    def to_string(cls, quality: 'ChordQualityType') -> str:
        return quality.name

    def __str__(self) -> str:
        if self == ChordQualityType.DOMINANT_7:
            return "dominant_7"
        if self == ChordQualityType.MAJOR_7:
            return "maj7"
        if self == ChordQualityType.MINOR_7:
            return "m7"
        return self.value


class ScaleDegree(Enum):
    TONIC = 1
    SUPERTONIC = 2
    MEDIANT = 3
    SUBDOMINANT = 4
    DOMINANT = 5
    SUBMEDIANT = 6
    LEADING_TONE = 7


class ScaleType(Enum):
    """Enum representing different scale types."""
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    NATURAL_MINOR = "natural_MINOR"
    HARMONIC_MINOR = "harmonic_MINOR"
    MELODIC_MINOR = "melodic_MINOR"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    LOCRIAN = "locrian"
    PENTATONIC_MAJOR = "pentatonic_MAJOR"
    PENTATONIC_MINOR = "pentatonic_MINOR"
    BLUES = "blues"
    CHROMATIC = "chromatic"
    WHOLE_TONE = "whole_tone"