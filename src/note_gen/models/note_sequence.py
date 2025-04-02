"""Models for note sequences."""
from typing import List, Optional, Dict, Any, Tuple
from pydantic import Field
from note_gen.models.note import Note
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.sequence import Sequence
from note_gen.core.constants import DEFAULTS
from note_gen.validation.base_validation import ValidationResult
from note_gen.core.enums import ValidationLevel
from note_gen.validation.sequence_validation import validate_note_sequence

class NoteSequence(Sequence):
    """Model for note sequences."""
    notes: List[Note] = Field(default_factory=list, description="List of notes in the sequence")
    duration: float = Field(default=DEFAULTS["duration"], description="Duration in beats")
    tempo: int = Field(default=DEFAULTS["bpm"], description="Tempo in beats per minute")
    time_signature: Tuple[int, int] = Field(
        default=DEFAULTS["time_signature"],
        description="Time signature as (numerator, denominator)"
    )
    scale_info: Optional[Dict[str, Any]] = None
    chord_progression: Optional[Dict[str, Any]] = None
    progression_name: Optional[str] = None
    note_pattern_name: Optional[str] = None
    rhythm_pattern_name: Optional[str] = None

    def validate_sequence(self, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate the sequence using sequence validation rules."""
        result = validate_note_sequence(self.notes, level)

        # Additional validations
        total_duration = sum(note.duration for note in self.notes)
        if abs(total_duration - self.duration) > 0.001:  # Allow small floating-point differences
            result.add_error(
                field="duration",
                message=f"Total duration ({self.duration}) does not match sum of note durations ({total_duration})"
            )

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert sequence to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "notes": [note.model_dump() for note in self.notes],
            "duration": self.duration,
            "tempo": self.tempo,
            "time_signature": self.time_signature,
            "scale_info": self.scale_info if self.scale_info else None,
            "progression_name": self.progression_name,
            "note_pattern_name": self.note_pattern_name,
            "rhythm_pattern_name": self.rhythm_pattern_name
        })
        return base_dict

    def clone(self) -> 'NoteSequence':
        """Create a deep copy of the sequence."""
        return self.__class__(**self.model_dump())

    def transpose(self, semitones: int) -> 'NoteSequence':
        """Create a new sequence with all notes transposed by the specified number of semitones."""
        new_sequence = self.clone()
        new_sequence.notes = [note.transpose(semitones) for note in self.notes]
        return new_sequence

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
