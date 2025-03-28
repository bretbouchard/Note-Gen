from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator
import logging

# Define request model inline if you prefer not to create a separate file
class SequenceRequest(BaseModel):
    progression_name: str
    note_pattern_name: str
    rhythm_pattern_name: str
    scale_info: ScaleInfo

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("")
async def generate_sequence(request: SequenceRequest):
    try:
        logger.debug(f"Received request data for generating sequence: {request}")
        logger.debug(f"Type of progression_name: {type(request.progression_name)}")
        logger.debug(f"Type of note_pattern_name: {type(request.note_pattern_name)}")
        logger.debug(f"Type of rhythm_pattern_name: {type(request.rhythm_pattern_name)}")
        logger.debug(f"Type of scale_info: {type(request.scale_info)}")
        logger.debug(f"Scale info details: {request.scale_info}")
        logger.debug(f"Scale info type details: {type(request.scale_info.tonic)}")
        logger.debug(f"Scale info tonic details: {request.scale_info.tonic}")
        logger.debug(f"Scale info scale_type details: {request.scale_info.scale_type}")
        logger.debug(f"Scale info num_octaves details: {request.scale_info.num_octaves}")
        sequence_data = {
            "progression_name": request.progression_name,
            "note_pattern_name": request.note_pattern_name,
            "rhythm_pattern_name": request.rhythm_pattern_name,
            "scale_info": request.scale_info
        }
        logger.info(f"Generating sequence with data: {sequence_data}")
        # Generate the sequence
        generator = NoteSequenceGenerator()
        sequence = await generator.generate_sequence_from_presets(
            progression_name=request.progression_name,
            note_pattern_name=request.note_pattern_name,
            rhythm_pattern_name=request.rhythm_pattern_name,
            scale_info=request.scale_info
        )
        logger.info(f"Generated sequence: {sequence.model_dump_json()}")
        return sequence.model_dump_json()
    except ValueError as e:
        logger.error(f"Error generating sequence with request data: {request}", exc_info=True)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating sequence with request data: {request}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))