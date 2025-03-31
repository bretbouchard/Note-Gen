"""Validation functions for note sequences."""
from typing import Dict, Any
from src.note_gen.validation.base_validation import ValidationResult
from src.note_gen.core.enums import ValidationLevel

def validate_note_sequence(data: Dict[str, Any], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
    """
    Validate a note sequence.
    
    Args:
        data: Dictionary containing note sequence data
        level: Validation level to apply
        
    Returns:
        ValidationResult with validation status and any errors
    """
    result = ValidationResult(is_valid=True)
    
    # Basic structure validation
    if not isinstance(data.get('notes'), list):
        result.add_error("notes", "Notes must be a list")

    # Duration validation
    duration = data.get('duration')
    if not isinstance(duration, (int, float)) or duration <= 0:
        result.add_error("duration", "Duration must be a positive number")

    # Tempo validation
    tempo = data.get('tempo', 120)  # Default tempo if not specified
    if not isinstance(tempo, int) or tempo < 20 or tempo > 300:
        result.add_error("tempo", "Tempo must be an integer between 20 and 300")

    # Note validation
    total_duration = 0
    for i, note in enumerate(data.get('notes', [])):
        if not isinstance(note, dict):
            result.add_error(f"notes[{i}]", "Note must be a dictionary")
            continue
            
        # Validate note duration
        note_duration = note.get('duration')
        if not isinstance(note_duration, (int, float)) or note_duration <= 0:
            result.add_error(f"notes[{i}].duration", "Note has invalid duration")
        else:
            total_duration += note_duration

    # Validate total duration matches sum of note durations
    if duration and abs(total_duration - duration) > 0.001:  # Allow small floating-point differences
        result.add_error("duration", 
            f"Total duration ({duration}) does not match sum of note durations ({total_duration})")

    # Additional strict validation rules
    if level == ValidationLevel.STRICT:
        # Add stricter validation rules here
        pass

    return result
