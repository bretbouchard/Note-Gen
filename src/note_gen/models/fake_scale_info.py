from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.scale import Scale
from typing import Optional, Any, Dict, ClassVar, List
import logging

logger = logging.getLogger(__name__)

class FakeScaleInfo(BaseModel):
    root: Note
    scale_type: ScaleType
    complexity: float = Field(default=0.0, ge=0.0, le=1.0)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('scale_type', mode='before')
    @classmethod
    def validate_scale_type(cls, v: Any) -> ScaleType:
        logger.debug('Validating scale type: %s', v)
        if not isinstance(v, ScaleType):
            try:
                v = ScaleType(v)
            except ValueError as e:
                logger.error('Invalid scale type: %s', v)
                raise ValueError(f'Invalid scale type: {v}') from e
        return v

    @field_validator('complexity', mode='before')
    @classmethod
    def validate_complexity(cls, v: Any) -> float:
        logger.debug('Validating complexity: %s', v)
        if not isinstance(v, (int, float)):
            try:
                v = float(v)
            except (TypeError, ValueError) as e:
                logger.error('Invalid complexity value: %s', v)
                raise ValueError(f'Complexity must be a number, got {v}') from e

        if not 0.0 <= v <= 1.0:
            logger.error('Complexity out of range: %s', v)
            raise ValueError(f'Complexity must be between 0.0 and 1.0, got {v}')
        return v

    # Define a root note as a ClassVar
    root_note: ClassVar[Note] = Note(note_name='C', octave=4)

    # Scale quality mappings
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

    _scale: Optional[Scale] = None  # Cache for Scale instance

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

        logger.error(f"Invalid scale type: {self.scale_type} for degree: {degree}")
        raise ValueError(f"Invalid degree: {degree} or scale type: {self.scale_type}")

    def get_scale_note_at_degree(self, degree: int) -> Note:
        """Return the note at a given scale degree."""
        scale = self._get_scale()
        notes = scale.notes or []
        index = degree - 1

        if index < 0 or index >= len(notes):
            raise ValueError(f"Invalid scale degree: {degree}")

        return notes[index]

    @classmethod
    def validate_fake_scale(cls, fake_scale: 'FakeScaleInfo') -> None:
        pass
