from typing import List, Optional
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

class ChordQualityType(Enum):
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
    INVALID = 'INVALID'
    INVALID_QUALITY = "INVALID_QUALITY"

    INTERVALS = {
        'MAJOR': [0, 4, 7],
        'MINOR': [0, 3, 7],
        'DIMINISHED': [0, 3, 6],
        'AUGMENTED': [0, 4, 8],
        'DOMINANT': [0, 4, 7, 10],
        'DOMINANT7': [0, 4, 7, 10],
        'MAJOR7': [0, 4, 7, 11],
        'MINOR7': [0, 3, 7, 10],
        'DIMINISHED7': [0, 3, 6, 9],
        'HALF_DIMINISHED7': [0, 3, 6, 10],
        'MAJOR9': [0, 4, 7, 11, 14],
        'MINOR9': [0, 3, 7, 10, 14],
        'DOMINANT9': [0, 4, 7, 10, 14],
        'AUGMENTED7': [0, 4, 8, 10],
        'MAJOR11': [0, 4, 7, 11, 14, 17],
        'MINOR11': [0, 3, 7, 10, 14, 17],
        'DOMINANT11': [0, 4, 7, 10, 14, 17],
        'SUS2': [0, 2, 7],
        'SUS4': [0, 5, 7],
        'SEVEN_SUS4': [0, 5, 7, 10],
        'FLAT5': [0, 4, 6],
        'FLAT7': [0, 4, 7, 9],
        'SHARP5': [0, 4, 8],
        'SHARP7': [0, 4, 7, 11],
        'INVALID': []
    }

    # Mapping of string representations to enum values
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
        'dominant': 'DOMINANT',
        'dominant7': 'DOMINANT7',
        'maj7': 'MAJOR7',
        'm7': 'MINOR7',
        'dim7': 'DIMINISHED7',
        'ø7': 'HALF_DIMINISHED7',
        'm7b5': 'HALF_DIMINISHED7',
        '7': 'DOMINANT7',
        '7sus4': 'SEVEN_SUS4',
        'b5': 'FLAT5',
        'b7': 'FLAT7',
        '#5': 'SHARP5',
        '#7': 'SHARP7',
        '+': 'AUGMENTED',
        '°': 'DIMINISHED',
    }

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQualityType':
        if not quality_str:
            logger.error("Quality string cannot be empty")
            raise ValueError("Quality string cannot be empty")
        quality_str = str(quality_str).strip().upper()  # Convert to uppercase for comparison
        logger.debug(f"Processing quality string: {quality_str}")
        if quality_str in cls._member_map_:
            return cls[quality_str]
        else:
            raise ValueError(f"Invalid quality string: {quality_str}")

    def to_json(self) -> str:
        try:
            print(f"Serializing ChordQualityType: {self} with value: {self.value}")  
            if isinstance(self.value, str):
                return self.value  
            elif isinstance(self.value, int):
                return str(self.value)  
            return self.name  
        except Exception as e:
            raise CustomValidationError(f"Error serializing ChordQualityType: {str(e)}")

    @classmethod
    def from_json(cls, json_value: str) -> 'ChordQualityType':
        print(f"Deserializing from JSON value: '{json_value}'")  
        if json_value in cls.CHORD_QUALITY_ALIASES:
            json_value = cls.CHORD_QUALITY_ALIASES[json_value]
        try:
            result = cls[json_value.upper()]
            print(f"Converted JSON value '{json_value}' to {result}")  
            return result
        except KeyError:
            raise CustomValidationError(f"Invalid JSON value: {json_value}")
        except Exception as e:
            raise CustomValidationError(f"Error deserializing ChordQualityType: {str(e)}")

    def __str__(self) -> str:
        return self.value

    @classmethod
    def get_intervals(cls, quality: 'ChordQualityType') -> List[int]:
        if isinstance(quality, ChordQualityType) and quality.value in cls.INTERVALS:
            return cls.INTERVALS[quality.value]
        raise ValueError(f"Invalid chord quality: {quality}")

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

    def __str__(self) -> str:
        return str(self.value)

class CustomValidationError(Exception):
    """Custom exception for validation errors."""
    pass