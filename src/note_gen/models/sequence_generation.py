"""Models for sequence generation."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .note import Note
from .patterns import Pattern

class SequenceGeneration(BaseModel):
    """Model for sequence generation parameters and methods."""
    
    def create_note(self, note_str: str, **kwargs) -> Note:
        """Create a Note from a note string (e.g. 'C4')."""
        # Parse note string to get pitch and octave
        if len(note_str) < 2:
            raise ValueError(f"Invalid note string: {note_str}")
            
        pitch = note_str[:-1]  # Everything except last character
        try:
            octave = int(note_str[-1])  # Last character should be octave
        except ValueError:
            raise ValueError(f"Invalid octave in note string: {note_str}")
            
        return Note(
            pitch=pitch,
            octave=octave,
            **kwargs
        )

    def create_sequence_note(self, position: float = 0.0, **kwargs) -> Note:
        """Create a note for a sequence with given position."""
        return Note(
            pitch="C",  # Default pitch
            octave=4,   # Default octave
            position=position,
            **kwargs
        )

    def create_pattern_note(self, pattern: Pattern, index: int, **kwargs) -> Note:
        """Create a note based on pattern parameters."""
        return Note(
            pitch="C",  # Default pitch
            octave=4,   # Default octave
            position=float(index),
            **kwargs
        )

    def process_note(self, note_str: str, position: float = 0.0) -> Note:
        """Process and create a note with position."""
        if len(note_str) < 2:
            raise ValueError(f"Invalid note string: {note_str}")
            
        pitch = note_str[:-1]
        try:
            octave = int(note_str[-1])
        except ValueError:
            raise ValueError(f"Invalid octave in note string: {note_str}")
            
        return Note(
            pitch=pitch,
            octave=octave,
            position=position
        )

    def create_note_sequence(self, notes: List[str], **kwargs) -> List[Note]:
        """Create a sequence of notes from string representations."""
        return [self.process_note(note_str, float(i)) for i, note_str in enumerate(notes)]
