from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import Dict, Any, List, Optional, cast

from note_gen.controllers.pattern_controller import PatternController
from note_gen.presenters.pattern_presenter import PatternPresenter
from note_gen.dependencies import get_pattern_controller
from note_gen.models.patterns import NotePattern
from note_gen.models.rhythm import RhythmPattern
from note_gen.core.enums import ScaleType, ValidationLevel

router = APIRouter(tags=["patterns"])

@router.get("/note-patterns")
async def get_note_patterns(
    controller: PatternController = Depends(get_pattern_controller)
):
    """Get all available note patterns."""
    try:
        patterns = await controller.get_all_note_patterns()
        return {"patterns": PatternPresenter.present_many_note_patterns(patterns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rhythm-patterns")
async def get_rhythm_patterns(
    controller: PatternController = Depends(get_pattern_controller)
):
    """Get all available rhythm patterns."""
    try:
        patterns = await controller.get_all_rhythm_patterns()
        return {"patterns": PatternPresenter.present_many_rhythm_patterns(patterns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/note-patterns/{pattern_id}")
async def get_note_pattern(
    pattern_id: str,
    controller: PatternController = Depends(get_pattern_controller)
):
    """Get a note pattern by ID."""
    try:
        pattern = await controller.get_note_pattern(pattern_id)
        if not pattern:
            raise HTTPException(status_code=404, detail="Note pattern not found")
        return PatternPresenter.present_note_pattern(pattern)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rhythm-patterns/{pattern_id}")
async def get_rhythm_pattern(
    pattern_id: str,
    controller: PatternController = Depends(get_pattern_controller)
):
    """Get a rhythm pattern by ID."""
    try:
        pattern = await controller.get_rhythm_pattern(pattern_id)
        if not pattern:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        return PatternPresenter.present_rhythm_pattern(pattern)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/note-patterns")
async def create_note_pattern(
    pattern_data: Dict[str, Any] = Body(...),
    controller: PatternController = Depends(get_pattern_controller)
):
    """Create a new note pattern."""
    try:
        pattern = await controller.create_note_pattern(pattern_data)
        return PatternPresenter.present_note_pattern(pattern)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/rhythm-patterns")
async def create_rhythm_pattern(
    pattern_data: Dict[str, Any] = Body(...),
    controller: PatternController = Depends(get_pattern_controller)
):
    """Create a new rhythm pattern."""
    try:
        pattern = await controller.create_rhythm_pattern(pattern_data)
        return PatternPresenter.present_rhythm_pattern(pattern)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/rhythm-patterns/validate")
async def validate_rhythm_pattern(
    pattern_data: Dict[str, Any] = Body(...),
    validation_level: str = Query("NORMAL", description="Validation level"),
    controller: PatternController = Depends(get_pattern_controller)
):
    """Validate a rhythm pattern."""
    try:
        # Create a pattern from the data
        pattern = RhythmPattern(**pattern_data)

        # Validate the pattern
        validation_level_enum = ValidationLevel(validation_level)
        validation_result = await controller.validate_pattern(pattern, validation_level_enum)

        # Return the validation result
        return {
            "is_valid": validation_result.is_valid,
            "violations": [v.model_dump() for v in validation_result.violations],
            "warnings": validation_result.warnings
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/note-patterns/validate")
async def validate_note_pattern(
    pattern_data: Dict[str, Any] = Body(...),
    validation_level: str = Query("NORMAL", description="Validation level"),
    controller: PatternController = Depends(get_pattern_controller)
):
    """Validate a note pattern."""
    try:
        # Create a pattern from the data
        pattern = NotePattern(**pattern_data)

        # Validate the pattern
        validation_level_enum = ValidationLevel(validation_level)
        validation_result = await controller.validate_pattern(pattern, validation_level_enum)

        # Return the validation result
        return {
            "is_valid": validation_result.is_valid,
            "violations": [v.model_dump() for v in validation_result.violations],
            "warnings": validation_result.warnings
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate")
async def validate_pattern(
    pattern_data: Dict[str, Any] = Body(...),
    validation_level: str = Query("NORMAL", description="Validation level"),
    controller: PatternController = Depends(get_pattern_controller)
):
    """Validate a pattern."""
    try:
        # Check if this is a pattern generation request
        if "root_note" in pattern_data and "scale_type" in pattern_data and "pattern_config" in pattern_data:
            # This is a pattern generation request, not a direct pattern validation
            # For now, just return valid
            return {"is_valid": True, "violations": [], "warnings": []}

        # Create a pattern from the data
        pattern = NotePattern(**pattern_data)

        # Validate the pattern
        validation_level_enum = ValidationLevel(validation_level)
        validation_result = await controller.validate_pattern(pattern, validation_level_enum)

        # Return the validation result
        return {
            "is_valid": validation_result.is_valid,
            "violations": [v.model_dump() for v in validation_result.violations],
            "warnings": validation_result.warnings
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate")
async def generate_pattern(
    root_note: str = Body(..., description="Root note (e.g., 'C')"),
    scale_type: str = Body(..., description="Scale type (e.g., 'MAJOR')"),
    pattern_config: Dict[str, Any] = Body(..., description="Pattern configuration"),
    controller: PatternController = Depends(get_pattern_controller)
):
    """Generate a musical pattern."""
    try:
        # Convert string scale type to enum
        scale_type_enum = ScaleType(scale_type)

        # Generate the pattern
        pattern = await controller.generate_pattern(
            root_note=root_note,
            scale_type=scale_type_enum,
            pattern_config=pattern_config
        )

        # Return the pattern
        return PatternPresenter.present_note_pattern(pattern)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{pattern_id}")
async def get_pattern_by_id(
    pattern_id: str,
    type: str = Query("note", description="Pattern type (note or rhythm)"),
    controller: PatternController = Depends(get_pattern_controller)
):
    """Get a pattern by ID."""
    try:
        # Determine which repository to use based on type
        if type.lower() == "note":
            pattern = await controller.get_note_pattern(pattern_id)
        else:
            pattern = await controller.get_rhythm_pattern(pattern_id)

        if not pattern:
            raise HTTPException(status_code=404, detail=f"Pattern with ID {pattern_id} not found")

        # Return the pattern
        if type.lower() == "note":
            return PatternPresenter.present_note_pattern(cast(NotePattern, pattern))
        else:
            return PatternPresenter.present_rhythm_pattern(cast(RhythmPattern, pattern))
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/pattern-by-name")
async def get_pattern_by_name(
    name: str = Query(..., description="Pattern name"),
    type: str = Query("note", description="Pattern type (note or rhythm)"),
    controller: PatternController = Depends(get_pattern_controller)
):
    """Get a pattern by name."""
    try:
        pattern = await controller.get_pattern_by_name(name, type)
        if not pattern:
            raise HTTPException(status_code=404, detail=f"{type.capitalize()} pattern not found")
        return PatternPresenter.present_pattern(pattern)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))