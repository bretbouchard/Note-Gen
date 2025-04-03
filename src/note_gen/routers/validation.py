"""
Router for validation endpoints.

This router provides endpoints for validating different types of models and structures.
"""

from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, Any, Optional

from note_gen.controllers.validation_controller import ValidationController
from note_gen.dependencies import get_validation_controller
from note_gen.core.enums import ValidationLevel
from note_gen.validation.base_validation import ValidationResult

router = APIRouter(tags=["validation"])

@router.post("/note-pattern")
async def validate_note_pattern(
    pattern: Dict[str, Any] = Body(...),
    level: Optional[ValidationLevel] = ValidationLevel.NORMAL,
    controller: ValidationController = Depends(get_validation_controller)
):
    """
    Validate a note pattern.
    
    Args:
        pattern: The note pattern to validate
        level: The validation level to apply
        
    Returns:
        ValidationResult: The validation result
    """
    try:
        result = await controller.validate_note_pattern(pattern, level)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post("/rhythm-pattern")
async def validate_rhythm_pattern(
    pattern: Dict[str, Any] = Body(...),
    level: Optional[ValidationLevel] = ValidationLevel.NORMAL,
    controller: ValidationController = Depends(get_validation_controller)
):
    """
    Validate a rhythm pattern.
    
    Args:
        pattern: The rhythm pattern to validate
        level: The validation level to apply
        
    Returns:
        ValidationResult: The validation result
    """
    try:
        result = await controller.validate_rhythm_pattern(pattern, level)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post("/note-sequence")
async def validate_note_sequence(
    sequence: Dict[str, Any] = Body(...),
    level: Optional[ValidationLevel] = ValidationLevel.NORMAL,
    controller: ValidationController = Depends(get_validation_controller)
):
    """
    Validate a note sequence.
    
    Args:
        sequence: The note sequence to validate
        level: The validation level to apply
        
    Returns:
        ValidationResult: The validation result
    """
    try:
        result = await controller.validate_note_sequence(sequence, level)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post("/chord-progression")
async def validate_chord_progression(
    progression: Dict[str, Any] = Body(...),
    level: Optional[ValidationLevel] = ValidationLevel.NORMAL,
    controller: ValidationController = Depends(get_validation_controller)
):
    """
    Validate a chord progression.
    
    Args:
        progression: The chord progression to validate
        level: The validation level to apply
        
    Returns:
        ValidationResult: The validation result
    """
    try:
        result = await controller.validate_chord_progression(progression, level)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post("/config")
async def validate_config(
    config: Dict[str, Any] = Body(...),
    config_type: str = Body(...),
    controller: ValidationController = Depends(get_validation_controller)
):
    """
    Validate a configuration dictionary.
    
    Args:
        config: The configuration to validate
        config_type: The type of configuration
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        result = await controller.validate_config(config, config_type)
        return {"is_valid": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
