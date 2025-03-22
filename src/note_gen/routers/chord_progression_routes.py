"""
Consolidated routes for chord progression operations with improved error handling and logging.
"""
from fastapi import APIRouter, Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.patterns import ChordProgression
from ..database.db import get_db_conn
from ..api.errors import APIException, ErrorCodes
from ..database.errors import DocumentNotFoundError, DatabaseError

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/chord-progressions",
    tags=["chord-progressions"]
)

@router.get("/", response_model=List[ChordProgression])
async def get_chord_progressions(db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Get all chord progressions"""
    try:
        cursor = db.chord_progressions.find({})
        chord_progressions = await cursor.to_list(length=None)
        return [ChordProgression(**cp) for cp in chord_progressions]
    except DatabaseError as e:
        logger.error("Failed to fetch chord progressions", exc_info=True)
        raise APIException(
            code=ErrorCodes.DATABASE_ERROR,
            message="Failed to fetch chord progressions",
            status_code=500,
            details={"error": str(e)}
        )

@router.get("/{progression_id}", response_model=ChordProgression)
async def get_chord_progression(
    progression_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
):
    """Get a specific chord progression by ID"""
    try:
        progression = await db.chord_progressions.find_one({"_id": progression_id})
        if not progression:
            raise DocumentNotFoundError(f"Chord progression {progression_id} not found")
        return ChordProgression(**progression)
    except DocumentNotFoundError as e:
        raise APIException(
            code=ErrorCodes.NOT_FOUND,
            message=str(e),
            status_code=404
        )
    except DatabaseError as e:
        logger.error(f"Failed to fetch chord progression {progression_id}", exc_info=True)
        raise APIException(
            code=ErrorCodes.DATABASE_ERROR,
            message="Failed to fetch chord progression",
            status_code=500,
            details={"error": str(e)}
        )
