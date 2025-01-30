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

logger = logging.getLogger(__name__)

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ChordQualityType):
            return obj.name
        return super().default(obj)

router = APIRouter()


@router.post("/chord-progressions", response_model=ChordProgression)
async def create_chord_progression(chord_progression: ChordProgression, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> ChordProgression:
    try:
        logger.info(f"Incoming request to create chord progression: {chord_progression}")
        logger.debug(f"Request data: {chord_progression.dict()}")
        logger.info(f"Creating chord progression: {chord_progression}")
        
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
        
        progression_data = chord_progression.dict(exclude_unset=True)
        logger.debug(f"Prepared data for insertion: {progression_data}")

        # Use custom JSON encoder to handle serialization
        progression_data = jsonable_encoder(progression_data, custom_encoder=CustomJSONEncoder)

        result = await db.chord_progressions.insert_one(progression_data)
        chord_progression.id = str(result.inserted_id)
        logger.info(f"Chord progression created with ID: {chord_progression.id}")
        
        logger.info(f"Created progression details: {chord_progression.dict()}")
        # Convert ChordQualityType to string for serialization
        for chord in chord_progression.chords:
            if isinstance(chord.quality, ChordQualityType):
                chord.quality = chord.quality.name  # Convert to string
        return jsonable_encoder(chord_progression, custom_encoder=CustomJSONEncoder)
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
    logger.info('get_all_chord_progressions called')  
    try:
        progressions = await db.chord_progressions.find().to_list(length=None)
        logger.debug(f'Fetched {len(progressions)} chord progressions from the database: {progressions}')  
        response_data = []
        for progression in progressions:
            try:
                # Validate against the ChordProgression model
                validated_progression = ChordProgression(**progression)
                required_fields = ['name', 'chords', 'key', 'scale_type']
                missing_fields = [field for field in required_fields if not getattr(validated_progression, field)]
                if missing_fields:
                    logger.error(f"Missing required fields for progression {progression}: {', '.join(missing_fields)}")
                response_data.append(validated_progression.dict())
            except ValidationError as e:
                logger.error(f'Validation error for progression {progression}: {e.errors()}')
                raise HTTPException(status_code=400, detail='Invalid chord progression data')
        logger.debug(f'Serialized response data: {response_data}')  
        return response_data
    except Exception as e:
        logger.error(f'Error fetching chord progressions: {e}')  
        raise HTTPException(status_code=500, detail='Internal Server Error')

# Additional CRUD operations can be added here
