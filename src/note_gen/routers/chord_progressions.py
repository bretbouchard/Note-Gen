from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List, Optional

from src.note_gen.controllers.chord_progression_controller import ChordProgressionController
from src.note_gen.presenters.chord_progression_presenter import ChordProgressionPresenter
from src.note_gen.dependencies import get_chord_progression_controller
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_progression import ChordProgression

router = APIRouter(tags=["chord-progressions"])

@router.get("/")
async def get_progressions(
    controller: ChordProgressionController = Depends(get_chord_progression_controller)
):
    """Get all available chord progressions."""
    try:
        progressions = await controller.get_all_progressions()
        return {"progressions": ChordProgressionPresenter.present_many(progressions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{progression_id}")
async def get_progression(
    progression_id: str,
    controller: ChordProgressionController = Depends(get_chord_progression_controller)
):
    """Get a chord progression by ID."""
    try:
        progression = await controller.get_progression(progression_id)
        if not progression:
            raise HTTPException(status_code=404, detail="Chord progression not found")
        return ChordProgressionPresenter.present(progression)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_progression(
    progression_data: Dict[str, Any] = Body(...),
    controller: ChordProgressionController = Depends(get_chord_progression_controller)
):
    """Create a new chord progression."""
    try:
        progression = await controller.create_progression(progression_data)
        return ChordProgressionPresenter.present(progression)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate")
async def generate_progression(
    key: str = Body(...),
    scale_type: str = Body(...),
    complexity: float = Body(0.5),
    num_chords: int = Body(4),
    controller: ChordProgressionController = Depends(get_chord_progression_controller)
):
    """Generate a new chord progression."""
    try:
        progression = await controller.generate_progression(
            key=key,
            scale_type=scale_type,
            complexity=complexity,
            num_chords=num_chords
        )
        return ChordProgressionPresenter.present(progression)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))