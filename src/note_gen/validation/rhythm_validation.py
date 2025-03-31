"""Validation functions for rhythm-related data."""
from typing import Dict, Any, List
from src.note_gen.core.constants import DURATIONS, DURATION_LIMITS
from src.note_gen.core.enums import ValidationLevel, AccentType
from src.note_gen.validation.base_validation import ValidationResult, ValidationError
from src.note_gen.validation.rhythm_note_validation import RhythmNoteValidator
from src.note_gen.models.rhythm import RhythmNote

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
                    # Remove any unsupported fields before validation
                    allowed_fields = {
                        'note', 'position', 'duration', 'velocity', 'accent',
                        'tuplet_ratio', 'swing_ratio', 'humanize_amount', 'groove_offset'
                    }
                    filtered_element = {k: v for k, v in element.items() if k in allowed_fields}
                    
                    try:
                        RhythmNote(**filtered_element)
                    except Exception as e:
                        errors.append(ValidationError(
                            field=f"pattern[{i}]",
                            message=f"Invalid note data: {str(e)}"
                        ))

    # Time signature validation
    if "time_signature" in data:
        time_sig = data["time_signature"]
        if isinstance(time_sig, str):
            try:
                numerator, denominator = map(int, time_sig.split('/'))
            except ValueError:
                errors.append(ValidationError(
                    field="time_signature",
                    message="Invalid time signature format"
                ))
        elif isinstance(time_sig, tuple) and len(time_sig) == 2:
            numerator, denominator = time_sig
        else:
            errors.append(ValidationError(
                field="time_signature",
                message="Time signature must be a string 'n/m' or tuple (n, m)"
            ))
            numerator = denominator = None

        if numerator is not None and denominator is not None:
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

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )

def validate_rhythm_pattern(pattern_data: Dict[str, Any]) -> ValidationResult:
    """Validate a rhythm pattern."""
    return validate_rhythm_data(pattern_data, ValidationLevel.NORMAL)
