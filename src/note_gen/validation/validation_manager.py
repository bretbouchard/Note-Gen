
"""Validation manager for musical patterns and structures."""
from typing import List, Type, Dict, Any, Union, TYPE_CHECKING
from ..core.enums import ValidationLevel
from ..schemas.validation_response import ValidationResult, ValidationViolation
from pydantic import BaseModel

if TYPE_CHECKING:
    from ..models.patterns import Pattern, NotePattern, RhythmPattern

class ValidationManager:
    """Manages validation of musical patterns."""

    @staticmethod
    def validate_pattern(pattern: 'Pattern', level: ValidationLevel) -> ValidationResult:
        """
        Validate a pattern instance.
        
        Args:
            pattern: Pattern instance to validate
            level: Validation level to apply
            
        Returns:
            ValidationResult containing validation status and violations
        """
        from ..models.patterns import NotePattern, RhythmPattern  # Import here to avoid circular import
        
        violations: List[ValidationViolation] = []
        
        try:
            # Basic validation based on pattern type
            if isinstance(pattern, NotePattern):
                # Note pattern specific validation
                if level >= ValidationLevel.NORMAL:
                    note_range_result = pattern.validate_note_range()
                    violations.extend(note_range_result.violations)
                
                if level == ValidationLevel.STRICT:
                    pattern.validate_voice_leading()
                    pattern.validate_consonance()
                    pattern.validate_parallel_motion()
                    
            elif isinstance(pattern, RhythmPattern):
                # Rhythm pattern specific validation
                if not pattern.pattern:
                    violations.append(
                        ValidationViolation(
                            message="Pattern must contain at least one note",
                            code="EMPTY_PATTERN"
                        )
                    )
                    
                # Validate time signature
                numerator, denominator = pattern.time_signature
                if denominator not in [2, 4, 8, 16]:
                    violations.append(
                        ValidationViolation(
                            message="Invalid time signature denominator",
                            code="INVALID_TIME_SIGNATURE"
                        )
                    )
            else:
                violations.append(
                    ValidationViolation(
                        message="Unknown pattern type",
                        code="UNKNOWN_PATTERN_TYPE"
                    )
                )
                
        except Exception as e:
            violations.append(
                ValidationViolation(
                    message=str(e),
                    code="VALIDATION_ERROR"
                )
            )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @staticmethod
    def validate_model(
        model_class: Type[Union['Pattern', BaseModel]],
        data: Dict[str, Any],
        level: ValidationLevel
    ) -> ValidationResult:
        """
        Validate model data.
        
        Args:
            model_class: Class to validate against (Pattern or related models)
            data: Data to validate
            level: Validation level to apply
            
        Returns:
            ValidationResult containing validation status and violations
        """
        from ..models.patterns import Pattern  # Import here to avoid circular import
        
        violations: List[ValidationViolation] = []
        
        try:
            # Create instance using model_validate
            instance = model_class.model_validate(data)
            
            # Only run pattern validation if instance is a Pattern
            if isinstance(instance, Pattern):
                pattern_result = ValidationManager.validate_pattern(instance, level)
                violations.extend(pattern_result.violations)
                
        except Exception as e:
            violations.append(
                ValidationViolation(
                    message=str(e),
                    code="MODEL_VALIDATION_ERROR"
                )
            )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @classmethod
    def validate_sequence(cls, sequence: Any) -> ValidationResult:
        """Validate a musical sequence."""
        violations: List[ValidationViolation] = []
        
        if not sequence:
            violations.append(
                ValidationViolation(
                    message="Sequence cannot be empty",
                    code="EMPTY_SEQUENCE"
                )
            )
            
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    def validate_empty(self) -> ValidationResult:
        """Validate empty data."""
        return ValidationResult(is_valid=True)
