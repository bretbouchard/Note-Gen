"""Validation functions for scale degree data."""
from typing import Dict, Any
from src.note_gen.validation.base_validation import ValidationResult
from src.note_gen.core.enums import ValidationLevel, ChordQuality
from src.note_gen.core.constants import SCALE_DEGREE_QUALITIES, DEFAULT_SCALE_DEGREE_QUALITIES

def validate_scale_degree(data: Dict[str, Any], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
    """
    Validate scale degree data.
    
    Args:
        data: Dictionary containing scale degree data
        level: Validation level to apply
        
    Returns:
        ValidationResult: Result of validation
    """
    result = ValidationResult(is_valid=True)
    
    # Basic validation (LENIENT level and above)
    if 'value' not in data:
        result.add_error(
            field="value",
            message="Scale degree value is required"
        )
        return result
        
    value = data['value']
    if not isinstance(value, int):
        result.add_error(
            field="value",
            message="Scale degree value must be an integer"
        )
        return result
        
    if not (1 <= value <= 7):
        result.add_error(
            field="value",
            message="Scale degree value must be between 1 and 7"
        )
        return result

    # Quality validation (NORMAL level and above)
    if level.value >= ValidationLevel.NORMAL.value:
        quality = data.get('quality')
        if quality is not None:
            if not isinstance(quality, ChordQuality):
                result.add_error(
                    field="quality",
                    message="Quality must be a valid ChordQuality enum value"
                )
            elif value in SCALE_DEGREE_QUALITIES:
                default_quality = DEFAULT_SCALE_DEGREE_QUALITIES[value]
                if quality != default_quality:
                    result.add_warning(
                        warning=f"Non-standard quality {quality} for scale degree {value}. "
                               f"Standard quality is {default_quality}"
                    )

    return result

def validate_scale_degree_sequence(
    degrees: list[int],
    level: ValidationLevel = ValidationLevel.NORMAL
) -> ValidationResult:
    """Validate a sequence of scale degrees."""
    result = ValidationResult(is_valid=True)
    
    if not degrees:
        result.add_error(
            field="degrees",
            message="Scale degree sequence cannot be empty"
        )
        return result
        
    for i, degree in enumerate(degrees):
        if not isinstance(degree, int):
            result.add_error(
                field=f"degrees[{i}]",
                message=f"Invalid scale degree type: {type(degree)}"
            )
            result.is_valid = False
        elif not (1 <= degree <= 7):
            result.add_error(
                field=f"degrees[{i}]",
                message=f"Invalid scale degree value: {degree}"
            )
            result.is_valid = False
            
    if level == ValidationLevel.STRICT:
        # Check for common voice leading issues
        for i in range(len(degrees) - 1):
            if abs(degrees[i] - degrees[i + 1]) > 2:
                result.add_warning(
                    warning=f"Large interval between degrees {degrees[i]} and {degrees[i + 1]}"
                )
    
    return result
