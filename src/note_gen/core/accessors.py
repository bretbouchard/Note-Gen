"""Type-safe accessors for enums and constants."""
from typing import List, Tuple, Optional
from .enums import (
    ScaleType, 
    ChordQuality,
    TimeSignatureType
)
from .constants import (
    SCALE_INTERVALS,
    VALID_KEYS,
    COMMON_TIME_SIGNATURES,
    COLLECTION_NAMES,
    NOTE_PATTERNS,
    RHYTHM_PATTERNS,
    DEFAULT_KEY,
    DEFAULT_SCALE_TYPE,
    COMMON_PROGRESSIONS
)

class ScaleAccessor:
    @staticmethod
    def get_intervals(scale_type: ScaleType) -> Tuple[int, ...]:
        """Get intervals for a scale type."""
        return SCALE_INTERVALS[scale_type]

    @staticmethod
    def is_valid_scale(scale_type: str) -> bool:
        """Check if a scale type is valid."""
        return scale_type in ScaleType.__members__

class MusicTheoryAccessor:
    @staticmethod
    def get_valid_keys() -> List[str]:
        """Get all valid musical keys."""
        return VALID_KEYS

    @staticmethod
    def get_time_signatures() -> List[str]:
        """Get all supported time signatures."""
        return COMMON_TIME_SIGNATURES

class DatabaseAccessor:
    @staticmethod
    def get_collection_name(key: str) -> str:
        """Get collection name by key."""
        return COLLECTION_NAMES[key]

class ProgressionAccessor:
    @staticmethod
    def get_progression(name: str) -> List[str]:
        """Get a chord progression by name."""
        if name not in COMMON_PROGRESSIONS:
            raise ValueError(f"Invalid progression name: {name}")
        return COMMON_PROGRESSIONS[name]

    @staticmethod
    def list_progressions() -> List[str]:
        """List all available progression names."""
        return list(COMMON_PROGRESSIONS.keys())
