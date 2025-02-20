from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator

# Define request model inline if you prefer not to create a separate file
class SequenceRequest(BaseModel):
    progression_name: str
    note_pattern_name: str
    rhythm_pattern_name: str
    scale_info: ScaleInfo

router = APIRouter()

@router.post("")
async def generate_sequence(request: SequenceRequest):
    try:
        generator = NoteSequenceGenerator()
        sequence = await generator.generate_sequence_from_presets(
            progression_name=request.progression_name,
            note_pattern_name=request.note_pattern_name,
            rhythm_pattern_name=request.rhythm_pattern_name,
            scale_info=request.scale_info
        )
        return sequence
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))