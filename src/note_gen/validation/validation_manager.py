
"""Validation manager for musical patterns and structures."""
from typing import Dict, Any, Type, List, Union
from src.note_gen.core.enums import ValidationLevel
from ..schemas.validation_response import ValidationResult, ValidationViolation
from ..models.note import Note
from pydantic import BaseModel

class ValidationManager:
    """Manages validation of musical objects."""
    
    @staticmethod
    def validate_config(config: Dict[str, Any], config_type: str) -> bool:
        """Validate a configuration dictionary."""
        if config_type == "note_sequence":
            required_keys = {"chord_progression", "note_pattern", "rhythm_pattern", "scale_info"}
            return all(key in config for key in required_keys)
        
        return True  # Add more validation types as needed

    @staticmethod
    def validate_model(model: Any, level: ValidationLevel = ValidationLevel.NORMAL) -> bool:
        """Validate a model instance."""
        if hasattr(model, "validate"):
            return model.validate(level)
        return True

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

    @staticmethod
    def validate_sequence(sequence: List[Note], voice_leading_rules: List[Any]) -> ValidationResult:
        """Validate a sequence of notes."""
        result = ValidationResult()
        
        # Basic validation
        if not sequence:
            result.add_error("sequence", "Sequence cannot be empty")
            return result
        
        # Apply voice leading rules
        for rule in voice_leading_rules:
            rule_result = rule.validate(sequence)
            result.merge(rule_result)
        
        return result

    def validate_empty(self) -> ValidationResult:
        """Validate empty data."""
        return ValidationResult(is_valid=True)
