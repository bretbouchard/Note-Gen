from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict
from src.note_gen.core.enums import ChordQuality, ScaleType
from src.note_gen.models.note import Note

class Chord(BaseModel):
    root: Note
    quality: ChordQuality
    notes: List[Note] = Field(default_factory=list)
    inversion: int = Field(0, ge=0)  # Must be non-negative
    
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    @staticmethod
    def _enharmonic_note_name(note_name: str) -> str:
        """Convert to enharmonic equivalent for consistent comparisons."""
        enharmonic_map = {
            "C#": "Db", "Db": "C#",
            "D#": "Eb", "Eb": "D#",
            "F#": "Gb", "Gb": "F#",
            "G#": "Ab", "Ab": "G#",
            "A#": "Bb", "Bb": "A#"
        }
        return enharmonic_map.get(note_name, note_name)

    @field_validator('root', mode='before')
    @classmethod
    def validate_root(cls, v: Any) -> Note:
        """Convert string to Note object if possible."""
        if isinstance(v, str):
            try:
                return Note.from_note_name(v)
            except ValueError as e:
                raise ValueError(f"Invalid root note: {v}. {str(e)}")
        return v

    @field_validator('quality', mode='before')
    @classmethod
    def validate_quality(cls, v: Any) -> ChordQuality:
        """Convert string to ChordQuality enum if possible."""
        if isinstance(v, str):
            if v == '':  # Default to MAJOR for empty string
                return ChordQuality.MAJOR
            try:
                return ChordQuality(v)
            except ValueError:
                raise ValueError(f"Invalid chord quality: {v}")
        return v

    @field_validator('inversion')
    @classmethod
    def validate_inversion(cls, v: int) -> int:
        """Validate that inversion is non-negative."""
        if v < 0:
            raise ValueError(f"Inversion must be non-negative, got {v}")
        return v

    @model_validator(mode='after')
    def generate_notes(self) -> 'Chord':
        """Generate chord notes based on root and quality if not provided."""
        if not self.notes:
            # Define intervals for different chord qualities
            interval_map = {
                ChordQuality.MAJOR: [0, 4, 7],
                ChordQuality.MINOR: [0, 3, 7],
                ChordQuality.DIMINISHED: [0, 3, 6],
                ChordQuality.AUGMENTED: [0, 4, 8],
                ChordQuality.DOMINANT7: [0, 4, 7, 10],
                ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
                ChordQuality.MAJOR7: [0, 4, 7, 11],
                ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
                ChordQuality.MINOR7: [0, 3, 7, 10],
                ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
                ChordQuality.DIMINISHED7: [0, 3, 6, 9],
                ChordQuality.HALF_DIMINISHED7: [0, 3, 6, 10],
                ChordQuality.MAJOR9: [0, 4, 7, 11, 14],
                ChordQuality.MINOR9: [0, 3, 7, 10, 14]
            }
            
            # Get intervals for the chord quality
            intervals = interval_map.get(self.quality, [0, 4, 7])  # Default to major if not found
            
            # Generate notes based on intervals
            self.notes = [self.root.clone()]  # Start with the root note
            
            # Add the rest of the notes
            for interval in intervals[1:]:
                new_note = self.root.transpose(interval)
                self.notes.append(new_note)
            
            # Apply inversion if specified
            for _ in range(self.inversion):
                if self.notes:
                    # Move the lowest note up an octave
                    lowest_note = self.notes.pop(0)
                    transposed_note = lowest_note.transpose(12)  # Up an octave
                    self.notes.append(transposed_note)
        
        return self
    
    def to_string(self) -> str:
        """
        Convert the chord to a string representation.
        
        Returns:
            String representation of the chord (e.g., "C", "Dm", "G7")
        """
        quality_symbols = {
            ChordQuality.MAJOR: "",
            ChordQuality.MINOR: "m",
            ChordQuality.DIMINISHED: "dim",
            ChordQuality.AUGMENTED: "aug",
            ChordQuality.DOMINANT7: "7",
            ChordQuality.DOMINANT_SEVENTH: "7",
            ChordQuality.MAJOR7: "M7",
            ChordQuality.MAJOR_SEVENTH: "M7",
            ChordQuality.MINOR7: "m7",
            ChordQuality.MINOR_SEVENTH: "m7",
            ChordQuality.DIMINISHED7: "dim7",
            ChordQuality.HALF_DIMINISHED7: "m7b5",
            ChordQuality.MAJOR9: "M9",
            ChordQuality.MINOR9: "m9"
        }
        
        # Get the symbol for the chord quality
        symbol = quality_symbols.get(self.quality, "")
        
        # Combine root and quality symbol
        return f"{self.root.note_name}{symbol}"
    
    def __str__(self) -> str:
        """String representation of the chord."""
        return self.to_string()
