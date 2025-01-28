from typing import Optional, Dict, ClassVar
from pydantic import BaseModel, Field, field_validator

from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale, ScaleType
from src.note_gen.models.enums import ScaleType, ChordQualityType, ScaleDegree

class ScaleInfo(BaseModel):
    """Information about a musical scale."""
    root: Note
    scale_type: Optional[ScaleType] = Field(default=ScaleType.MAJOR)

    @field_validator('scale_type')
    def validate_scale_type(cls, value: ScaleType) -> ScaleType:
        if value not in [ScaleType.MAJOR, ScaleType.MINOR]:
            raise ValueError("Scale type must be either 'major' or 'minor'")
        return value

    # Define chord qualities for major and minor scales
    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, ChordQualityType]] = {
        1: ChordQualityType.MAJOR,
        2: ChordQualityType.MINOR,
        3: ChordQualityType.MINOR,
        4: ChordQualityType.MAJOR,
        5: ChordQualityType.MAJOR,
        6: ChordQualityType.MINOR,
        7: ChordQualityType.DIMINISHED
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, ChordQualityType]] = {
        1: ChordQualityType.MINOR,
        2: ChordQualityType.DIMINISHED,
        3: ChordQualityType.MAJOR,
        4: ChordQualityType.MINOR,
        5: ChordQualityType.MINOR,
        6: ChordQualityType.MAJOR,
        7: ChordQualityType.MAJOR
    }

    def get_note_for_degree(self, degree: int) -> Optional[Note]:
        """Get the note for a given scale degree."""
        if degree < 1 or degree > 7:
            return None
            
        if not self.scale_type:
            return None

        scale = Scale(root=self.root, scale_type=self.scale_type)
        notes = scale.get_notes()
        return notes[degree - 1] if notes else None

    def get_scale_note_at_degree(self, degree: int) -> Note:
        """Get the note at a given scale degree."""
        scale = Scale(root=self.root, scale_type=self.scale_type)
        return scale.get_note_at_degree(degree)

    def get_chord_quality_for_degree(self, degree: int) -> ChordQualityType:
        if degree < 1 or degree > 7:
            raise ValueError("Degree must be between 1 and 7")
        return self.MAJOR_SCALE_QUALITIES[degree] if self.scale_type == ScaleType.MAJOR else self.MINOR_SCALE_QUALITIES[degree]
