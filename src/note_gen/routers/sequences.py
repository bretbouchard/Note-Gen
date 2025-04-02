from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import Dict, Any, List, Optional

from src.note_gen.controllers.sequence_controller import SequenceController
from src.note_gen.presenters.sequence_presenter import SequencePresenter
from src.note_gen.dependencies import get_sequence_controller
from src.note_gen.models.note import Note
from src.note_gen.models.sequence import Sequence
from src.note_gen.models.note_sequence import NoteSequence

router = APIRouter(tags=["sequences"])

@router.get("/")
async def get_sequences(
    controller: SequenceController = Depends(get_sequence_controller)
):
    """Get all available sequences."""
    try:
        sequences = await controller.get_all_sequences()
        return {"sequences": SequencePresenter.present_many_sequences(sequences)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sequence_id}")
async def get_sequence(
    sequence_id: str,
    controller: SequenceController = Depends(get_sequence_controller)
):
    """Get a sequence by ID."""
    try:
        sequence = await controller.get_sequence(sequence_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Sequence not found")

        if isinstance(sequence, NoteSequence):
            return SequencePresenter.present_note_sequence(sequence)
        else:
            return SequencePresenter.present_sequence(sequence)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_sequence(
    sequence_data: Dict[str, Any] = Body(...),
    controller: SequenceController = Depends(get_sequence_controller)
):
    """Create a new sequence."""
    try:
        sequence = await controller.create_sequence(sequence_data)
        return SequencePresenter.present_sequence(sequence)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate")
async def generate_sequence(
    progression_name: str = Body(...),
    pattern_name: str = Body(...),
    rhythm_pattern_name: str = Body(...),
    controller: SequenceController = Depends(get_sequence_controller)
):
    """Generate a sequence from a chord progression and patterns."""
    try:
        sequence = await controller.generate_sequence(
            progression_name=progression_name,
            pattern_name=pattern_name,
            rhythm_pattern_name=rhythm_pattern_name
        )
        return SequencePresenter.present_note_sequence(sequence)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/by-name/{sequence_name}")
async def get_sequence_by_name(
    sequence_name: str,
    controller: SequenceController = Depends(get_sequence_controller)
):
    """Get a sequence by name."""
    try:
        sequence = await controller.get_sequence_by_name(sequence_name)
        if not sequence:
            raise HTTPException(status_code=404, detail="Sequence not found")

        if isinstance(sequence, NoteSequence):
            return SequencePresenter.present_note_sequence(sequence)
        else:
            return SequencePresenter.present_sequence(sequence)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))