from pydantic import BaseModel, Field, field_validator, ConfigDict
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ScaleType, ChordQualityType
from src.note_gen.models.scale import Scale
from typing import Optional, Any, Dict, ClassVar
import logging

logger = logging.getLogger(__name__)

class FakeScaleInfo(BaseModel):
    root: Note
    scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    complexity: float = Field(default=0.0)
    _scale: Optional[Scale] = None  # Cache for Scale instance

    # Add scale qualities mappings
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

    @field_validator('scale_type')
    def validate_scale_type(cls, value: ScaleType) -> ScaleType:
        if not isinstance(value, ScaleType):
            raise ValueError('Invalid scale type. Must be a valid ScaleType enum value.')
        return value

    @field_validator('complexity')
    def validate_complexity(cls, value: float) -> float:
        if not (0 <= value <= 1):
            raise ValueError("Complexity must be between 0 and 1")
        return value

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )

    def _get_scale(self) -> Scale:
        """Get or create the Scale instance."""
        if self._scale is None:
            self._scale = Scale(root=self.root, scale_type=self.scale_type)
        return self._scale

    def get_scale_info(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "scale_type": self.scale_type,
            "complexity": self.complexity,
        }

    def get_degree_of_note(self, note: Note) -> int:
        """Returns the degree of the given note in the scale."""
        scale = self._get_scale()
        scale_notes = scale.get_notes()
        
        # Normalize note names for comparison
        target_note_name = note.note_name.upper()
        
        # Try to find an exact match first
        for i, scale_note in enumerate(scale_notes[:-1], 1):  # Skip the octave note
            if scale_note.note_name.upper() == target_note_name:
                return i
                
        # If no exact match, try enharmonic equivalents
        target_midi = note.midi_number
        for i, scale_note in enumerate(scale_notes[:-1], 1):  # Skip the octave note
            if scale_note.midi_number == target_midi:
                return i
                
        raise ValueError(f"Note {note.note_name} is not in the scale")

    def get_quality_for_degree(self, degree: int) -> ChordQualityType:
        """Get the chord quality for a given scale degree."""
        if not (1 <= degree <= 7):
            raise ValueError("Scale degree must be between 1 and 7")
            
        # Define chord qualities for major and minor scales
        if self.scale_type == ScaleType.MAJOR:
            return self.MAJOR_SCALE_QUALITIES[degree]
        else:
            return self.MINOR_SCALE_QUALITIES[degree]

    def get_note_for_degree(self, degree: int) -> Note:
        """Get the note for a given scale degree."""
        scale = self._get_scale()
        return scale.get_scale_degree(degree)
