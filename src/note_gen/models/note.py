from __future__ import annotations
from typing import ClassVar, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.note_gen.models.scale_degree import ScaleDegree

class Note(BaseModel):
    """A musical note representation."""
    
    NOTES: ClassVar[Dict[str, int]] = {
        "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11
    }

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    octave: int
    accidental: Optional[str] = None
    velocity: int = 100
    duration: float = 1.0
    
    @model_validator(mode='after')
    def validate_fields(self) -> 'Note':
        # Validate octave
        if not -2 <= self.octave <= 8:
            raise ValueError("Octave must be between -2 and 8")
            
        # Validate note name
        if self.name not in self.NOTES:
            raise ValueError(f"Invalid note name: {self.name}")
            
        # Validate duration
        if self.duration <= 0:
            raise ValueError("Duration must be greater than 0")
            
        # Validate accidental
        if self.accidental is not None and self.accidental not in ['#', 'b']:
            raise ValueError("Accidental must be '#' or 'b'")
            
        return self

    @property
    def midi_number(self) -> int:
        """Calculate the MIDI number for the note."""
        base_value = self.NOTES[self.name]
        # Handle accidental
        if self.accidental == "#":
            base_value += 1
        elif self.accidental == "b":
            base_value -= 1
        return (self.octave + 1) * 12 + base_value

    def __str__(self) -> str:
        """String representation of the note."""
        accidental_name = ""
        if self.accidental == "#":
            accidental_name = "sharp"
        elif self.accidental == "b":
            accidental_name = "flat"
        
        parts = [self.name]
        if accidental_name:
            parts.append(accidental_name)
        parts.append(f"in octave {self.octave}")
        return " ".join(parts)