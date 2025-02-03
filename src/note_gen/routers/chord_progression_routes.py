# src/note_gen/routers/chord_progression_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ValidationError
from typing import List
from bson import ObjectId
from motor import motor_asyncio
from src.note_gen.dependencies import get_db
from src.note_gen.models.chord_progression import ChordProgression
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

router = APIRouter()


@router.post("/chord-progressions", response_model=ChordProgression)
async def create_chord_progression(chord_progression: ChordProgression, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> ChordProgression:
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
    return JSONResponse(status_code=201, content=serialize_chord_progression(chord_progression))

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
        return serialize_chord_progression(ChordProgression(**serialized_progression))
    except Exception as e:
        logger.error(f"Error fetching chord progression with ID {progression_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/chord-progressions")
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

# Additional CRUD operations can be added here
