from pydantic import BaseModel, Field, field_validator, ConfigDict
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ScaleType, ChordQualityType
from src.note_gen.models.scale import Scale
from typing import Optional, Any
import logging

logging.basicConfig(level=logging.DEBUG)

class FakeScaleInfo(BaseModel):
    root: Note
    scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    complexity: float = Field(default=0.0)

    @field_validator('scale_type')
    def validate_scale_type(cls, value):
        if value not in ScaleType:
            raise ValueError('Invalid scale type. Must be either MAJOR or MINOR.')
        return value

    @field_validator('complexity')
    def validate_complexity(cls, value: float) -> float:
        if not (0 <= value <= 1):
            raise ValueError("Complexity must be between 0 and 1")
        return value

    class Config:
        model_config = ConfigDict(arbitrary_types_allowed=True)

    def some_method(self) -> None:
        """Placeholder method for future functionality."""
        pass
    
    def get_scale_info(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "scale_type": self.scale_type,
            "complexity": self.complexity,
        }

    def get_degree_of_note(self, note: Note) -> int:
        """Returns the degree of the given note in the scale."""
        note_to_degree = {
            "C": 1,
            "D": 2,
            "E": 3,
            "F": 4,
            "G": 5,
            "A": 6,
            "B": 7
        }
        if note.note_name not in note_to_degree:
            raise ValueError(f"Note {note.note_name} not in scale.")
        return note_to_degree[note.note_name]

    def get_note_for_degree(self, degree: int) -> Optional[Note]:
        if degree < 1 or degree > 7:
            return None
        scale = Scale(root=self.root, scale_type=self.scale_type)
        notes = scale.get_notes()
        return notes[degree - 1] if notes else None

    def get_scale_note_at_degree(self, degree: int) -> Note:
        scale = Scale(root=self.root, scale_type=self.scale_type)
        return scale.get_note_at_degree(degree)

    def get_chord_quality_for_degree(self, degree: int) -> ChordQualityType:
        if degree < 1 or degree > 7:
            raise ValueError("Degree must be between 1 and 7")
        return ChordQualityType.MAJOR if degree % 2 == 1 else ChordQualityType.MINOR

    def get_scale_degree_note(self, degree: int) -> Note:
        scale = Scale(root=self.root, scale_type=self.scale_type)
        return scale.get_note_at_degree(degree)
