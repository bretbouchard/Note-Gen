"""Validation functions for rhythm-related data."""
from typing import Dict, Any, List
from src.note_gen.core.constants import DURATIONS, DURATION_LIMITS
from src.note_gen.core.enums import ValidationLevel, AccentType
from src.note_gen.validation.base_validation import ValidationResult, ValidationError
from src.note_gen.validation.rhythm_note_validation import RhythmNoteValidator
from src.note_gen.models.rhythm_note import RhythmNote

def validate_rhythm_data(data: Dict[str, Any], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
    """
    Validate rhythm data structure and values.
    
    Args:
        data: Dictionary containing rhythm data
        level: Validation level to apply
    
    Returns:
        ValidationResult with validation status and any errors
    """
    errors: List[ValidationError] = []
    
    # Basic structure validation
    if not isinstance(data, dict):
        return ValidationResult(is_valid=False, errors=[
            ValidationError(field="data", message="Data must be a dictionary")
        ])

    required_fields = {"duration", "pattern", "time_signature"}
    missing_fields = required_fields - set(data.keys())
    if missing_fields:
        errors.append(ValidationError(
            field="structure",
            message=f"Missing required fields: {', '.join(missing_fields)}"
        ))

    # Duration validation
    if "duration" in data:
        duration = data["duration"]
        if not isinstance(duration, (int, float)):
            errors.append(ValidationError(
                field="duration",
                message="Duration must be a number"
            ))
        elif not (DURATION_LIMITS["min"] <= duration <= DURATION_LIMITS["max"]):
            errors.append(ValidationError(
                field="duration",
                message=f"Duration must be between {DURATION_LIMITS['min']} and {DURATION_LIMITS['max']}"
            ))

    # Pattern validation
    if "pattern" in data:
        pattern = data["pattern"]
        if not isinstance(pattern, list):
            errors.append(ValidationError(
                field="pattern",
                message="Pattern must be a list"
            ))
        else:
            # Validate pattern elements
            for i, element in enumerate(pattern):
                if not isinstance(element, dict):
                    errors.append(ValidationError(
                        field=f"pattern[{i}]",
                        message="Pattern element must be a dictionary"
                    ))
                else:
                    # Validate element structure
                    if "duration" not in element:
                        errors.append(ValidationError(
                            field=f"pattern[{i}]",
                            message="Pattern element missing duration"
                        ))
                    if "accent" in element and not isinstance(element["accent"], (str, AccentType)):
                        errors.append(ValidationError(
                            field=f"pattern[{i}].accent",
                            message="Invalid accent type"
                        ))

    # Time signature validation
    if "time_signature" in data:
        time_sig = data["time_signature"]
        if not isinstance(time_sig, str):
            errors.append(ValidationError(
                field="time_signature",
                message="Time signature must be a string"
            ))
        else:
            try:
                numerator, denominator = map(int, time_sig.split('/'))
                if numerator <= 0 or denominator <= 0:
                    errors.append(ValidationError(
                        field="time_signature",
                        message="Time signature components must be positive"
                    ))
                if denominator not in [2, 4, 8, 16]:
                    errors.append(ValidationError(
                        field="time_signature",
                        message="Invalid time signature denominator"
                    ))
            except ValueError:
                errors.append(ValidationError(
                    field="time_signature",
                    message="Invalid time signature format"
                ))

    # Additional validation for strict level
    if level == ValidationLevel.STRICT:
        if "pattern" in data and isinstance(data["pattern"], list):
            # Check for consistent accent patterns
            accent_pattern = [elem.get("accent") for elem in data["pattern"] if isinstance(elem, dict)]
            if accent_pattern:
                unique_accents = set(accent_pattern)
                if not all(accent in AccentType.__members__.values() for accent in unique_accents):
                    errors.append(ValidationError(
                        field="pattern.accents",
                        message="Invalid accent types in pattern"
                    ))

            # Validate total pattern duration matches specified duration
            if "duration" in data:
                pattern_duration = sum(elem.get("duration", 0) for elem in data["pattern"] 
                                    if isinstance(elem, dict))
                if abs(pattern_duration - data["duration"]) > 0.001:  # Allow small float differences
                    errors.append(ValidationError(
                        field="pattern.duration",
                        message="Pattern duration does not match specified duration"
                    ))

    # Add individual rhythm note validation
    if "pattern" in data and isinstance(data["pattern"], list):
        for i, note in enumerate(data["pattern"]):
            if isinstance(note, RhythmNote):
                note_result = RhythmNoteValidator.validate(note, level)
                if not note_result.is_valid:
                    for violation in note_result.violations:
                        errors.append(ValidationError(
                            field=f"pattern[{i}].{violation.path}",
                            message=violation.message
                        ))

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )

def validate_rhythm_pattern(pattern_data: Dict[str, Any]) -> ValidationResult:
    """Validate a rhythm pattern."""
    violations: List[ValidationViolation] = []
    
    # Validate pattern notes exist
    if not pattern_data.get('pattern'):  # Changed from 'notes' to 'pattern'
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
