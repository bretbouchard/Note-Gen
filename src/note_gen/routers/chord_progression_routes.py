# src/note_gen/routers/chord_progression_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from motor import motor_asyncio
from src.note_gen.dependencies import get_db
from src.note_gen.models.chord_progression import ChordProgression
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chord-progressions", response_model=ChordProgression)
async def create_chord_progression(chord_progression: ChordProgression, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> ChordProgression:
    try:
        logger.info(f"Incoming request to create chord progression: {chord_progression}")
        logger.debug(f"Request data: {chord_progression.dict()}")
        logger.info(f"Creating chord progression: {chord_progression}")
        progression_data = chord_progression.dict(exclude_unset=True)
        logger.debug(f"Prepared data for insertion: {progression_data}")
        result = await db.chord_progressions.insert_one(progression_data)
        chord_progression.id = str(result.inserted_id)
        logger.info(f"Chord progression created with ID: {chord_progression.id}")
        return chord_progression
    except Exception as e:
        logger.error(f"Error creating chord progression: {e}")
        logger.error(f"Request data that caused error: {chord_progression.dict()}")
        logger.error(f"Exception details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/chord-progressions/{progression_id}", response_model=ChordProgression)
async def get_chord_progression(progression_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> ChordProgression:
    logger.info(f"Fetching chord progression with ID: {progression_id}")
    try:
        progression = await db.chord_progressions.find_one({"_id": ObjectId(progression_id)})
        logger.debug(f"Query result: {progression}")
        if progression is None:
            logger.warning(f"Chord progression not found for ID: {progression_id}")
            raise HTTPException(status_code=404, detail="Chord progression not found")
        # Ensure all ObjectId fields in the progression are serialized to strings
        serialized_progression = {k: str(v) if isinstance(v, ObjectId) else v for k, v in progression.items()}
        logger.info(f"Fetched chord progression: {serialized_progression}")
        return ChordProgression(**serialized_progression)
    except Exception as e:
        logger.error(f"Error fetching chord progression with ID {progression_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/chord-progressions")
async def get_all_chord_progressions(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    try:
        progressions = await db.chord_progressions.find().to_list(length=None)
        logger.info(f"Fetched {len(progressions)} chord progressions")
        valid_progressions = []
        for progression in progressions:
            logger.debug(f"Processing progression: {progression}")
            for field, value in progression.items():
                if isinstance(value, ObjectId):
                    progression[field] = str(value)
            # Check for required fields
            if "chords" in progression and "key" in progression and "scale_type" in progression:
                valid_progressions.append(ChordProgression(**progression))
            else:
                logger.error(f"Missing required fields in progression: {progression}")
        logger.debug(f"Serialized progressions: {valid_progressions}")
        return valid_progressions
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Additional CRUD operations can be added here
