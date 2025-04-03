"""Validation functions for Roman numerals."""

from typing import Dict, Any
from note_gen.validation.base_validation import ValidationResult
from note_gen.core.enums import ValidationLevel
from note_gen.core.constants import ROMAN_TO_INT, ROMAN_NUMERAL_PATTERN
import re

def validate_roman_numeral_data(data: Dict[str, Any], level: ValidationLevel) -> ValidationResult:
    """Validate roman numeral data."""
    result = ValidationResult(is_valid=True)
    
    # Basic structure validation
    if 'numeral' not in data:
        result.add_error(
            field="numeral",
            message="Missing required field 'numeral'"
        )
        return result
        
    numeral = data['numeral']
    
    # Validate numeral format
    if not re.match(ROMAN_NUMERAL_PATTERN, numeral):
        result.add_error(
            field="numeral",
            message=f"Invalid roman numeral format: {numeral}"
        )
        
    # Validate numeral value
    if numeral.upper() not in ROMAN_TO_INT:
        result.add_error(
            field="numeral",
            message=f"Invalid roman numeral value: {numeral}"
        )
        
    # Validate accidental if present
    if 'accidental' in data and data['accidental']:
        if data['accidental'] not in ['#', 'b']:
            result.add_error(
                field="accidental",
                message=f"Invalid accidental: {data['accidental']}"
            )
            
    # Validate inversion if present
    if 'inversion' in data and data['inversion'] is not None:
        if not (0 <= data['inversion'] <= 3):
            result.add_error(
                field="inversion",
                message=f"Invalid inversion: {data['inversion']}"
            )
            
    # Additional validation for STRICT level
    if level == ValidationLevel.STRICT:
        # Validate secondary dominants
        if 'secondary' in data and data['secondary']:
            secondary_result = validate_roman_numeral_data(data['secondary'], level)
            if not secondary_result.is_valid:
                for error in secondary_result.errors:
                    result.add_error(
                        field="secondary",
                        message=f"Secondary: {error}"
                    )
    
    return result
