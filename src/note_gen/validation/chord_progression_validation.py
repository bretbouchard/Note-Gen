"""Validation functions for chord progression data."""
from typing import Dict, Any
from src.note_gen.core.enums import ValidationLevel, ChordQuality
from src.note_gen.core.constants import VALID_KEYS
from src.note_gen.validation.base_validation import ValidationResult

def validate_chord_progression_data(data: Dict[str, Any], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
    """
    Validate chord progression data structure and values.
    
    Args:
        data: Dictionary containing chord progression data
        level: Validation level to apply
    
    Returns:
        ValidationResult with validation status and any errors
    """
    result = ValidationResult(is_valid=True)
    
    # Basic structure validation
    if not isinstance(data, dict):
        result.add_error("data", "Data must be a dictionary")
        return result

    required_fields = {"name", "key", "chords"}
    missing_fields = required_fields - set(data.keys())
    if missing_fields:
        result.add_error("fields", f"Missing required fields: {', '.join(missing_fields)}")

    # Key validation
    if "key" in data:
        key = data["key"]
        if not isinstance(key, str):
            result.add_error("key", "Key must be a string")
        elif key not in VALID_KEYS:
            result.add_error("key", f"Invalid key: {key}")

    # Chords validation
    if "chords" in data:
        chords = data["chords"]
        if not isinstance(chords, list):
            result.add_error("chords", "Chords must be a list")
        else:
            for i, chord in enumerate(chords):
                if not isinstance(chord, dict):
                    result.add_error(f"chords[{i}]", "Chord must be a dictionary")
                else:
                    # Validate chord structure
                    if "root" not in chord:
                        result.add_error(f"chords[{i}].root", "Missing root")
                    if "quality" not in chord:
                        result.add_error(f"chords[{i}].quality", "Missing quality")
                    elif not isinstance(chord["quality"], (str, ChordQuality)):
                        result.add_error(f"chords[{i}].quality", "Invalid chord quality")

    # Additional validation for stricter levels
    if level == ValidationLevel.STRICT:
        if "chords" in data and isinstance(data["chords"], list):
            # Validate chord progression length
            if len(data["chords"]) < 2:
                result.add_error("progression_length", "Progression must contain at least 2 chords")
            elif len(data["chords"]) > 16:
                result.add_error("progression_length", "Progression exceeds maximum length of 16 chords")

            # Validate chord variety
            unique_chords = set((c.get("root"), c.get("quality")) for c in data["chords"])
            if len(unique_chords) < 2:
                result.add_error("chord_variety", "Progression should use more than one unique chord")

            # Validate voice leading
            for i in range(len(data["chords"]) - 1):
                current_chord = data["chords"][i]
                next_chord = data["chords"][i + 1]
                
                # Check for parallel fifths/octaves
                if (current_chord.get("root") == next_chord.get("root") and 
                    current_chord.get("quality") == next_chord.get("quality")):
                    result.add_error(f"voice_leading_{i}", 
                                   f"Potential voice leading issue between chords {i} and {i+1}")

            # Validate cadence
            if len(data["chords"]) >= 2:
                final_chords = data["chords"][-2:]
                # Check for authentic cadence
                if not (final_chords[-1].get("root") == data.get("key") and 
                       final_chords[-2].get("root") in ["G", "D"]):
                    result.add_error("cadence", "Non-standard cadence detected")

    return result
