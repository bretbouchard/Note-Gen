"""
src/note_gen/models/request_models.py
Request models for API endpoints.
"""

from pydantic import BaseModel
from src.note_gen.models.scale_info import ScaleInfo

class GenerateSequenceRequest(BaseModel):
    """Request model for generating a note sequence."""
    progression_name: str
    note_pattern_name: str
    rhythm_pattern_name: str
    scale_info: ScaleInfo
