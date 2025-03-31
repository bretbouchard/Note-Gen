"""Models for note sequences."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .scale_info import ScaleInfo
from src.note_gen.models.note import Note
from src.note_gen.validation.musical_validation import validate_note_sequence
from src.note_gen.core.enums import ValidationLevel

class NoteSequence(BaseModel):
    notes: List[Note]
    metadata: Dict[str, Any] = {}
    scale_info: Optional[ScaleInfo] = None
    progression_name: Optional[str] = None
    note_pattern_name: Optional[str] = None
    rhythm_pattern_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NoteSequence':
        """Create a NoteSequence from a dictionary."""
        # Convert dictionary notes to Note objects
        notes = [Note(**note_data) if isinstance(note_data, dict) else note_data 
                for note_data in data.get('notes', [])]
        return cls(notes)

    def validate(self, level: ValidationLevel = ValidationLevel.NORMAL) -> bool:
        """Validate the note sequence."""
        # Pass the list of notes, not the dictionary
        return validate_note_sequence(self.notes, level).is_valid
