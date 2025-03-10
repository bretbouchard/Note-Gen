"""
src/note_gen/models/request_models.py
Request models for API endpoints.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.patterns import NotePattern

class GenerateSequenceRequest(BaseModel):
    """Request model for generating a note sequence."""
    progression_name: str
    note_pattern_name: NotePattern
    rhythm_pattern_name: str
    scale_info: ScaleInfo
    chords: Optional[List[Dict[str, Any]]] = None
