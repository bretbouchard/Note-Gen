# src/note_gen/models/patterns.py
from typing import List, Optional, Union
from pydantic import BaseModel

from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.scale_degree import ScaleDegree

NoteType = Union[Note, ScaleDegree, Chord]

class NotePatternData(BaseModel):
    """Runtime definition for NotePatternData."""
    notes: List[NoteType] = []
    intervals: Optional[List[int]] = None
    duration: float = 1.0
    position: float = 0.0
    velocity: Optional[int] = None
    direction: Optional[str] = None
    use_chord_tones: bool = False
    use_scale_mode: bool = False
    arpeggio_mode: bool = False
    restart_on_chord: bool = False
    octave_range: Optional[List[int]] = None