from pydantic import BaseModel
from src.note_gen.models.note_sequence import ScaleInfo

class SequenceRequest(BaseModel):
    progression_name: str
    note_pattern_name: str
    rhythm_pattern_name: str
    scale_info: ScaleInfo