from typing import List, Optional, Dict, Union
from enum import Enum, StrEnum
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AccidentalType(StrEnum):
    """Enum for accidental types in musical notation."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

# Define intervals and aliases outside the enum class
CHORD_QUALITY_INTERVALS = {
    'MAJOR': [0, 4, 7],
    'MINOR': [0, 3, 7],
    'DIMINISHED': [0, 3, 6],
    'AUGMENTED': [0, 4, 8],
    'DOMINANT7': [0, 4, 7, 10],
    'MAJOR7': [0, 4, 7, 11],
    'MINOR7': [0, 3, 7, 10],
    'DIMINISHED7': [0, 3, 6, 9],
    'HALF_DIMINISHED7': [0, 3, 6, 10],
    'DOMINANT': [0, 4, 7, 10],
    'MAJOR9': [0, 4, 7, 11],
    'MINOR9': [0, 3, 7, 10, 14],
    'DOMINANT9': [0, 4, 7, 10, 14],
    'AUGMENTED7': [0, 4, 8, 10],
    'MAJOR11': [0, 4, 7, 11, 14],
    'MINOR11': [0, 3, 7, 10, 14],
    'DOMINANT11': [0, 4, 7, 10, 14, 17],
    'SUS2': [0, 2, 7],
    'SUS4': [0, 5, 7],
    'SEVEN_SUS4': [0, 5, 7, 10],
    'FLAT5': [0, 4, 6],
    'FLAT7': [0, 4, 7, 9],
    'SHARP5': [0, 4, 8],
    'SHARP7': [0, 4, 7, 11],
}

CHORD_QUALITY_ALIASES = {
    'maj': 'MAJOR',
    'M': 'MAJOR',
    'major': 'MAJOR',
    'min': 'MINOR',
    'm': 'MINOR',
    'minor': 'MINOR',
    'dim': 'DIMINISHED',
    'diminished': 'DIMINISHED',
    'aug': 'AUGMENTED',
    'augmented': 'AUGMENTED',
    'dominant': 'DOMINANT',
    'dominant7': 'DOMINANT7',
    'dom7': 'DOMINANT7',
    'maj7': 'MAJOR7',
    'major7': 'MAJOR7',
    'm7': 'MINOR7',
    'minor7': 'MINOR7',
    'dim7': 'DIMINISHED7',
    'diminished7': 'DIMINISHED7',
    'ø7': 'HALF_DIMINISHED7',
    'm7b5': 'HALF_DIMINISHED7',
    'half_diminished7': 'HALF_DIMINISHED7',
    '7': 'DOMINANT7',
    '7sus4': 'SEVEN_SUS4',
    'b5': 'FLAT5',
    'b7': 'FLAT7',
    '#5': 'SHARP5',
    '#7': 'SHARP7',
    '+': 'AUGMENTED',
    '°': 'DIMINISHED',
}

class ChordQualityType(StrEnum):
    """Enum for chord quality types."""
    MAJOR = 'MAJOR'
    MINOR = 'MINOR'
    DIMINISHED = 'DIMINISHED'
    AUGMENTED = 'AUGMENTED'
    DOMINANT = 'DOMINANT'
    DOMINANT7 = 'DOMINANT7'
    MAJOR7 = 'MAJOR7'
    MINOR7 = 'MINOR7'
    DIMINISHED7 = 'DIMINISHED7'
    HALF_DIMINISHED7 = 'HALF_DIMINISHED7'
    MAJOR9 = 'MAJOR9'
    MINOR9 = 'MINOR9'
    DOMINANT9 = 'DOMINANT9'
    AUGMENTED7 = 'AUGMENTED7'
    MAJOR11 = 'MAJOR11'
    MINOR11 = 'MINOR11'
    DOMINANT11 = 'DOMINANT11'
    SUS2 = 'SUS2'
    SUS4 = 'SUS4'
    SEVEN_SUS4 = 'SEVEN_SUS4'
    FLAT5 = 'FLAT5'
    FLAT7 = 'FLAT7'
    SHARP5 = 'SHARP5'
    SHARP7 = 'SHARP7'

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQualityType':
        """Convert a string representation to a ChordQualityType."""
        logging.debug(f"Converting string: {quality_str}")
        if isinstance(quality_str, cls):
            return quality_str

        # First try aliases
        # For single-letter aliases, preserve case
        if len(quality_str) == 1:
            normalized = quality_str
        else:
            normalized = quality_str.lower()
        logging.debug(f"Normalized string: {normalized}")
        logging.debug(f"Available aliases: {CHORD_QUALITY_ALIASES}")
        if normalized in CHORD_QUALITY_ALIASES:
            alias_quality = CHORD_QUALITY_ALIASES[normalized]
            logging.debug(f"Found alias mapping: {normalized} -> {alias_quality}")
            try:
                return cls(alias_quality)
            except ValueError:
                raise ValueError(f"Invalid chord quality alias mapping: {quality_str} -> {alias_quality}")

        # Then try direct mapping
        try:
            return cls(quality_str.upper())
        except ValueError:
            pass

        # If not found, raise a descriptive error
        valid_values = list(cls._member_names_) + list(CHORD_QUALITY_ALIASES.keys())
        raise ValueError(f"Invalid chord quality: {quality_str}. Must be one of {valid_values}")

    # Add alias for backward compatibility
    @classmethod
    def from_name(cls, quality_str: str) -> 'ChordQualityType':
        """Alias for from_string for backward compatibility."""
        return cls.from_string(quality_str)

    def to_json(self) -> str:
        """Convert the enum to a JSON string."""
        return self.value

    @classmethod
    def from_json(cls, json_value: str) -> 'ChordQualityType':
        """Create an enum instance from a JSON string."""
        try:
            if isinstance(json_value, cls):
                return json_value
            return cls.from_string(json_value)
        except ValueError as e:
            raise ValueError(f"Invalid JSON value: {json_value}. {str(e)}")
        except Exception as e:
            raise ValueError(f"Error deserializing ChordQualityType: {str(e)}")

    def __str__(self) -> str:
        return self.value

    @classmethod
    def get_intervals(cls, quality: Union['ChordQualityType', str]) -> List[int]:
        """Get the intervals for a given chord quality."""
        logging.debug(f"Getting intervals for quality: {quality}")

        # Convert string to ChordQualityType if needed
        if isinstance(quality, str):
            try:
                quality = cls.from_string(quality)
            except ValueError as e:
                raise ValueError(f"Invalid chord quality: {quality}. {str(e)}")

        if quality.value not in CHORD_QUALITY_INTERVALS:
            raise ValueError(f"No intervals defined for chord quality: {quality}. Must be one of {list(CHORD_QUALITY_INTERVALS.keys())}")
        return CHORD_QUALITY_INTERVALS[quality.value]

    @classmethod
    def values(cls) -> List[str]:
        """Get all enum values as strings."""
        return [member.value for member in cls]

    @classmethod
    def get_all_chord_quality_values(cls) -> List[str]:
        """Get all valid chord quality values."""
        return [member.value for member in cls]

    @classmethod
    def get_aliases(cls) -> Dict[str, str]:
        """Get all chord quality aliases."""
        return CHORD_QUALITY_ALIASES

class ScaleDegree(Enum):
    TONIC = 1
    SUPERTONIC = 2
    MEDIANT = 3
    SUBDOMINANT = 4
    DOMINANT = 5
    SUBMEDIANT = 6
    LEADING_TONE = 7

    def __str__(self) -> str:
        return str(self.value)

class ScaleType(StrEnum):
    """Enum representing different scale types."""
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
    WHOLE_TONE = "WHOLE_TONE"
    MINOR_PENTATONIC = "MINOR_PENTATONIC"
    MAJOR_PENTATONIC = "MAJOR_PENTATONIC"
    HARMONIC_MAJOR = "HARMONIC_MAJOR"
    MELODIC_MAJOR = "MELODIC_MAJOR"
    DOUBLE_HARMONIC_MAJOR = "DOUBLE_HARMONIC_MAJOR"

    def __str__(self) -> str:
        return self.value

    def get_intervals(self) -> List[int]:
        """Get the intervals for this scale type."""
        absolute_intervals_map = {
            ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11],
            ScaleType.MINOR: [0, 2, 3, 5, 7, 8, 10],
            ScaleType.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
            ScaleType.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11],
            ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
            ScaleType.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
            ScaleType.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
            ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
            ScaleType.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
            ScaleType.PENTATONIC_MAJOR: [0, 2, 4, 7, 9],
            ScaleType.PENTATONIC_MINOR: [0, 3, 5, 7, 10],
            ScaleType.BLUES: [0, 3, 5, 6, 7, 10],
            ScaleType.CHROMATIC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            ScaleType.WHOLE_TONE: [0, 2, 4, 6, 8, 10],
            ScaleType.MINOR_PENTATONIC: [0, 3, 5, 7, 10],
            ScaleType.MAJOR_PENTATONIC: [0, 2, 4, 7, 9],
            ScaleType.HARMONIC_MAJOR: [0, 2, 4, 5, 7, 8, 11],
            ScaleType.MELODIC_MAJOR: [0, 2, 4, 5, 7, 8, 10],
            ScaleType.DOUBLE_HARMONIC_MAJOR: [0, 1, 4, 5, 7, 8, 11],
        }

        if self not in absolute_intervals_map:
            raise ValueError(f"No intervals defined for scale type: {self}")
        
        # Convert absolute intervals to relative intervals
        absolute_intervals = absolute_intervals_map[self]
        relative_intervals = []
        for i in range(1, len(absolute_intervals)):
            relative_intervals.append(absolute_intervals[i] - absolute_intervals[i-1])
        
        logger.debug(f"Getting intervals for scale type: {self}")
        return relative_intervals

class CustomValidationError(Exception):
    """Custom exception for validation errors."""
    pass