"""Router for pattern-related endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.core.database import get_db_conn
from src.note_gen.models.patterns import NotePattern, RhythmPattern

router = APIRouter(prefix="/api/v1/patterns", tags=["patterns"])

@router.get("/patterns")
async def get_patterns(db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    try:
        patterns = {
            "note_patterns": await db.note_patterns.find().to_list(None),
            "rhythm_patterns": await db.rhythm_patterns.find().to_list(None)
        }
        return patterns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
