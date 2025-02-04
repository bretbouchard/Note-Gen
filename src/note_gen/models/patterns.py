from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_degree import ScaleDegree

NoteType = Union[Note, ScaleDegree, Chord]

class NotePatternData(BaseModel):
    """Data structure for note pattern parameters."""
    notes: List[Dict[str, Any]] = Field(..., description="List of notes in the pattern")
    intervals: Optional[List[int]] = Field(None, description="List of intervals")
    duration: float = Field(default=1.0, description="Pattern duration")
    position: float = Field(default=0.0, description="Pattern position")
    velocity: int = Field(default=100, description="Pattern velocity")
    direction: str = Field(default="up", description="Pattern direction")
    use_chord_tones: bool = Field(default=False, description="Use chord tones")
    use_scale_mode: bool = Field(default=False, description="Use scale mode")
    arpeggio_mode: bool = Field(default=False, description="Arpeggio mode")
    restart_on_chord: bool = Field(default=False, description="Restart on chord")
    octave_range: List[int] = Field(default=[4, 5], description="Octave range")
    default_duration: float = Field(default=1.0, description="Default note duration")

    class Config:
        json_schema_extra = {
            'example': {
                'name': 'Simple Triad',
                'data': {
                    'notes': [
                        {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                        {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                        {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100}
                    ]
                }
            }
        }
        arbitrary_types_allowed = True

class NotePattern(BaseModel):
    """A pattern of musical notes."""
    id: Optional[str] = Field(None, description="ID of the note pattern")
    name: str = Field(..., description="Name of the note pattern")
    description: str = Field(..., description="Pattern description")
    tags: List[str] = Field(..., description="Pattern tags")
    complexity: Optional[float] = Field(None, description="Pattern complexity")
    notes: Optional[List[Note]] = Field(default=None, description="List of notes in the pattern")
    data: Optional[Union[NotePatternData, List[Union[int, List[int]]]]] = Field(default=None, description="Additional pattern data")
    style: Optional[str] = Field(default=None, description="Pattern style")
    is_test: Optional[bool] = Field(default=None, description="Test flag")

    @property
    def total_duration(self) -> float:
        """Calculate the total duration of the pattern."""
        if not self.notes:
            return 0.0
        return sum(note.duration for note in self.notes)

    def get_notes(self) -> List[Note]:
        """Get the list of notes in the pattern."""
        return self.notes or []

    def add_note(self, note: Note) -> None:
        """Add a note to the pattern."""
        if self.notes is None:
            self.notes = []
        self.notes.append(note)

    def remove_note(self, index: int) -> None:
        """Remove a note from the pattern."""
        if self.notes and 0 <= index < len(self.notes):
            self.notes.pop(index)

    def clear_notes(self) -> None:
        """Clear all notes from the pattern."""
        self.notes = []

    class Config:
        json_schema_extra = {
            'example': {
                'name': 'Simple Triad',
                'description': 'A simple triad pattern',
                'tags': ['triad', 'basic'],
                'notes': [
                    {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                    {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                    {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100}
                ]
            }
        }
        arbitrary_types_allowed = True

    @model_validator(mode='before')
    def validate_data(cls, values):
        # Check data field
        data = values.get('data')
        if data is None:
            raise ValueError("Data must be provided and cannot be None.")
        if isinstance(data, list):
            if not data or not all(isinstance(item, (int, list)) for item in data):
                raise ValueError("Data must be a non-empty list of integers or nested lists.")
        elif not isinstance(data, NotePatternData):
            raise ValueError("Data must be an instance of NotePatternData or a list.")

        return values