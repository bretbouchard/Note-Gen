"""Module for defining note events in a musical sequence."""
import logging
from pydantic import BaseModel, Field

from models.note import Note
from models.chord import Chord
from models.scale_degree import ScaleDegree

# Set up logging
logger = logging.getLogger(__name__)

class NoteEvent(BaseModel):
    """Represents a musical note event with timing and performance information."""
    note: Note | ScaleDegree | Chord
    position: float = Field(default=0.0)
    duration: float = Field(default=1.0)
    velocity: int = Field(default=100)
    channel: int = Field(default=0)
    is_rest: bool = Field(default=False)
    
    @property
    def end_position(self) -> float:
        """Get the end position of the note event."""
        return self.position + self.duration
    
    def overlaps(self, other: 'NoteEvent') -> bool:
        """Check if this note event overlaps with another."""
        return (self.position < other.end_position and 
                other.position < self.end_position)
    
    def transpose(self, semitones: int) -> None:
        """Transpose the note by the given number of semitones."""
        if isinstance(self.note, Note):
            self.note = self.note.transpose(semitones)
        elif isinstance(self.note, Chord):
            self.note = self.note.transpose(semitones)