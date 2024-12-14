"""Base types for music theory models."""
from __future__ import annotations

from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field

from .accidental_type import AccidentalType

class Note(BaseModel):
    """A musical note."""
    note_name: str = Field(description="The note name (A-G)")
    accidental: AccidentalType = Field(
        default=AccidentalType.NATURAL,
        description="The accidental applied to this note"
    )
    midi_number: int = Field(description="The MIDI note number")
    duration: float = Field(default=1.0, description="The duration of the note")
    velocity: Optional[int] = Field(default=None, description="The velocity of the note")
    position: Optional[float] = Field(default=None, description="The position of the note")
    octave_offset: int = Field(default=0, description="The octave offset")
    is_chord_note: bool = Field(default=False, description="Whether this note is part of a chord")
    scale_type: Optional[str] = Field(default="major", description="The scale type")
    key: Optional[str] = Field(default="C", description="The key")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: Any) -> None:
        if 'midi_number' not in data:
            from .note_utils import calculate_midi_note
            data['midi_number'] = calculate_midi_note(
                data['note_name'],
                data.get('accidental', AccidentalType.NATURAL),
                data.get('octave', 4)
            )
        super().__init__(**data)
