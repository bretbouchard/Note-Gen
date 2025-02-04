# src/note_gen/routers/chord_progression_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ValidationError
from typing import List
from bson import ObjectId
from motor import motor_asyncio
from src.note_gen.dependencies import get_db
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionResponse
from src.note_gen.models.note import Note
import logging
from fastapi.encoders import jsonable_encoder
from json import JSONEncoder
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ChordQualityType):
            return obj.name
        return super().default(obj)

def serialize_chord_progression(chord_progression):
    serialized = {
        'id': chord_progression.id,
        'name': chord_progression.name,
        'chords': [
            {
                'root': chord.root,
                'quality': chord.quality.to_json() if isinstance(chord.quality, ChordQualityType) else str(chord.quality),
                'notes': [note.to_json() for note in chord.notes],
                'inversion': chord.inversion
            }
            for chord in chord_progression.chords
        ],
        'key': chord_progression.key,
        'scale_type': chord_progression.scale_type,
        'complexity': chord_progression.complexity
    }
    logger.debug(f"Serialized chord progression: {serialized}")
    return serialized

async def create_chord_progression_in_db(chord_progression: ChordProgression, db: motor_asyncio.AsyncIOMotorDatabase):
    logger.info(f"Incoming request to create chord progression: {chord_progression}")
    logger.debug(f"Request data: {chord_progression.dict()}")

    # Validate required fields
    required_fields = ['name', 'chords', 'key', 'scale_type']
    missing_fields = [field for field in required_fields if not getattr(chord_progression, field)]
    if missing_fields:
        logger.error(f"Missing required fields: {', '.join(missing_fields)}")
        raise HTTPException(status_code=400, detail=f'Missing required fields: {", ".join(missing_fields)}')

    # Convert ChordQualityType to string for serialization
    for chord in chord_progression.chords:
        if isinstance(chord.quality, ChordQualityType):
            chord.quality = chord.quality.name  # Convert to string

    # Serialize nested Note objects
    for chord in chord_progression.chords:
        chord.notes = [note.to_json() for note in chord.notes]  # Ensure notes are serialized

    progression_data = chord_progression.dict(exclude_unset=True)
    logger.debug(f"Prepared data for insertion: {progression_data}")

    try:
        result = await db.chord_progressions.insert_one(progression_data)
        if not result.acknowledged:
            logger.error(f"Failed to insert chord progression into the database. Result: {result}")
            raise HTTPException(status_code=500, detail="Failed to insert chord progression")
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error during chord progression insertion: {e}")
        raise HTTPException(status_code=500, detail="Database error during insertion")
    except Exception as e:
        logger.error(f"Unexpected error during chord progression insertion: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    chord_progression.id = str(result.inserted_id)
    logger.info(f"Chord progression created with ID: {chord_progression.id}")
    logger.debug(f"Serialized response: {serialize_chord_progression(chord_progression)}")
    return ChordProgressionResponse(**serialize_chord_progression(chord_progression))

async def get_chord_progression_from_db(chord_progression_id: str, db: motor_asyncio.AsyncIOMotorDatabase):
    logger.info(f"Fetching chord progression with ID: {chord_progression_id}")
    try:
        progression = await db.chord_progressions.find_one({"_id": ObjectId(chord_progression_id)})
        logger.debug(f"Query result: {progression}")
        if progression is None:
            logger.warning(f"Chord progression not found for ID: {chord_progression_id}")
            raise HTTPException(status_code=404, detail="Chord progression not found")
        # Ensure all ObjectId fields in the progression are serialized to strings
        serialized_progression = {k: str(v) if isinstance(v, ObjectId) else v for k, v in progression.items()}
        logger.info(f"Fetched chord progression: {serialized_progression}")
        return ChordProgressionResponse(**serialize_chord_progression(ChordProgression(**serialized_progression)))
    except Exception as e:
        logger.error(f"Error fetching chord progression with ID {chord_progression_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def update_chord_progression_in_db(chord_progression_id: str, chord_progression: ChordProgression, db: motor_asyncio.AsyncIOMotorDatabase):
    logger.info(f"Updating chord progression with ID: {chord_progression_id}")
    try:
        progression = await db.chord_progressions.find_one({"_id": ObjectId(chord_progression_id)})
        logger.debug(f"Query result: {progression}")
        if progression is None:
            logger.warning(f"Chord progression not found for ID: {chord_progression_id}")
            raise HTTPException(status_code=404, detail="Chord progression not found")
        # Update the progression with the new data
        updated_progression_data = chord_progression.dict(exclude_unset=True)
        logger.debug(f"Prepared data for update: {updated_progression_data}")
        result = await db.chord_progressions.update_one({"_id": ObjectId(chord_progression_id)}, {"$set": updated_progression_data})
        if not result.acknowledged:
            logger.error(f"Failed to update chord progression in the database. Result: {result}")
            raise HTTPException(status_code=500, detail="Failed to update chord progression")
        logger.info(f"Chord progression updated with ID: {chord_progression_id}")
        logger.debug(f"Serialized response: {serialize_chord_progression(chord_progression)}")
        return ChordProgressionResponse(**serialize_chord_progression(chord_progression))
    except Exception as e:
        logger.error(f"Error updating chord progression with ID {chord_progression_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def delete_chord_progression_from_db(chord_progression_id: str, db: motor_asyncio.AsyncIOMotorDatabase):
    logger.info(f"Deleting chord progression with ID: {chord_progression_id}")
    try:
        result = await db.chord_progressions.delete_one({"_id": ObjectId(chord_progression_id)})
        if not result.acknowledged:
            logger.error(f"Failed to delete chord progression from the database. Result: {result}")
            raise HTTPException(status_code=500, detail="Failed to delete chord progression")
        logger.info(f"Chord progression deleted with ID: {chord_progression_id}")
    except Exception as e:
        logger.error(f"Error deleting chord progression with ID {chord_progression_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

router = APIRouter()

@router.post("/chord_progressions/", response_model=ChordProgressionResponse)
async def create_chord_progression(chord_progression: ChordProgression, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new chord progression."""
    db_chord_progression = await create_chord_progression_in_db(chord_progression, db)
    return db_chord_progression

@router.get("/chord_progressions/{chord_progression_id}/", response_model=ChordProgressionResponse)
async def read_chord_progression(chord_progression_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    """Retrieve a chord progression by ID."""
    chord_progression = await get_chord_progression_from_db(chord_progression_id, db)
    return chord_progression

@router.put("/chord_progressions/{chord_progression_id}/", response_model=ChordProgressionResponse)
async def update_chord_progression(chord_progression_id: str, chord_progression: ChordProgression, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    """Update a chord progression by ID."""
    updated_chord_progression = await update_chord_progression_in_db(chord_progression_id, chord_progression, db)
    return updated_chord_progression

@router.delete("/chord_progressions/{chord_progression_id}/")
async def delete_chord_progression(chord_progression_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    """Delete a chord progression by ID."""
    await delete_chord_progression_from_db(chord_progression_id, db)

@router.get("/chord_progressions")
async def get_all_chord_progressions(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info('get_all_chord_progressions called')  
    try:
        progressions = await db.chord_progressions.find().to_list(length=None)
        logger.debug(f'Fetched {len(progressions)} chord progressions from the database: {progressions}')  
        response_data = []
        for progression in progressions:
            try:
                validated_progression = ChordProgression(**progression)
                required_fields = ['name', 'chords', 'key', 'scale_type']
                missing_fields = [field for field in required_fields if not getattr(validated_progression, field)]
                if missing_fields:
                    logger.error(f"Missing required fields for progression {progression}: {', '.join(missing_fields)}")
                response_data.append(serialize_chord_progression(validated_progression))
            except ValidationError as e:
                logger.error(f'Validation error for progression {progression}: {e.errors()}')
                raise HTTPException(status_code=400, detail='Invalid chord progression data')
        logger.debug(f'Serialized response data: {response_data}')  
        return response_data
    except Exception as e:
        logger.error(f'Error fetching chord progressions: {e}')  
        raise HTTPException(status_code=500, detail='Internal Server Error')
