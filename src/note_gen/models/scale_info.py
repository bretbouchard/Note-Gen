"""Scale information model."""
from typing import List, Optional, Tuple
import re
from pydantic import BaseModel, Field, field_validator
from ..core.constants import (
    FULL_NOTE_REGEX,
    SCALE_INTERVALS,
    NOTE_TO_SEMITONE,
    SEMITONE_TO_NOTE
)
from ..core.enums import ScaleType
from .note import Note

class ScaleInfo(BaseModel):
    """Model for scale information."""
    key: str = Field(..., description="The key of the scale (e.g., 'C', 'F#', 'Bb')")
    scale_type: ScaleType

    @field_validator('key')
    def validate_key(cls, v: str) -> str:
        """Validate the key format."""
        # Remove any whitespace
        v = v.strip()
        
        # Check if the key matches the pattern: [A-G](#|b)?
        import re
        if not re.match(r'^[A-G][#b]?$', v):
            raise ValueError(f"Invalid key format: {v}")
        return v

    def get_scale_notes(self, octave: int = 4) -> List[Note]:
        """Get all notes in the scale for a given octave."""
        root_semitone = NOTE_TO_SEMITONE[self.key]
        intervals = SCALE_INTERVALS[self.scale_type]  # Use the enum directly
        
        scale_notes = []
        for interval in intervals:
            semitone = (root_semitone + interval) % 12
            note_name = SEMITONE_TO_NOTE[semitone]
            scale_notes.append(Note(pitch=note_name, octave=octave))
        
        return scale_notes

    def is_note_in_scale(self, note: Note) -> bool:
        """Check if a note is in the scale."""
        scale_notes = self.get_scale_notes(note.octave)
        return any(n.pitch == note.pitch for n in scale_notes)

    def get_scale_degree(self, pitch: str) -> int:
        """Get the scale degree (1-based) for a given pitch.
        
        Args:
            pitch: The pitch name (e.g., 'C', 'F#')
            
        Returns:
            The scale degree (1-7) if the pitch is in the scale, raises ValueError otherwise
        """
        scale_notes = self.get_scale_notes()
        for i, note in enumerate(scale_notes, 1):
            if note.pitch == pitch:
                return i
        raise ValueError(f"Pitch {pitch} is not in the scale {self.key} {self.scale_type.value}")

    def __str__(self) -> str:
        """String representation of the scale."""
        return f"{self.key} {self.scale_type.value}"
