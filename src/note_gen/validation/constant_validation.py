"""Validation functions for constants and enums."""
from typing import Dict, Tuple, Any, List, Optional
from src.note_gen.core.constants import (
    SCALE_INTERVALS,
    COMMON_TIME_SIGNATURES,
    NOTE_PATTERNS,
    RHYTHM_PATTERNS,
    COMMON_PROGRESSIONS,
    COLLECTION_NAMES,
    VALID_KEYS,
    CHORD_INTERVALS,
    DURATION_LIMITS,
    RANGE_LIMITS,
    PATTERN_VALIDATION_LIMITS,
    PATTERN_DEFAULTS
)
from src.note_gen.core.enums import (
    ScaleType, 
    ChordQuality, 
    PatternDirection,
    ValidationLevel,
    PatternType
)
from src.note_gen.schemas.validation_response import ValidationResult

class ConstantValidator:
    """Validator for application constants."""

    @classmethod
    def validate_scale_intervals(cls, intervals: Dict[ScaleType, Tuple[int, ...]]) -> ValidationResult:
        """Validate scale intervals structure."""
        result = ValidationResult(is_valid=True)
        
        for scale_type, interval_tuple in intervals.items():
            if not isinstance(interval_tuple, tuple):
                result.add_error("scale_intervals", f"Scale intervals for {scale_type} must be a tuple")
                continue
            
            if scale_type == ScaleType.CHROMATIC and len(interval_tuple) != 12:
                result.add_error("chromatic_scale", "Chromatic scale must have 12 notes")
                
            if not all(isinstance(i, int) and 0 <= i <= 11 for i in interval_tuple):
                result.add_error("interval_values", f"Invalid intervals in {scale_type}: all must be integers 0-11")
                
        return result

    @classmethod
    def validate_chord_intervals(cls, intervals: Dict[ChordQuality, Tuple[int, ...]]) -> ValidationResult:
        """Validate chord intervals."""
        result = ValidationResult(is_valid=True)
        
        for quality, interval_tuple in intervals.items():
            if not isinstance(interval_tuple, tuple):
                result.add_error("chord_intervals", f"Chord intervals for {quality} must be a tuple")
                continue
                
            if not all(isinstance(i, int) for i in interval_tuple):
                result.add_error("interval_type", f"All intervals for {quality} must be integers")
                
            if not all(0 <= i <= 11 for i in interval_tuple):
                result.add_error("interval_range", f"All intervals for {quality} must be between 0 and 11")
                
        return result

    @classmethod
    def validate_time_signatures(cls) -> ValidationResult:
        """Validate time signatures."""
        result = ValidationResult(is_valid=True)
        
        for ts in COMMON_TIME_SIGNATURES:
            try:
                num_str, denom_str = ts.split('/')
                num = int(num_str)
                denom = int(denom_str)
                
                if num <= 0:
                    result.add_error("time_signature_numerator", f"Invalid numerator in time signature: {ts}")
                if denom not in [2, 4, 8, 16]:
                    result.add_error("time_signature_denominator", f"Invalid denominator in time signature: {ts}")
            except ValueError:
                result.add_error("time_signature_format", f"Invalid time signature format: {ts}")
                
        return result

    @classmethod
    def validate_note_patterns(cls, patterns: Dict[str, Dict[str, Any]]) -> ValidationResult:
        """Validate note patterns structure."""
        result = ValidationResult(is_valid=True)
        required_keys = {"direction", "intervals", "description"}
        
        for pattern_name, pattern in patterns.items():
            if not isinstance(pattern, dict):
                result.add_error("pattern_type", f"Pattern {pattern_name} must be a dictionary")
                continue
                
            missing_keys = required_keys - set(pattern.keys())
            if missing_keys:
                result.add_error("missing_keys", f"Pattern {pattern_name} missing required keys: {missing_keys}")
                
            if "direction" in pattern and not isinstance(pattern["direction"], PatternDirection):
                result.add_error("pattern_direction", f"Invalid direction in pattern {pattern_name}")
                
        return result

    @classmethod
    def validate_rhythm_patterns(cls, patterns: Dict[str, Dict[str, Any]]) -> ValidationResult:
        """Validate rhythm patterns structure."""
        result = ValidationResult(is_valid=True)
        required_keys = {"notes", "total_duration", "description"}
        
        for pattern_name, pattern in patterns.items():
            if not isinstance(pattern, dict):
                result.add_error("pattern_type", f"Pattern {pattern_name} must be a dictionary")
                continue
                
            missing_keys = required_keys - set(pattern.keys())
            if missing_keys:
                result.add_error("missing_keys", f"Pattern {pattern_name} missing required keys: {missing_keys}")
                
            if "notes" in pattern:
                for i, note in enumerate(pattern["notes"]):
                    if not isinstance(note[1], (int, float)) or note[1] < DURATION_LIMITS["min"]:
                        result.add_error("note_duration", f"Invalid duration for note {i} in pattern {pattern_name}")
                        
        return result

    @classmethod
    def validate_progressions(cls) -> ValidationResult:
        """Validate chord progressions."""
        result = ValidationResult(is_valid=True)
        required_keys = {"name", "description", "chords", "tags"}
        
        for prog_name, progression in COMMON_PROGRESSIONS.items():
            if not isinstance(progression, dict):
                result.add_error("progression_type", f"Progression {prog_name} must be a dictionary")
                continue
                
            missing_keys = required_keys - set(progression.keys())
            if missing_keys:
                result.add_error("missing_keys", f"Progression {prog_name} missing required keys: {missing_keys}")
                
            if "chords" in progression:
                for i, chord in enumerate(progression["chords"]):
                    if not isinstance(chord, dict) or "root" not in chord or "quality" not in chord:
                        result.add_error("chord_format", f"Invalid chord format at position {i} in progression {prog_name}")
                        
        return result

    @classmethod
    def validate_pattern_limits(cls) -> ValidationResult:
        """Validate pattern validation limits."""
        result = ValidationResult(is_valid=True)
        
        required_categories = {"name", "duration", "interval"}
        for category in required_categories:
            if category not in PATTERN_VALIDATION_LIMITS:
                result.add_error("missing_category", f"Missing required category: {category}")
                
        for category, limits in PATTERN_VALIDATION_LIMITS.items():
            if "min" in limits and "max" in limits:
                if limits["min"] > limits["max"]:
                    result.add_error(
                        "invalid_range",
                        f"Invalid range for {category}: min ({limits['min']}) > max ({limits['max']})"
                    )
                    
        return result

    @classmethod
    def validate_pattern_defaults(cls) -> ValidationResult:
        """Validate pattern defaults."""
        result = ValidationResult(is_valid=True)
        
        required_fields = {
            "duration", "time_signature", "max_interval_jump",
            "min_duration", "max_duration", "direction"
        }
        
        missing_fields = required_fields - set(PATTERN_DEFAULTS.keys())
        if missing_fields:
            result.add_error("missing_defaults", f"Missing required default fields: {missing_fields}")
            
        if "direction" in PATTERN_DEFAULTS:
            try:
                PatternDirection(PATTERN_DEFAULTS["direction"])
            except ValueError:
                result.add_error("invalid_direction", f"Invalid default direction: {PATTERN_DEFAULTS['direction']}")
                
        return result

    @classmethod
    def validate_all(cls, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate all constants."""
        result = ValidationResult(is_valid=True)
        
        validations = [
            cls.validate_scale_intervals(SCALE_INTERVALS),
            cls.validate_chord_intervals(CHORD_INTERVALS),
            cls.validate_time_signatures(),
            cls.validate_pattern_limits(),
            cls.validate_pattern_defaults()
        ]
        
        for validation in validations:
            if not validation.is_valid:
                result.is_valid = False
                for violation in validation.violations:
                    result.add_error(violation.code, violation.message)
                
        return result
