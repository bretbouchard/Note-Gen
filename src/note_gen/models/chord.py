# src/note_gen/models/chord.py
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator
import logging

from src.note_gen.models.note import Note
from src.note_gen.models.chord_quality import ChordQualityType

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chord(BaseModel):
    """A musical chord consisting of a root note and quality."""
    root: Note
    quality: Optional[ChordQualityType] = Field(default=ChordQualityType.MAJOR)
    notes: Optional[List[Note]] = Field(default=None)
    inversion: int = Field(default=0, description="Inversion of the chord (0 = root position)")

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    @field_validator('quality', mode='before')
    @classmethod
    def validate_quality(cls, v: Union[str, ChordQualityType]) -> ChordQualityType:
        """Validate and convert the quality field."""
        if isinstance(v, str):
            try:
                return ChordQualityType.from_string(v)
            except ValueError as e:
                raise ValueError(f"Invalid chord quality: {v}") from e
        return v

    @field_validator('inversion')
    @classmethod
    def validate_inversion(cls, v: int) -> int:
        """Validate the inversion value."""
        if v < 0:
            raise ValueError("Inversion cannot be negative")
        return v

    def _generate_chord_notes(self) -> List[Note]:
        """Generate the notes that make up this chord."""
        intervals = self.quality.get_intervals()
        root_midi = self.root.midi_number
        notes: List[Note] = [self.root]
        
        for interval in intervals[1:]:  # Skip first interval (0) since we already have root
            next_midi = root_midi + interval
            next_note = Note.from_midi(next_midi, duration=int(self.root.duration))
            # Set velocity to match root note
            next_note.velocity = self.root.velocity
            notes.append(next_note)
            
        return notes

    def generate_notes(self) -> List[Note]:
        logger.info("Generating notes for chord...")  # Log when generating notes
        if self.notes is None:  # Only generate if notes haven't been generated yet
            self.notes = self._generate_chord_notes()

        # Apply inversion if specified
        if self.inversion > 0:
            notes = self.notes.copy()
            for _ in range(self.inversion):
                # Move the first note up an octave
                first_note = notes.pop(0)
                notes.append(first_note.transpose(12))
            self.notes = notes

        logger.info("Notes generated successfully.")  # Log successful generation
        return self.notes

    def get_notes(self) -> List[Note]:
        logger.info("Getting notes for chord...")  # Log when getting notes
        return self.generate_notes()

    @classmethod
    def from_string(cls, chord_str: str) -> 'Chord':
        """Create a Chord from a string representation (e.g., 'C', 'Dm', 'G7')."""
        # Parse the root note
        root_end = 1
        if len(chord_str) > 1 and chord_str[1] in ['#', 'b']:
            root_end = 2
        root_str = chord_str[:root_end]
        
        # Default to MAJOR if no quality specified
        quality = ChordQualityType.MAJOR
        
        # Parse the quality if present
        if len(chord_str) > root_end:
            quality_str = chord_str[root_end:]
            quality = ChordQualityType.from_string(quality_str)
        
        # Create the root note (default to octave 4)
        root = Note(note_name=root_str, octave=4)
        
        return cls(root=root, quality=quality)

    @classmethod
    def from_quality(cls, root: Note, quality: str) -> 'Chord':
        """Create a chord from a root note and quality string."""
        quality_type = ChordQualityType.from_string(quality)
        return cls(root=root, quality=quality_type)

    def transpose(self, semitones: int) -> 'Chord':
        """Transpose the chord by the given number of semitones."""
        new_root = self.root.transpose(semitones)
        return Chord(root=new_root, quality=self.quality, inversion=self.inversion)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'root': self.root,
            'quality': self.quality,
            'notes': [note.to_dict() for note in self.notes] if self.notes is not None else None,
            'inversion': self.inversion
        }

    def some_function(self) -> None:
        # Function implementation
        pass

    def another_function(self) -> None:
        # Example logic to demonstrate reachability
        if self.notes is not None:
            for note in self.notes:
                print(note.to_dict())  # Print each note's dictionary representation
        else:
            print("No notes available")
