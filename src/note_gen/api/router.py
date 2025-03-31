"""API router configuration."""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.core.database import get_database
from src.note_gen.api import pattern_api
from typing import Annotated

router = APIRouter()

DbDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]

@router.get("/chord-progressions")
async def get_chord_progressions(db: DbDep):
    """Get all chord progressions."""
    return await pattern_api.fetch_chord_progressions(db)

@router.get("/chord-progressions/{progression_id}")
async def get_chord_progression(
    progression_id: str,
    db: DbDep
):
    """Get a specific chord progression."""
    return await pattern_api.fetch_chord_progression_by_id(db, progression_id)

@router.get("/rhythm-patterns")
async def get_rhythm_patterns(db: DbDep):
    """Get all rhythm patterns."""
    return await pattern_api.fetch_rhythm_patterns(db)

@router.get("/rhythm-patterns/{pattern_id}")
async def get_rhythm_pattern(
    pattern_id: str,
    db: DbDep
):
    """Get a specific rhythm pattern."""
    return await pattern_api.fetch_rhythm_pattern_by_id(db, pattern_id)

@router.get("/note-patterns")
async def get_note_patterns(db: DbDep):
    """Get all note patterns."""
    return await pattern_api.fetch_note_patterns(db)

@router.get("/note-patterns/{pattern_id}")
async def get_note_pattern(
    pattern_id: str,
    db: DbDep
):
    """Get a specific note pattern."""
    return await pattern_api.fetch_note_pattern_by_id(db, pattern_id)
