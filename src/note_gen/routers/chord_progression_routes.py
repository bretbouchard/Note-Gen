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
        logger.info(f"Creating chord progression: {chord_progression}")
        progression_data = chord_progression.dict(exclude_unset=True)
        logger.debug(f"Prepared data for insertion: {progression_data}")
        logger.debug(f"Inserting data into collection: chord_progressions")
        logger.debug(f"Database connection: {db}")
        result = await db.chord_progressions.insert_one(progression_data)
        logger.debug(f"Insert result: {result.inserted_id}")
        logger.info(f"Inserted {result.inserted_count} document(s) with ID(s): {result.inserted_id}")
        chord_progression.id = str(result.inserted_id)  # Convert ObjectId to string
        # Ensure all ObjectId fields in the chord_progression are serialized to strings
        for field, value in chord_progression.dict().items():
            if isinstance(value, ObjectId):
                setattr(chord_progression, field, str(value))
        logger.info(f"Chord progression created with ID: {chord_progression.id}")
        logger.debug(f"Created chord progression data: {chord_progression.dict()}")
        return chord_progression
    except motor_asyncio.errors.WriteError as e:
        logger.error(f"Error creating chord progression: {e}", exc_info=True)
        if 'progression_data' in locals():
            logger.debug(f"Progression data attempted to insert: {progression_data}")
        raise HTTPException(status_code=400, detail=f"Bad Request: {e}")
    except Exception as e:
        logger.error(f"Error creating chord progression: {e}", exc_info=True)
        if 'progression_data' in locals():
            logger.debug(f"Progression data attempted to insert: {progression_data}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@router.get("/chord-progressions/{progression_id}", response_model=ChordProgression)
async def get_chord_progression(progression_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> ChordProgression:
    try:
        logger.info(f"Fetching chord progression with ID: {progression_id}")
        progression = await db.chord_progressions.find_one({"_id": ObjectId(progression_id)})
        logger.debug(f"Query result: {progression}")
        if progression is None:
            logger.warning(f"Chord progression not found for ID: {progression_id}")
            raise HTTPException(status_code=404, detail="Chord progression not found")
        # Ensure all ObjectId fields in the progression are serialized to strings
        serialized_progression = {k: str(v) if isinstance(v, ObjectId) else v for k, v in progression.items()}
        logger.info(f"Fetched chord progression: {serialized_progression}")
        return ChordProgression(**serialized_progression)
    except motor_asyncio.errors.OperationFailure as e:
        logger.error(f"Error fetching chord progression: {e}", exc_info=True)
        logger.debug(f"Progression ID attempted to fetch: {progression_id}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching chord progression: {e}", exc_info=True)
        logger.debug(f"Progression ID attempted to fetch: {progression_id}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Additional CRUD operations can be added here
