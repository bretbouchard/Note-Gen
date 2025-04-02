from fastapi import APIRouter, HTTPException
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_progression import ChordProgression  # Updated import path
from typing import List

router = APIRouter()

@router.post("/progression")
async def generate_from_progression(progression: ChordProgression):
    """Generate a sequence from a chord progression."""
    try:
        # Implement sequence generation logic here
        return {"sequence": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chord")
async def generate_from_chord(chord: Chord):
    """Generate a sequence from a single chord."""
    try:
        # Implement single chord sequence generation logic here
        return {"sequence": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
