"""Scale models and related functionality."""
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.note_gen.core.enums import ScaleType  # Import from centralized location
from src.note_gen.core.constants import SCALE_INTERVALS
from .note import Note

class Scale(BaseModel):
    """Scale model with full implementation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    root: Note
    scale_type: ScaleType
    octave: int = 4
    notes: Optional[List[Note]] = None
    
    @model_validator(mode='after')
    def ensure_notes(self) -> 'Scale':
        """Ensure notes list is populated."""
        if self.notes is None:
            self.notes = self._generate_scale_notes()
        return self

    def _generate_scale_notes(self) -> List[Note]:
        """Generate the notes for this scale."""
        if not isinstance(self.scale_type, ScaleType):
            raise ValueError(f"Invalid scale type: {self.scale_type}")
            
        # Get intervals for this scale type
        intervals = SCALE_INTERVALS.get(self.scale_type)
        if not intervals:
            raise ValueError(f"No intervals defined for scale type: {self.scale_type}")
        
        # Generate notes based on root note and intervals
        root_midi = self.root.midi_number
        result = [self.root]  # Start with the root note
        
        for interval in intervals[1:]:  # Skip the first interval (0) as it's the root
            # Calculate new midi number
            new_midi = root_midi + interval
            
            # Create new note
            if self.root.prefer_flats:
                note_name = Note.SEMITONE_TO_FLAT[new_midi % 12]
            else:
                note_name = Note.SEMITONE_TO_SHARP[new_midi % 12]
                
            octave = (new_midi // 12) - 1
            
            # Create the note with proper parameters
            note = Note(
                note_name=note_name,
                octave=octave,
                duration=self.root.duration,
                velocity=self.root.velocity,
                position=self.root.position,
                stored_midi_number=new_midi,  # Set the stored_midi_number
                scale_degree=intervals.index(interval) + 1,  # Set the scale degree based on the interval index
                prefer_flats=self.root.prefer_flats  # Inherit prefer_flats from the root note
            )
            result.append(note)
            
        return result

    def get_note_at_position(self, position: int) -> Optional[Note]:
        """
        Get the note at the specified scale position (0-based index).
        
        Args:
            position: The position in the scale (0 = tonic, 1 = second, etc.)
            
        Returns:
            The Note at the specified position, or None if position is invalid.
        """
        if not self.notes:
            self.notes = self._generate_scale_notes()
            
        # Handle degree within the scale's range
        if 0 <= position < len(self.notes):
            return self.notes[position]
            
        # Handle degrees outside the scale's range (modulo calculation)
        if self.notes:
            # Calculate octaves and position within the scale
            octaves = position // len(self.notes)
            position_in_scale = position % len(self.notes)
            
            # Get the base note and adjust octave
            base_note = self.notes[position_in_scale]
            if base_note:
                # Create a new note with adjusted octave
                return Note(
                    note_name=base_note.note_name,
                    octave=base_note.octave + octaves,
                    duration=base_note.duration,
                    velocity=base_note.velocity,
                    position=base_note.position,
                    prefer_flats=base_note.prefer_flats,
                    stored_midi_number=None,  # Will be calculated automatically
                    scale_degree=base_note.scale_degree if hasattr(base_note, 'scale_degree') else None
                )
        
        return None
