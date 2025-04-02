from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import Dict, Any, List, Optional

from note_gen.controllers.pattern_controller import PatternController
from note_gen.presenters.pattern_presenter import PatternPresenter
from note_gen.dependencies import get_pattern_controller
from note_gen.models.patterns import NotePattern, RhythmPattern

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