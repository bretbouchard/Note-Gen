"""Validation functions for note sequences."""
from typing import Dict, Any, List, Union
from note_gen.validation.base_validation import ValidationResult
from note_gen.core.enums import ValidationLevel
from note_gen.models.note import Note

def validate_note_sequence(data: Union[Dict[str, Any], List[Note]], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
    """
    Validate a note sequence.

    Args:
        data: Dictionary containing note sequence data
        level: Validation level to apply

    Returns:
        ValidationResult with validation status and any errors
    """
    result = ValidationResult(is_valid=True)

    # Handle both List[Note] and Dict[str, Any] inputs
    if isinstance(data, list):
        # If data is a list of Notes
        notes = data
        duration = sum(note.duration for note in notes)
        tempo = 120  # Default tempo
    else:
        # If data is a dictionary
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

        notes = data.get('notes', [])

    # Note validation
    total_duration = 0
    for i, note in enumerate(notes):
        if isinstance(note, Note):
            # If note is a Note object
            note_duration = note.duration
        elif isinstance(note, dict):
            # If note is a dictionary
            note_duration = note.get('duration')
        else:
            result.add_error(f"notes[{i}]", "Note must be a Note object or dictionary")
            continue

        # Validate note duration
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
