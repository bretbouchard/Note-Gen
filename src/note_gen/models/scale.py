from typing import List, Optional
from pydantic import BaseModel

from src.note_gen.models.note import Note
from src.note_gen.models.enums import ScaleType

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
        
        if self.notes is not None:
            return self.notes[degree - 1]
        else:
            raise ValueError("Notes have not been generated for this scale")

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
        
        if self.notes is not None:
            return [self.notes[pos] for pos in positions]
        else:
            raise ValueError("Notes have not been generated for this scale")

    def get_degree_of_note(self, note: Note) -> int:
        """Get the scale degree of a note within the scale.
        
        Args:
            note: The note to find the degree for.
            
        Returns:
            int: The scale degree (1-based indexing).
            
        Raises:
            ValueError: If the note is not in the scale.
        """
        if note not in self.notes:
            raise ValueError(f"{note} is not in the scale.")
        return self.notes.index(note) + 1  # 1-based indexing

    def get_note_by_degree(self, degree: int) -> Note:
        """Get a note at a specific scale degree (1-based indexing).
        
        Args:
            degree: The scale degree (1-based indexing).
            
        Returns:
            Note: The note at the specified scale degree.
            
        Raises:
            ValueError: If the degree is not valid for this scale.
        """
        if degree < 1 or degree > len(self.notes):
            raise ValueError(f"Degree {degree} is out of range for this scale.")
        return self.notes[degree - 1]  # Convert to 0-based indexing

    def transpose(self, semitones: int) -> 'Scale':
        """Transpose the scale by a number of semitones."""
        new_root = self.root.transpose(semitones)
        return Scale(root=new_root, scale_type=self.scale_type)