from pydantic import BaseModel, Field, field_validator, ConfigDict, validator
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.scale import Scale
from typing import Optional, Any, Dict, ClassVar
import logging

logger = logging.getLogger(__name__)

class FakeScaleInfo(BaseModel):
    root: Note
    scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    complexity: float = Field(default=0.0)
    _scale: Optional[Scale] = None  # Cache for Scale instance

    # Define a root note as a ClassVar
    root_note: ClassVar[Note] = Note(name="C")  # Define a root note

    # Update the MAJOR_SCALE_QUALITIES and MINOR_SCALE_QUALITIES mappings
    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, ChordQuality]] = {
        1: ChordQuality.MAJOR,
        2: ChordQuality.MINOR,
        3: ChordQuality.MINOR,
        4: ChordQuality.MAJOR,
        5: ChordQuality.MAJOR,
        6: ChordQuality.MINOR,
        7: ChordQuality.DIMINISHED
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, ChordQuality]] = {
        1: ChordQuality.MINOR,
        2: ChordQuality.DIMINISHED,
        3: ChordQuality.MAJOR,
        4: ChordQuality.MINOR,
        5: ChordQuality.MINOR,
        6: ChordQuality.MAJOR,
        7: ChordQuality.MAJOR
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
        scale_notes = scale.generate_notes()
        
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

    def get_quality_for_degree(self, degree: int) -> Chord:
        """Get the chord quality for a given scale degree."""
        if not (1 <= degree <= 7):
            raise ValueError("Scale degree must be between 1 and 7")
            
        # Define chord qualities for major and minor scales
        if self.scale_type == ScaleType.MAJOR:
            return Chord(root=self.get_note_for_degree(degree), quality=self.MAJOR_SCALE_QUALITIES[degree])
        else:
            return Chord(root=self.get_note_for_degree(degree), quality=self.MINOR_SCALE_QUALITIES[degree])

    def get_note_for_degree(self, degree: int) -> Note:
        """Get the note for a given scale degree."""
        scale = self._get_scale()
        return scale.get_scale_degree(degree)

    def get_chord_quality_for_degree(self, degree: int) -> ChordQuality:
        """Return the chord quality for a given scale degree."""
        logger.debug(f"Getting chord quality for degree {degree} in {self.scale_type} scale")
        
        if self.scale_type == ScaleType.MAJOR:
            quality = self.MAJOR_SCALE_QUALITIES.get(degree, ChordQuality.DIMINISHED)
            logger.debug(f"For degree {degree} in MAJOR scale, using quality: {quality}")
            return quality
        elif self.scale_type == ScaleType.MINOR:
            quality = self.MINOR_SCALE_QUALITIES.get(degree, ChordQuality.DIMINISHED)
            logger.debug(f"For degree {degree} in MINOR scale, using quality: {quality}")
            return quality
            
        # If we get here, it's an error
        logger.error(f"Invalid scale type: {self.scale_type} for degree: {degree}")
        raise ValueError(f"Invalid degree: {degree} or scale type: {self.scale_type}")

    def get_scale_note_at_degree(self, degree: int) -> Note:
        """Return the note at a given scale degree."""
        if not self._scale:
            self._scale = Scale(root=self.root, scale_type=self.scale_type)
        
        # Adjust for 1-based indexing
        index = degree - 1
        
        # Ensure the degree is within the scale's range
        if index < 0 or index >= len(self._scale.notes):
            raise ValueError(f"Invalid scale degree: {degree}")
        
        return self._scale.notes[index]

    @classmethod
    def validate_fake_scale(cls, fake_scale: 'FakeScaleInfo') -> None:
        # Implementation
        pass
