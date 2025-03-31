"""Pattern validation module."""
from typing import Dict, Any, List, TypeVar, Type, Optional
from .base_validation import ValidationResult, ValidationViolation
from .pattern_types import PatternValidatable
from ..core.enums import ValidationLevel
from ..core.constants import DURATION_LIMITS
from ..models.patterns import NotePattern, NotePatternData
from .validation_manager import ValidationManager

T = TypeVar('T')

class PatternValidation:
    """Pattern validation class."""
    
    @staticmethod
    def validate_unknown_pattern() -> ValidationResult:
        """Create validation result for unknown pattern type."""
        violation = ValidationViolation(
            message="Unknown pattern type",
            code="UNKNOWN_PATTERN_TYPE"
        )
        return ValidationResult(
            is_valid=False,
            violations=[violation]
        )

    @staticmethod
    def validate_rhythm_pattern(pattern_data: Dict[str, Any]) -> ValidationResult:
        """Validate a rhythm pattern."""
        violations: List[ValidationViolation] = []
        
        # Validate pattern notes exist
        if not pattern_data.get('pattern'):
            violations.append(
                ValidationViolation(
                    message="Pattern must contain at least one note",
                    code="EMPTY_PATTERN"
                )
            )
            
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

def validate_pattern_structure(pattern_data: Dict[str, Any]) -> List[str]:
    """Validate the basic structure of a pattern."""
    violations = []
    
    required_fields = ['name', 'pattern', 'data']
    for field in required_fields:
        if field not in pattern_data:
            violations.append(f"Missing required field: {field}")
    
    if 'pattern' in pattern_data:
        if not isinstance(pattern_data['pattern'], list):
            violations.append("Pattern must be a list")
            
    if 'data' in pattern_data:
        if not isinstance(pattern_data['data'], dict):
            violations.append("Data must be a dictionary")
            
    return violations

class PatternValidator:
    """Validator for musical patterns."""
    
    @staticmethod
    def validate(pattern: Any, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate pattern data."""
        if isinstance(pattern, PatternValidatable):
            return PatternValidator._validate_note_pattern(pattern, level)
        elif hasattr(pattern, 'pattern') and hasattr(pattern, 'time_signature'):
            return PatternValidator._validate_rhythm_pattern(pattern, level)
        else:
            return PatternValidation.validate_unknown_pattern()

    @staticmethod
    def _validate_note_pattern(pattern: PatternValidatable, level: ValidationLevel) -> ValidationResult:
        """Validate note pattern."""
        violations = []
        
        if level >= ValidationLevel.NORMAL:
            try:
                pattern.validate_voice_leading()
            except Exception as e:
                violations.append(str(e))

            range_result = pattern.validate_note_range()
            violations.extend([v.message for v in range_result.violations])

        if level == ValidationLevel.STRICT:
            try:
                pattern.validate_consonance()
            except Exception as e:
                violations.append(str(e))

            try:
                pattern.validate_parallel_motion()
            except Exception as e:
                violations.append(str(e))

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=[ValidationViolation(message=v, code="VALIDATION_ERROR") for v in violations]
        )

    @staticmethod
    def _validate_rhythm_pattern(pattern: Any, level: ValidationLevel) -> ValidationResult:
        """Validate rhythm pattern."""
        violations = []
        
        if not pattern.pattern:
            violations.append(
                ValidationViolation(
                    message="Pattern cannot be empty",
                    code="EMPTY_PATTERN"
                )
            )
            
        if level >= ValidationLevel.NORMAL:
            numerator, denominator = pattern.time_signature
            if denominator not in [2, 4, 8, 16]:
                violations.append(
                    ValidationViolation(
                        message="Invalid time signature denominator",
                        code="INVALID_TIME_SIGNATURE"
                    )
                )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @staticmethod
    def validate_pattern(pattern: NotePattern) -> ValidationResult:
        violations: List[ValidationViolation] = []
        
        try:
            # Validate voice leading
            pattern.validate_voice_leading()
            
            # Validate note range
            if pattern.data.octave_range:
                min_octave, max_octave = pattern.data.octave_range
                for note in pattern.pattern:
                    if note.octave < min_octave or note.octave > max_octave:
                        violations.append(
                            ValidationViolation(
                                code="NOTE_RANGE_ERROR",
                                message=f"Note {note} is outside octave range {min_octave}-{max_octave}"
                            )
                        )
            
            # Validate scale compatibility if scale_info is present
            if pattern.scale_info:
                for note in pattern.pattern:
                    if not pattern.scale_info.is_note_in_scale(note):
                        violations.append(
                            ValidationViolation(
                                code="SCALE_COMPATIBILITY_ERROR",
                                message=f"Note {note} is not in scale {pattern.scale_info}"
                            )
                        )
            
        except ValueError as e:
            violations.append(
                ValidationViolation(
                    code="VALIDATION_ERROR",
                    message=str(e)
                )
            )
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )
