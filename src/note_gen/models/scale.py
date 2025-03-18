from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, computed_field
from .note import Note
from .enums import ScaleType
from .scale_info import ScaleInfo
from .chord import Chord
from .chord_quality import ChordQuality

class Scale(BaseModel):
    """Represents a musical scale."""
    root: Note
    scale_type: ScaleType
    notes: List[Note] = Field(default_factory=list)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    def __init__(self, **data):
        super().__init__(**data)
        if not self.notes:
            self.notes = self._generate_scale_notes()

    def _generate_scale_notes(self) -> List[Note]:
        """Generate the notes of the scale based on root note and scale type."""
        intervals = self.scale_type.get_intervals()
        scale_notes = []
        root_midi = self.root.midi_number
        
        for interval in intervals:  # Use all intervals including 0
            note = Note.from_midi_number(root_midi + interval)
            scale_notes.append(note)
            
        return scale_notes

    def get_scale_degree(self, degree: int) -> Note:
        """Get the note at a specific scale degree (1-based indexing)."""
        if not self.scale_type.validate_degree(degree):
            raise ValueError(f"Invalid scale degree {degree} for {self.scale_type.value}")
        return self.notes[degree - 1]

    def get_note_from_degree(self, degree: int) -> Note:
        """Alias for get_scale_degree."""
        return self.get_scale_degree(degree)

    def get_degree_of_note(self, note: Note) -> Optional[int]:
        """Get the scale degree of a note (1-based indexing)."""
        note_name = note.note_name
        for i, scale_note in enumerate(self.notes, 1):
            if scale_note.note_name == note_name:
                return i
        return None

    def get_chord_by_degree(self, degree: int, quality: ChordQuality = ChordQuality.MAJOR) -> Chord:
        """Get the chord built on a specific scale degree."""
        if not self.scale_type.validate_degree(degree):
            raise ValueError(f"Invalid scale degree {degree} for {self.scale_type.value}")
        root_note = self.get_scale_degree(degree)
        return Chord(root=root_note, quality=quality)

    @classmethod
    def from_scale_info(cls, scale_info: ScaleInfo) -> 'Scale':
        """Create a Scale instance from ScaleInfo."""
        root_note = Note.from_note_name(scale_info.key)
        return cls(
            root=root_note,
            scale_type=scale_info.scale_type
        )

    @computed_field
    @property
    def degree_count(self) -> int:
        """Get the number of degrees in the scale."""
        return len(self.notes)

    def __str__(self) -> str:
        return f"{self.root.note_name} {self.scale_type.value}"

    def __len__(self) -> int:
        return len(self.notes)
