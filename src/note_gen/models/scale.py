"""Scale model definition."""
from typing import List, Tuple, Optional, Union, Dict, Any
import re
from pydantic import Field, field_validator, ConfigDict, model_validator
from src.note_gen.models.base import BaseModelWithConfig
from src.note_gen.models.note import Note
from src.note_gen.core.enums import ScaleType

class ScaleInfo(BaseModelWithConfig):
    """Information about a musical scale."""
    
    key: str = Field(..., pattern=r'^[A-G][b#]?\d*$')  # Allow optional octave number
    scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    
    @property
    def root_note(self) -> Note:
        """Get the root note of the scale."""
        return Note.from_name(self.key)

class Scale(BaseModelWithConfig):
    """Model representing a musical scale."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    root: Union[str, Note]
    scale_type: ScaleType

    @model_validator(mode='before')
    def _validate_root_input(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(values.get('root'), str):
            values['root'] = Note.from_name(values['root'])
        return values

    notes: List[Note] = Field(default_factory=list, description="Notes in the scale")
    octave_range: tuple[int, int] = Field(default=(4, 5), description="Range of octaves (min, max)")

    def generate_notes(self) -> 'Scale':
        """Generate the notes of the scale based on root note and scale type."""
        intervals = self.scale_type.intervals
        root_midi = self.root.to_midi_number()
        if root_midi is None:
            raise ValueError("Root note has no valid MIDI number")
        
        self.notes = []
        for interval in intervals:
            note_midi = root_midi + interval
            if 0 <= note_midi <= 127:  # Check MIDI number is valid
                self.notes.append(Note.from_midi_number(note_midi))
        
        return self  # Return self for method chaining

    @field_validator('root')
    def _validate_root_type(cls, v: Note) -> Note:
        """Validate the root note."""
        if not isinstance(v, Note):
            if isinstance(v, str):
                return Note.from_name(v)
            raise ValueError("Root must be a Note instance or a valid note name string")
        return v

    @classmethod
    def from_root(cls, root: str, scale_type: ScaleType = ScaleType.MAJOR, **kwargs) -> 'Scale':
        """Create a scale from a root note name."""
        root_note = Note.from_name(root) if isinstance(root, str) else root
        scale = cls(root=root_note, scale_type=scale_type, **kwargs)
        return scale.generate_notes()

    def get_degree(self, degree: int) -> Optional[Note]:
        """Get the note at the specified scale degree (1-based)."""
        if not 1 <= degree <= len(self.notes):
            return None
        return self.notes[degree - 1]

    def contains_note(self, note: Note) -> bool:
        """Check if a note is in the scale."""
        note_midi = note.to_midi_number()
        if note_midi is None:
            return False
        return any(
            (n.to_midi_number() or 0) % 12 == note_midi % 12 
            for n in self.notes
        )

    def transpose(self, semitones: int) -> 'Scale':
        """Create a new scale transposed by the specified number of semitones."""
        new_root = self.root.transpose(semitones)
        new_scale = Scale(root=new_root, scale_type=self.scale_type)
        return new_scale.generate_notes()

    def get_notes_in_range(self, min_midi: int = 21, max_midi: int = 108) -> List[Note]:
        """Get all scale notes within the specified MIDI range."""
        result: List[Note] = []
        for note in self.notes:
            midi_num = note.to_midi_number()
            if midi_num is not None and min_midi <= midi_num <= max_midi:
                result.append(note)
        return result

    def get_note_by_degree(self, degree: int) -> Optional[Note]:
        """Get note by scale degree."""
        if not isinstance(degree, int) or degree < 1:
            return None
        # Implementation...

    def get_scale_notes(self) -> List[Note]:
        """Get all notes in the scale."""
        # Implementation...
        return []

    def __str__(self) -> str:
        """Return string representation of scale."""
        # Remove octave from string representation
        root_without_octave = self.root.pitch if self.root else "?"
        return f"{root_without_octave} {self.scale_type.name}"
