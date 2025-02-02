from typing import List, Optional
from pydantic import BaseModel

from .note import Note
from .scale_type import ScaleType

class Scale(BaseModel):
    """A musical scale."""
    root: Note
    scale_type: ScaleType
    notes: Optional[List[Note]] = None

    def generate_notes(self) -> List[Note]:
        """Generate all notes in the scale.
        
        Returns:
            List[Note]: List of notes in the scale
            
        Raises:
            ValueError: If any note in the scale would be outside valid MIDI range (0-127)
        """
        intervals = self.scale_type.get_intervals()
        root_midi = self.root.midi_number
        notes = []

        # Start with the root note
        notes.append(self.root)

        for interval in intervals:
            try:
                # Create a new note for each interval
                new_midi = root_midi + interval
                note = Note.from_midi_number(
                    midi_number=new_midi,
                    duration=self.root.duration,
                    velocity=self.root.velocity
                )
                notes.append(note)
            except ValueError as e:
                # Provide a more helpful error message
                raise ValueError(
                    f"Cannot generate scale: note at interval {interval} "
                    f"from root {self.root.note_name}{self.root.octave} "
                    f"would be outside valid MIDI range (0-127). "
                    f"Try using a different octave for the root note."
                ) from e
        
        self.notes = notes
        return notes

    def get_scale_degree(self, degree: int) -> Note:
        """Get a note at a specific scale degree (1-based indexing).
        
        Args:
            degree: The scale degree (1-based indexing)
            
        Returns:
            Note: The note at the specified scale degree
            
        Raises:
            ValueError: If the degree is not valid for this scale
        """
        if not self.notes:
            self.generate_notes()

        # Get the number of unique notes in the scale (excluding octave)
        scale_length = len(self.scale_type.get_intervals())
        
        if not 1 <= degree <= scale_length:
            raise ValueError(f"Scale degree must be between 1 and {scale_length}")
        
        return self.notes[degree - 1]

    def get_triad(self, degree: int) -> List[Note]:
        """Get a triad starting at the given scale degree (1-based indexing).
        
        Args:
            degree: The scale degree (1-based indexing)
            
        Returns:
            List[Note]: Three notes forming the triad
            
        Raises:
            ValueError: If the degree is not valid for this scale
        """
        if not self.notes:
            self.generate_notes()
        
        # Get the number of unique notes in the scale (excluding octave)
        scale_length = len(self.scale_type.get_intervals())
        
        if not 1 <= degree <= scale_length:
            raise ValueError(f"Scale degree must be between 1 and {scale_length}")
        
        # Get notes at positions 1, 3, and 5 relative to the degree
        positions = [degree - 1, degree + 1, degree + 3]
        if any(pos >= scale_length for pos in positions):
            raise ValueError(f"Cannot build triad at degree {degree} - would exceed scale length")
        
        return [self.notes[pos] for pos in positions]

    def transpose(self, semitones: int) -> 'Scale':
        """Transpose the scale by a number of semitones."""
        new_root = self.root.transpose(semitones)
        return Scale(root=new_root, scale_type=self.scale_type)