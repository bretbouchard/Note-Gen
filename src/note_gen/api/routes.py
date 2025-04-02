from fastapi import APIRouter, Depends, HTTPException
from ..database.db import get_db_conn
from .pattern_api import (
    get_patterns,
    fetch_note_patterns,
    fetch_rhythm_patterns,
    fetch_note_pattern_by_id,
    fetch_rhythm_pattern_by_id
)

router = APIRouter(prefix="/api/v1")

@router.get("/patterns/")
async def get_all_patterns(db=Depends(get_db_conn)):
    return await get_patterns(db)

@router.get("/patterns/note")
async def get_note_patterns(db=Depends(get_db_conn)):
    return await fetch_note_patterns(db)

@router.get("/patterns/rhythm")
async def get_rhythm_patterns(db=Depends(get_db_conn)):
    return await fetch_rhythm_patterns(db)

@router.get("/patterns/{pattern_id}")
async def get_pattern(pattern_id: str, pattern_type: str = None, db=Depends(get_db_conn)):
    if pattern_type == "note":
        pattern = await fetch_note_pattern_by_id(db, pattern_id)
    elif pattern_type == "rhythm":
        pattern = await fetch_rhythm_pattern_by_id(db, pattern_id)
    else:
        # Try both types if pattern_type is not specified
        pattern = await fetch_note_pattern_by_id(db, pattern_id)
        if not pattern:
            pattern = await fetch_rhythm_pattern_by_id(db, pattern_id)
    
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return pattern
