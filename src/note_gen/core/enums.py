"""Centralized enums for the Note Generator application."""
from enum import Enum, auto
from functools import wraps
from warnings import warn
import math
from typing import (
    Tuple, List, Set, Optional, Dict, Any, Union,
    Callable, TypeVar, ParamSpec
)

P = ParamSpec('P')
R = TypeVar('R')

def deprecated(since: str, remove_in: str, use_instead: Optional[str] = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to mark enum values as deprecated."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            name = func.__name__ if hasattr(func, '__name__') else str(func)
            message = f"Warning: {name} is deprecated since version {since} and will be removed in {remove_in}."
            if use_instead:
                message += f" Use {use_instead} instead."
            warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ScaleType(str, Enum):
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

    @property
    def intervals(self) -> Tuple[int, ...]:
        """Get the intervals for this scale type as a tuple."""
        from .constants import SCALE_INTERVALS
        # Get the intervals from SCALE_INTERVALS
        # The intervals are already tuples, so no conversion needed
        return SCALE_INTERVALS[self.value]

class ChordQuality(str, Enum):
    """Chord quality enumeration."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    DIMINISHED = "DIMINISHED"
    AUGMENTED = "AUGMENTED"
    DOMINANT = "DOMINANT"
    DOMINANT_SEVENTH = "DOMINANT_SEVENTH"
    MAJOR_SEVENTH = "MAJOR_SEVENTH"
    MINOR_SEVENTH = "MINOR_SEVENTH"
    DIMINISHED_SEVENTH = "DIMINISHED_SEVENTH"
    HALF_DIMINISHED_SEVENTH = "HALF_DIMINISHED_SEVENTH"
    SUSPENDED_SECOND = "SUSPENDED_SECOND"
    SUSPENDED_FOURTH = "SUSPENDED_FOURTH"
    MAJOR_NINTH = "MAJOR_NINTH"
    MINOR_NINTH = "MINOR_NINTH"
    MAJOR_ELEVENTH = "MAJOR_ELEVENTH"
    MINOR_ELEVENTH = "MINOR_ELEVENTH"
    DOMINANT_ELEVENTH = "DOMINANT_ELEVENTH"

    @classmethod
    def from_string(cls, s: str) -> 'ChordQuality':
        """Convert string to ChordQuality."""
        mapping = {
            '': cls.MAJOR,
            'maj': cls.MAJOR,
            'm': cls.MINOR,
            'dim': cls.DIMINISHED,
            'aug': cls.AUGMENTED,
            '7': cls.DOMINANT_SEVENTH,
            'maj7': cls.MAJOR_SEVENTH,
            'm7': cls.MINOR_SEVENTH
        }
        if s not in mapping:
            raise ValueError(f"Unknown chord quality: {s}")
        return mapping[s]

    @classmethod
    def get_intervals(cls, quality: 'ChordQuality') -> List[int]:
        """Get the intervals for a given chord quality."""
        QUALITY_INTERVALS: Dict[ChordQuality, List[int]] = {
            cls.MAJOR: [0, 4, 7],
            cls.MINOR: [0, 3, 7],
            cls.DIMINISHED: [0, 3, 6],
            cls.AUGMENTED: [0, 4, 8],
            cls.DOMINANT_SEVENTH: [0, 4, 7, 10],
            cls.MAJOR_SEVENTH: [0, 4, 7, 11],
            cls.MINOR_SEVENTH: [0, 3, 7, 10],
            cls.DIMINISHED_SEVENTH: [0, 3, 6, 9],
            cls.HALF_DIMINISHED_SEVENTH: [0, 3, 6, 10],
            cls.SUSPENDED_SECOND: [0, 2, 7],
            cls.SUSPENDED_FOURTH: [0, 5, 7],
            cls.MAJOR_ELEVENTH: [0, 4, 7, 11, 14, 17],
            cls.MINOR_ELEVENTH: [0, 3, 7, 10, 14, 17],
            cls.DOMINANT_ELEVENTH: [0, 4, 7, 10, 14, 17],
            cls.DOMINANT: [0, 4, 7, 10],  # Same as dominant seventh
            cls.MAJOR_NINTH: [0, 4, 7, 11, 14],
            cls.MINOR_NINTH: [0, 3, 7, 10, 14]
        }

        if quality not in QUALITY_INTERVALS:
            raise ValueError(f"Invalid chord quality: {quality}")

        return QUALITY_INTERVALS[quality]

    def __str__(self) -> str:
        return self.name.replace('ChordQuality.', '')


class TimeSignatureType(str, Enum):
    """Types of time signatures."""
    SIMPLE = "simple"
    COMPOUND = "compound"

    @classmethod
    def validate(cls, time_signature: Union[str, Tuple[int, int]]) -> 'TimeSignatureType':
        """Validate and return the time signature type."""
        try:
            if isinstance(time_signature, tuple):
                numerator, denominator = time_signature
            else:
                numerator, denominator = map(int, str(time_signature).split('/'))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid time signature format: {time_signature}")

        if denominator not in [2, 4, 8, 16]:
            raise ValueError("Denominator must be 2, 4, 8, or 16")

        if numerator <= 0 or denominator <= 0:
            raise ValueError("Time signature components must be positive")

        if numerator not in [2, 3, 4, 6, 9, 12]:
            raise ValueError("Numerator must be 2, 3, 4, 6, 9, or 12 for simple and compound meters")

        return cls.COMPOUND if numerator in [6, 9, 12] else cls.SIMPLE

    @classmethod
    def validate_pattern_duration(cls, pattern_duration: float, time_signature: Tuple[int, int]) -> bool:
        """Validate pattern duration against time signature."""
        numerator, denominator = time_signature
        expected_duration = float(numerator) / denominator * 4.0
        if not math.isclose(pattern_duration, expected_duration, rel_tol=1e-9):
            raise ValueError(f"Pattern duration {pattern_duration} does not match time signature {numerator}/{denominator}")
        return True

    @classmethod
    def get_valid_signatures(cls) -> Dict[str, 'TimeSignatureType']:
        """Return valid time signatures and their types."""
        return {
            "2/4": cls.SIMPLE,
            "3/4": cls.SIMPLE,
            "4/4": cls.SIMPLE,
            "6/8": cls.COMPOUND,
            "9/8": cls.COMPOUND,
            "12/8": cls.COMPOUND
        }

    @classmethod
    def from_time_signature(cls, numerator: int, denominator: int) -> 'TimeSignatureType':
        """Determine time signature type from numerator and denominator."""
        return cls.COMPOUND if numerator in [6, 9, 12] else cls.SIMPLE


class PatternDirection(str, Enum):
    """Direction for pattern generation."""
    UP = "up"
    DOWN = "down"
    RANDOM = "random"
    ALTERNATE = "alternate"
    CIRCULAR = "circular"

    @classmethod
    def validate_sequence(cls, directions: List[str]) -> bool:
        """Validate a sequence of directions."""
        valid_values = set(member.value for member in cls)
        if not all(direction in valid_values for direction in directions):
            invalid = [d for d in directions if d not in valid_values]
            raise ValueError(f"Invalid direction(s): {invalid}")
        return True


class SequenceType(str, Enum):
    """Sequence type enum."""
    CIRCULAR = "CIRCULAR"
    LINEAR = "LINEAR"
    RANDOM = "RANDOM"
    RHYTHMIC = "RHYTHMIC"


class ErrorType(str, Enum):
    """Error type enum."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CHORD_ERROR = "CHORD_ERROR"
    SCALE_ERROR = "SCALE_ERROR"
    PATTERN_ERROR = "PATTERN_ERROR"


class DatabaseCollectionType(str, Enum):
    """Types of database collections."""
    CHORD_PROGRESSIONS = "chord_progressions"
    NOTE_PATTERNS = "note_patterns"
    RHYTHM_PATTERNS = "rhythm_patterns"
    MIGRATIONS = "migrations"


class ValidationLevel(str, Enum):
    """Validation level for pattern generation."""
    STRICT = "strict"
    NORMAL = "normal"
    RELAXED = "relaxed"
    LENIENT = "lenient"  # Added LENIENT level


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

    @classmethod
    def get_accent_value(cls, accent_type: 'AccentType') -> float:
        """Get the velocity multiplier for an accent type."""
        values = {
            cls.NORMAL: 1.0,
            cls.STRONG: 1.2,
            cls.WEAK: 0.8,
            cls.GHOST: 0.5
        }
        return values[accent_type]

    @classmethod
    def validate_accent_pattern(cls, pattern: List['AccentType']) -> bool:
        """Validate an accent pattern."""
        if not pattern:
            raise ValueError("Accent pattern cannot be empty")

        if not all(isinstance(accent, cls) for accent in pattern):
            raise ValueError("All accents must be AccentType instances")

        return True


class VoiceLeadingRule(str, Enum):
    """Rules for voice leading validation."""
    PARALLEL_FIFTHS = "parallel_fifths"
    PARALLEL_OCTAVES = "parallel_octaves"
    VOICE_CROSSING = "voice_crossing"
    VOICE_SPACING = "voice_spacing"
    MELODIC_MOTION = "melodic_motion"
    RESOLUTION = "resolution"
    CONTRARY_MOTION = "contrary_motion"

    @classmethod
    def get_rule_severity(cls, rule: 'VoiceLeadingRule') -> str:
        """Get the severity level for a voice leading rule."""
        severities: Dict[VoiceLeadingRule, str] = {
            cls.PARALLEL_FIFTHS: "warning",
            cls.PARALLEL_OCTAVES: "warning",
            cls.VOICE_CROSSING: "error",
            cls.VOICE_SPACING: "warning"
        }
        return severities[rule]

    @classmethod
    def validate_progression(cls, progression: List[Any], rules: Optional[Set['VoiceLeadingRule']] = None) -> List[Dict[str, Any]]:
        """Validate a chord progression against voice leading rules."""
        if rules is None:
            rules = set(cls)

        violations: List[Dict[str, Any]] = []
        # Implementation would check for specific voice leading violations
        # and return a list of violation dictionaries
        return violations

    def __str__(self) -> str:
        """Return uppercase string representation."""
        return self.value.upper()


class TransformationType(str, Enum):
    """Types of pattern transformations."""
    TRANSPOSE = "transpose"
    INVERT = "invert"
    RETROGRADE = "retrograde"
    REVERSE = "reverse"
    AUGMENT = "augment"
    DIMINISH = "diminish"


class NoteModificationType(str, Enum):
    """Types of note modifications."""
    TRANSPOSE = "transpose"
    INVERT = "invert"
    RETROGRADE = "retrograde"
    AUGMENT = "augment"
    DIMINISH = "diminish"

    @classmethod
    def validate_modification(cls, mod_type: 'NoteModificationType', value: Any) -> bool:
        """Validate a modification type and its value."""
        if mod_type == cls.TRANSPOSE:
            return isinstance(value, int)
        elif mod_type == cls.INVERT:
            return isinstance(value, bool)
        elif mod_type == cls.RETROGRADE:
            return isinstance(value, bool)
        elif mod_type in (cls.AUGMENT, cls.DIMINISH):
            return isinstance(value, (int, float)) and value > 0
        return False


class PatternType(str, Enum):
    """Types of musical patterns."""
    MELODIC = "melodic"
    RHYTHMIC = "rhythmic"
    HARMONIC = "harmonic"
    COMBINED = "combined"
    CUSTOM = "custom"

    @classmethod
    def validate_pattern_type(cls, pattern_type: str) -> bool:
        """Validate if a pattern type is valid."""
        return pattern_type in [member.value for member in cls]
