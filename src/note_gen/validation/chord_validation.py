"""Validation functions for chord data."""
from typing import Dict, Any, Optional
from src.note_gen.core.enums import ValidationLevel, ChordQuality
from src.note_gen.core.constants import CHORD_INTERVALS
from src.note_gen.validation.base_validation import ValidationResult, ValidationError

def validate_chord_data(
    chord_data: Dict[str, Any], 
    level: ValidationLevel = ValidationLevel.NORMAL
) -> ValidationResult:
    """
    Validate chord data structure and content.
    
    Args:
        chord_data: Dictionary containing chord data
        level: Validation level to apply
    
    Returns:
        ValidationResult with validation status and messages
    """
    result = ValidationResult(is_valid=True)
    
    # Required fields check
    required_fields = {'root', 'quality'}
    missing_fields = required_fields - set(chord_data.keys())
    if missing_fields:
        result.add_error(
            field="structure",
            message=f"Missing required fields: {', '.join(missing_fields)}"
        )
        result.is_valid = False
        return result

    # Quality validation
    quality = chord_data.get('quality')
    if not isinstance(quality, ChordQuality):
        try:
            quality = ChordQuality(quality)
        except ValueError:
            result.add_error(
                field="quality",
                message=f"Invalid chord quality: {quality}"
            )
            result.is_valid = False
            return result

    # Notes validation
    notes = chord_data.get('notes', [])
    if notes:
        expected_count = len(CHORD_INTERVALS[quality])
        if len(notes) != expected_count:
            result.add_error(
                field="notes",
                message=f"Invalid number of notes for {quality}. Expected {expected_count}, got {len(notes)}"
            )
            result.is_valid = False

    # Inversion validation
    inversion = chord_data.get('inversion', 0)
    if not isinstance(inversion, int) or not (0 <= inversion <= 3):
        result.add_error(
            field="inversion",
            message="Inversion must be an integer between 0 and 3"
        )
        result.is_valid = False

    # Duration validation
    duration = chord_data.get('duration', 1.0)
    if not isinstance(duration, (int, float)) or duration <= 0:
        result.add_error(
            field="duration",
            message="Duration must be a positive number"
        )
        result.is_valid = False

    # Position validation
    position = chord_data.get('position', 0.0)
    if not isinstance(position, (int, float)) or position < 0:
        result.add_error(
            field="position",
            message="Position must be a non-negative number"
        )
        result.is_valid = False

    return result
