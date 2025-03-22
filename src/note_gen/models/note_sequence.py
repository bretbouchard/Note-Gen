"""Note sequence model with updated imports."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from src.note_gen.core.enums import ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.core.accessors import ScaleAccessor

class NoteSequenceCreate(BaseModel):
    """Model for creating a new note sequence."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "progression_name": "I-IV-V",
                "note_pattern_name": "ascending_scale",
                "rhythm_pattern_name": "basic_quarter_notes",
                "scale_info": {
                    "root": {
                        "note_name": "C",
                        "octave": 4,
                        "duration": 1.0,
                        "velocity": 64
                    },
                    "scale_type": "MAJOR"
                }
            }
        }
    )

    progression_name: str = Field(..., description="Name of the chord progression to use")
    note_pattern_name: str = Field(..., description="Name of the note pattern to use")
    rhythm_pattern_name: str = Field(..., description="Name of the rhythm pattern to use")
    scale_info: ScaleInfo = Field(..., description="Scale information for the sequence")

class NoteSequence(BaseModel):
    """Model representing a sequence of notes."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notes": [
                    {
                        "note_name": "C",
                        "octave": 4,
                        "duration": 1.0,
                        "velocity": 64
                    }
                ],
                "scale_info": {
                    "root": {
                        "note_name": "C",
                        "octave": 4,
                        "duration": 1.0,
                        "velocity": 64
                    },
                    "scale_type": "MAJOR"
                },
                "progression_name": "I-IV-V",
                "note_pattern_name": "ascending_scale",
                "rhythm_pattern_name": "basic_quarter_notes"
            }
        }
    )

    notes: List[Note] = Field(default_factory=list, description="List of notes in the sequence")
    scale_info: ScaleInfo = Field(..., description="Scale information for the sequence")
    progression_name: Optional[str] = Field(None, description="Name of the chord progression used")
    note_pattern_name: Optional[str] = Field(None, description="Name of the note pattern used")
    rhythm_pattern_name: Optional[str] = Field(None, description="Name of the rhythm pattern used")
