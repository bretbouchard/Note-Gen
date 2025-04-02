"""Pattern validation module."""
from typing import Dict, Any, List, TypeVar, Type, Optional
from .base_validation import ValidationResult, ValidationViolation
from .pattern_types import PatternValidatable
from ..core.enums import ValidationLevel
from ..core.constants import DURATION_LIMITS
from ..models.rhythm import RhythmPattern

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
    def validate_rhythm_pattern(pattern: RhythmPattern) -> ValidationResult:
        """Validate a rhythm pattern."""
        violations = []

        if not pattern.pattern:
            violations.append(
                ValidationViolation(
                    code="EMPTY_PATTERN",
                    message="Pattern cannot be empty"
                )
            )

        # Validate time signature
        numerator, denominator = pattern.time_signature
        if denominator not in [1, 2, 4, 8, 16, 32, 64]:
            violations.append(
                ValidationViolation(
                    code="INVALID_TIME_SIGNATURE",
                    message="Time signature denominator must be a power of 2"
                )
            )

        # Validate note positions are ordered
        positions = [note.position for note in pattern.pattern]
        if positions != sorted(positions):
            violations.append(
                ValidationViolation(
                    code="UNORDERED_POSITIONS",
                    message="Notes must be ordered by position"
                )
            )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @staticmethod
    def validate_pattern_structure(data: Dict[str, Any]) -> List[ValidationViolation]:
        """Validate the basic structure of a pattern."""
        violations: List[ValidationViolation] = []

        # Only validate required fields that are actually needed
        required_fields = {'name', 'pattern'}  # Remove 'data' from required fields
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            violations.append(ValidationViolation(
                message=f"Missing required fields: {', '.join(missing_fields)}",
                code="MISSING_FIELDS"
            ))

        if 'pattern' in data and not isinstance(data['pattern'], list):
            violations.append(ValidationViolation(
                message="Pattern must be a list",
                code="INVALID_PATTERN_TYPE"
            ))

        return violations

def validate_pattern_structure(data: Dict[str, Any]) -> List[ValidationViolation]:
    """Validate the basic structure of a pattern."""
    violations: List[ValidationViolation] = []

    required_fields = {'name', 'pattern', 'data'}
    missing_fields = required_fields - set(data.keys())
    if missing_fields:
        violations.append(ValidationViolation(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            code="MISSING_FIELDS"
        ))

    if 'pattern' in data and not isinstance(data['pattern'], list):
        violations.append(ValidationViolation(
            message="Pattern must be a list",
            code="INVALID_PATTERN_TYPE"
        ))

    return violations


class PatternValidator:
    """Validator for musical patterns."""

    @staticmethod
    def validate(pattern: Any, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate pattern data."""
        if isinstance(pattern, RhythmPattern):
            return PatternValidation.validate_rhythm_pattern(pattern)
        elif hasattr(pattern, 'validate'):
            try:
                # First check if pattern is empty
                if not getattr(pattern, 'pattern', None):
                    return ValidationResult(
                        is_valid=False,
                        violations=[ValidationViolation(
                            message="Pattern cannot be empty",
                            code="EMPTY_PATTERN"
                        )]
                    )
                pattern.validate()
                return ValidationResult(is_valid=True)
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    violations=[ValidationViolation(message=str(e), code="VALIDATION_ERROR")]
                )
        else:
            return PatternValidation.validate_unknown_pattern()
