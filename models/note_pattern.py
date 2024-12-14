"""Data structures for musical note patterns."""
from __future__ import annotations

from typing import Any, Literal, Optional, Union, List, Dict, TYPE_CHECKING
from pydantic import BaseModel, Field, validator

if TYPE_CHECKING:
    from models.chord import Chord
    from models.note import Note
    from models.scale_degree import ScaleDegree

# Type aliases
DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]
NoteType = Union['Note', 'ScaleDegree', 'Chord']
PatternDataType = Union[List[int], Dict[str, Any], 'NotePatternData']

class NotePatternData(BaseModel):
    """Data structure for note patterns."""
    model_config = {"arbitrary_types_allowed": True}

    notes: List[NoteType] = Field(default_factory=list)
    intervals: Optional[List[int]] = Field(default=None, description="List of intervals between notes")
    duration: float = Field(default=1.0, description="Duration of the pattern")
    position: float = Field(default=0.0, description="Position of the pattern")
    velocity: Optional[int] = Field(default=None, description="Velocity of the pattern")
    direction: Optional[DirectionType] = Field(default=None, description="Direction of the pattern")
    use_chord_tones: bool = Field(default=False, description="Whether to use chord tones")
    use_scale_mode: bool = Field(default=False, description="Whether to use scale mode")
    arpeggio_mode: bool = Field(default=False, description="Whether to use arpeggio mode")
    restart_on_chord: bool = Field(default=False, description="Whether to restart on chord")
    octave_range: Optional[List[int]] = Field(default=None, description="Range of octaves to use")

    @validator('notes')
    def check_notes(cls, v: List[NoteType]) -> List[NoteType]:
        """Validate notes in the pattern."""
        if not all(isinstance(note, (Note, ScaleDegree, Chord)) for note in v):
            raise ValueError('All items in notes must be instances of Note, ScaleDegree, or Chord')
        return v

    @validator('intervals')
    def check_intervals(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate intervals in the pattern."""
        if v is not None and not all(isinstance(i, int) for i in v):
            raise ValueError('All intervals must be integers')
        return v

    @validator('octave_range')
    def check_octave_range(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate octave range."""
        if v is not None:
            if len(v) != 2:
                raise ValueError('Octave range must be a list of two integers')
            if not all(isinstance(i, int) and -2 <= i <= 8 for i in v):
                raise ValueError('Octave range must be between -2 and 8')
            if v[0] > v[1]:
                raise ValueError('First octave must be lower than second octave')
        return v

class NotePattern(BaseModel):
    """A musical pattern with transformation capabilities."""
    model_config = {"arbitrary_types_allowed": True}

    name: str = Field(description="Name of the pattern")
    description: str = Field(default="", description="Description of the pattern")
    data: Optional[Union[NotePatternData, List[int]]] = Field(description="Pattern data")
    notes: Optional[List[NoteType]] = Field(default=None, description="List of notes in the pattern")
    intervals: Optional[List[int]] = Field(default=None, description="List of intervals between notes")
    duration: Optional[float] = Field(default=None, description="Duration of the pattern")
    position: Optional[float] = Field(default=None, description="Position of the pattern")
    velocity: Optional[int] = Field(default=None, description="Velocity of the pattern")
    direction: Optional[DirectionType] = Field(default=None, description="Direction of the pattern")
    use_chord_tones: Optional[bool] = Field(default=None, description="Whether to use chord tones")
    use_scale_mode: Optional[bool] = Field(default=None, description="Whether to use scale mode")
    arpeggio_mode: Optional[bool] = Field(default=None, description="Whether to use arpeggio mode")
    restart_on_chord: Optional[bool] = Field(default=None, description="Whether to restart on chord")
    octave_range: Optional[List[int]] = Field(default=None, description="Range of octaves to use")
    default_duration: Optional[float] = Field(default=None, description="Default duration for note patterns")

    @classmethod
    def create(cls, name: str, data: NotePatternData) -> NotePattern:
        """Create a note pattern."""
        return cls(name=name, data=data)

    def get_notes(self) -> List[NoteType]:
        """Get all notes in the pattern."""
        if self.notes:
            return self.notes
        if isinstance(self.data, NotePatternData):
            return self.data.notes
        return []

    def get_intervals(self) -> List[int]:
        """Get all intervals in the pattern."""
        if self.intervals:
            return self.intervals
        if isinstance(self.data, NotePatternData) and self.data.intervals:
            return self.data.intervals
        return []

    def get_duration(self) -> float:
        """Get the duration of the pattern."""
        if self.duration is not None:
            return self.duration
        if isinstance(self.data, NotePatternData):
            return self.data.duration
        return 1.0

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = super().dict(*args, **kwargs)
        if isinstance(self.data, NotePatternData):
            d['data'] = self.data.dict()
        return d

def get_pattern_notes(pattern: List[int], notes: List[NoteType]) -> List[NoteType]:
    """Get notes from a pattern."""
    if not check_pattern_notes(pattern, notes):
        raise ValueError("Invalid pattern or notes")
    return [notes[i] for i in pattern if 0 <= i < len(notes)]

def check_pattern_notes(pattern: List[int], notes: List[NoteType]) -> bool:
    """Check if pattern notes are valid."""
    return all(isinstance(i, int) and 0 <= i < len(notes) for i in pattern)

def check_pattern_intervals(pattern: List[int], intervals: List[int]) -> bool:
    """Check if pattern intervals are valid."""
    return all(isinstance(i, int) for i in pattern + intervals)