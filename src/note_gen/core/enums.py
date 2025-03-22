"""Centralized enums for the Note Generator application."""
from enum import Enum, auto
from typing import Tuple


class ScaleType(Enum):
    """Scale types supported by the system."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    HARMONIC_MINOR = "HARMONIC_MINOR"
    MELODIC_MINOR = "MELODIC_MINOR"
    DORIAN = "DORIAN"
    PHRYGIAN = "PHRYGIAN"
    LYDIAN = "LYDIAN"
    MIXOLYDIAN = "MIXOLYDIAN"
    LOCRIAN = "LOCRIAN"
    CHROMATIC = "CHROMATIC"

    @classmethod
    def get_scale_intervals(cls, scale_type: 'ScaleType') -> tuple[int, ...]:
        """Get the intervals for a given scale type."""
        from src.note_gen.core.constants import SCALE_INTERVALS
        return SCALE_INTERVALS[scale_type]


class ChordQuality(str, Enum):
    """Chord qualities supported by the system."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    DIMINISHED = "DIMINISHED"
    AUGMENTED = "AUGMENTED"
    DOMINANT = "DOMINANT"
    MAJOR7 = "MAJOR7"
    MINOR7 = "MINOR7"
    MINOR9 = "MINOR9"
    DOMINANT7 = "DOMINANT7"
    DIMINISHED7 = "DIMINISHED7"
    HALF_DIMINISHED7 = "HALF_DIMINISHED7"
    MAJOR9 = "MAJOR9"
    MINOR_SEVENTH = "MINOR_SEVENTH"
    MAJOR_SEVENTH = "MAJOR_SEVENTH"
    DOMINANT_SEVENTH = "DOMINANT_SEVENTH"
    DIMINISHED_SEVENTH = "DIMINISHED_SEVENTH"
    HALF_DIMINISHED_SEVENTH = "HALF_DIMINISHED_SEVENTH"
    MINOR_MAJOR_SEVENTH = "MINOR_MAJOR_SEVENTH"
    AUGMENTED_SEVENTH = "AUGMENTED_SEVENTH"
    AUGMENTED_MAJOR_SEVENTH = "AUGMENTED_MAJOR_SEVENTH"
    SUSPENDED_SECOND = "SUSPENDED_SECOND"
    SUSPENDED_FOURTH = "SUSPENDED_FOURTH"
    HALF_DIMINISHED = "HALF_DIMINISHED"
    FULL_DIMINISHED = "FULL_DIMINISHED"
    DOMINANT9 = "DOMINANT9"
    MAJOR11 = "MAJOR11"
    MINOR11 = "MINOR11"
    DIMINISHED11 = "DIMINISHED11"
    AUGMENTED11 = "AUGMENTED11"

    @classmethod
    def from_string(cls, value: str) -> 'ChordQuality':
        """Convert string to ChordQuality enum."""
        # Handle variations for chord qualities
        variations = {
            'maj7': 'MAJOR_SEVENTH',
            'major': 'MAJOR',
            'min7': 'MINOR7',
            'minor': 'MINOR',
            'dim': 'DIMINISHED',
            'aug': 'AUGMENTED',
            'dom7': 'DOMINANT7',
            'dom': 'DOMINANT'
        }
        value = variations.get(value.lower(), value.lower())
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid chord quality: {value}")

    def get_intervals(self) -> Tuple[int, ...]:
        """Get the intervals for this chord quality."""
        return CHORD_INTERVALS.get(self, ())


class TimeSignatureType(str, Enum):
    """Types of time signatures."""
    SIMPLE = "simple"
    COMPOUND = "compound"

    @classmethod
    def validate(cls, time_signature: str) -> 'TimeSignatureType':
        """Validate and return the time signature type."""
        numerator, denominator = map(int, time_signature.split('/'))
        if denominator in [2, 4] and numerator in [2, 3, 4]:
            return cls.SIMPLE
        elif denominator == 8 and numerator in [6, 9, 12]:
            return cls.COMPOUND
        raise ValueError(f"Invalid time signature: {time_signature}")


class PatternDirection(str, Enum):
    """Direction for pattern generation."""
    UP = "up"
    DOWN = "down"
    RANDOM = "random"
    ALTERNATE = "alternate"
    CIRCULAR = "circular"


class NoteModificationType(str, Enum):
    """Types of note modifications."""
    TRANSPOSE = "transpose"
    INVERT = "invert"
    RETROGRADE = "retrograde"
    AUGMENT = "augment"
    DIMINISH = "diminish"


class SequenceType(str, Enum):
    """Types of musical sequences."""
    LINEAR = "linear"
    CIRCULAR = "circular"
    RANDOM = "random"


class ErrorType(str, Enum):
    """Types of errors in the system."""
    VALIDATION = "validation"
    DATABASE = "database"
    PATTERN = "pattern"
    SCALE = "scale"
    CHORD = "chord"
    GENERAL = "general"


class DatabaseCollectionType(str, Enum):
    """Types of database collections."""
    CHORD_PROGRESSIONS = "chord_progressions"
    NOTE_PATTERNS = "note_patterns"
    RHYTHM_PATTERNS = "rhythm_patterns"
    MIGRATIONS = "migrations"


class ValidationLevel(str, Enum):
    """Validation levels for pattern validation."""
    STRICT = "strict"
    NORMAL = "normal"
    LENIENT = "lenient"


class PatternComplexity(str, Enum):
    """Complexity levels for patterns."""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    ADVANCED = "advanced"


class AccentType(str, Enum):
    """Types of accents in rhythm patterns."""
    NORMAL = "normal"
    STRONG = "strong"
    WEAK = "weak"
    GHOST = "ghost"


class VoiceLeadingRule(str, Enum):
    """Voice leading rules for chord progressions."""
    PARALLEL_FIFTHS = "parallel_fifths"
    PARALLEL_OCTAVES = "parallel_octaves"
    VOICE_CROSSING = "voice_crossing"
    VOICE_SPACING = "voice_spacing"
