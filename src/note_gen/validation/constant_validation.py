"""Validation functions for constants and enums."""
from typing import Dict, Tuple, Any
from src.note_gen.core.constants import (
    SCALE_INTERVALS,
    COMMON_TIME_SIGNATURES,
    NOTE_PATTERNS,
    RHYTHM_PATTERNS,
    COMMON_PROGRESSIONS,
    COLLECTION_NAMES,
    VALID_KEYS
)
from src.note_gen.core.enums import ScaleType, ChordQuality, PatternDirection

def validate_scale_intervals(intervals: Dict[ScaleType, Tuple[int, ...]]) -> None:
    """Validate scale intervals structure."""
    for scale_type, interval_tuple in intervals.items():
        if not isinstance(interval_tuple, tuple):
            raise AssertionError(f"Scale intervals for {scale_type} must be a tuple")
        
        if scale_type == ScaleType.CHROMATIC and len(interval_tuple) != 12:
            raise AssertionError("Chromatic scale must have 12 notes")

def validate_chord_intervals(intervals: Dict[ChordQuality, Tuple[int, ...]]) -> None:
    """Validate chord intervals."""
    for quality, interval_tuple in intervals.items():
        if not isinstance(interval_tuple, tuple):
            raise AssertionError(f"Chord intervals for {quality} must be a tuple")
        
        if not all(isinstance(i, int) for i in interval_tuple):
            raise AssertionError("All intervals must be integers")
        
        if not all(0 <= i <= 11 for i in interval_tuple):
            raise AssertionError("All intervals must be between 0 and 11")

def validate_time_signatures() -> None:
    """Validate time signatures."""
    for ts in COMMON_TIME_SIGNATURES:
        num, denom = map(int, ts.split('/'))
        assert num > 0, f"Invalid numerator in time signature: {ts}"
        assert denom in [2, 4, 8, 16], f"Invalid denominator in time signature: {ts}"

def validate_patterns() -> None:
    """Validate note and rhythm patterns."""
    for pattern_name, pattern in NOTE_PATTERNS.items():
        assert isinstance(pattern, list), f"Pattern {pattern_name} must be a list"
        assert all(isinstance(n, int) for n in pattern), f"Non-integer note in {pattern_name}"
        
    for pattern_name, pattern in RHYTHM_PATTERNS.items():
        assert isinstance(pattern, list), f"Pattern {pattern_name} must be a list"
        assert all(isinstance(d, float) and d > 0 for d in pattern), \
            f"Invalid duration in {pattern_name}"

def validate_progressions() -> None:
    """Validate chord progressions."""
    valid_numerals = {'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii',
                     'I', 'II', 'III', 'IV', 'V', 'VI', 'VII'}
    
    for prog_name, progression in COMMON_PROGRESSIONS.items():
        assert isinstance(progression, list), f"Progression {prog_name} must be a list"
        for numeral in progression:
            base_numeral = numeral.rstrip('°7').rstrip('7')
            assert base_numeral in valid_numerals, f"Invalid numeral {numeral} in {prog_name}"

def validate_constants() -> None:
    """Validate all constants."""
    validate_scale_intervals(SCALE_INTERVALS)
    validate_chord_intervals(CHORD_INTERVALS)
    validate_progressions(COMMON_PROGRESSIONS)
    validate_note_patterns(NOTE_PATTERNS)
    validate_rhythm_patterns(RHYTHM_PATTERNS)
    validate_time_signatures()
    validate_patterns()
    validate_progressions()
