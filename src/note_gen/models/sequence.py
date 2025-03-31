"""Models for musical sequences."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from src.note_gen.models.note import Note
from src.note_gen.core.constants import DEFAULTS
from src.note_gen.validation.base_validation import ValidationResult
from src.note_gen.core.enums import ValidationLevel
from src.note_gen.validation.sequence_validation import validate_note_sequence

class NoteSequenceBase(BaseModel):
    """Base model for note sequences."""
    notes: List[Note] = Field(default_factory=list, description="List of notes in the sequence")
    duration: float = Field(default=DEFAULTS["duration"], description="Duration in beats")
    tempo: int = Field(default=DEFAULTS["bpm"], description="Tempo in beats per minute")
    time_signature: tuple[int, int] = Field(
        default=DEFAULTS["time_signature"],
        description="Time signature as (numerator, denominator)"
    )
    name: str = Field(default="", description="Name of the sequence")

    def validate_sequence(self, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate the sequence using sequence validation rules."""
        data = self.model_dump()
        return validate_note_sequence(data, level)

    def to_dict(self) -> Dict[str, Any]:
        """Convert sequence to dictionary."""
        return {
            "notes": [note.model_dump() for note in self.notes],
            "duration": self.duration,
            "tempo": self.tempo,
            "time_signature": self.time_signature,
            "name": self.name
        }

    def clone(self) -> 'NoteSequenceBase':
        """Create a deep copy of the sequence."""
        return self.__class__(**self.model_dump())

    def transpose(self, semitones: int) -> 'NoteSequenceBase':
        """Create a new sequence with all notes transposed by the specified number of semitones."""
        new_sequence = self.clone()
        new_sequence.notes = [note.transpose(semitones) for note in self.notes]
        return new_sequence

class NoteSequenceCreate(NoteSequenceBase):
    """Model for creating a new note sequence."""
    pass

class NoteSequence(NoteSequenceBase):
    """Model for a note sequence with database ID."""
    id: str = Field(description="Unique identifier")
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    def validate_all(self, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Run all validations on the sequence."""
        # First validate basic sequence structure
        result = self.validate_sequence(level)
        if not result.is_valid:
            return result

        # Additional validations could be added here
        # For example, validating total duration matches time signature
        total_duration = sum(note.duration for note in self.notes)
        if abs(total_duration - self.duration) > 0.001:  # Allow small floating-point differences
            result.add_error(
                field="duration",
                message=f"Total duration ({self.duration}) does not match sum of note durations ({total_duration})"
            )
            result.add_violation(
                code="DURATION_MISMATCH",
                message=f"Total duration ({self.duration}) does not match sum of note durations ({total_duration})",
                path="sequence.duration"
            )

        return result

    @classmethod
    def from_notes(cls, notes: List[Note], **kwargs) -> 'NoteSequence':
        """Create a sequence from a list of notes."""
        total_duration = sum(note.duration for note in notes)
        return cls(
            notes=notes,
            duration=total_duration,
            **kwargs
        )

    @classmethod
    def empty(cls, **kwargs) -> 'NoteSequence':
        """Create an empty sequence."""
        return cls(notes=[], **kwargs)
