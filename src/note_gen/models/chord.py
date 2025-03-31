"""Chord model definition."""
from typing import Optional, List, Dict, ClassVar, Union
from pydantic import Field, ConfigDict, field_validator, model_validator
from .base import BaseModelWithConfig
from .note import Note
from ..core.enums import ChordQuality  # Updated import

class Chord(BaseModelWithConfig):
    """Model representing a musical chord."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    root: str = Field(..., description="Root note of the chord")
    quality: ChordQuality = Field(default=ChordQuality.MAJOR, description="Quality of the chord")
    notes: List[Note] = Field(default_factory=list)
    duration: float = Field(default=1.0, gt=0, description="Duration in beats")
    velocity: int = Field(default=64, ge=0, le=127, description="MIDI velocity (0-127)")
    octave: Optional[int] = Field(default=None, ge=0, le=8, description="Octave number")

    @field_validator('root', mode='before')
    @classmethod
    def validate_root(cls, v: Union[str, Note]) -> str:
        """Validate root note."""
        if isinstance(v, Note):
            return v.pitch
        try:
            return Note.normalize_pitch(v)
        except ValueError as e:
            raise ValueError(f"Invalid root note: {v}") from e

    @model_validator(mode='after')
    def validate_chord(self) -> 'Chord':
        """Validate the entire chord model."""
        if self.octave is not None and not (0 <= self.octave <= 8):
            raise ValueError("Octave must be between 0 and 8")
        if not (0 <= self.velocity <= 127):
            raise ValueError("Velocity must be between 0 and 127")
        if self.duration <= 0:
            raise ValueError("Duration must be positive")
        return self

    # Class variable for chord quality intervals
    QUALITY_INTERVALS: ClassVar[Dict[ChordQuality, List[int]]] = {
        ChordQuality.MAJOR: [0, 4, 7],
        ChordQuality.MINOR: [0, 3, 7],
        ChordQuality.DIMINISHED: [0, 3, 6],
        ChordQuality.AUGMENTED: [0, 4, 8],
        ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
        ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
        ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
        ChordQuality.DIMINISHED_SEVENTH: [0, 3, 6, 9],
        ChordQuality.HALF_DIMINISHED_SEVENTH: [0, 3, 6, 10],
        ChordQuality.SUSPENDED_SECOND: [0, 2, 7],
        ChordQuality.SUSPENDED_FOURTH: [0, 5, 7]
    }

    def get_notes(self) -> List[Note]:
        """Get the list of notes in the chord."""
        if not self.notes:
            self._generate_notes()
        return self.notes

    def _generate_notes(self) -> None:
        """Generate the notes for this chord based on root and quality."""
        # Create the base note with octave in the name string
        base_note = Note.from_name(f"{self.root}4")  # Use middle octave as default
        intervals = self.QUALITY_INTERVALS[self.quality]
        
        self.notes = []
        for interval in intervals:
            note = base_note.transpose(interval)
            self.notes.append(note)

    def transpose(self, semitones: int) -> 'Chord':
        """
        Create a new chord transposed by the specified number of semitones.
        
        Args:
            semitones: Number of semitones to transpose by
            
        Returns:
            Chord: New transposed chord
        """
        base_note = Note.from_name(self.root, octave=4)
        transposed_note = base_note.transpose(semitones)
        
        return Chord(
            root=transposed_note.note_name,
            quality=self.quality
        )

    def to_symbol(self) -> str:
        """
        Convert the chord to its symbol representation.
        
        Returns:
            str: Chord symbol (e.g., 'C', 'Am', 'F7')
        """
        quality_symbols = {
            ChordQuality.MAJOR: '',
            ChordQuality.MINOR: 'm',
            ChordQuality.DIMINISHED: 'dim',
            ChordQuality.AUGMENTED: 'aug',
            ChordQuality.MAJOR_SEVENTH: 'maj7',
            ChordQuality.MINOR_SEVENTH: 'm7',
            ChordQuality.DOMINANT_SEVENTH: '7'
        }
        return f"{self.root}{quality_symbols[self.quality]}"

    @classmethod
    def from_symbol(cls, symbol: str) -> 'Chord':
        """
        Create a Chord instance from a chord symbol.
        
        Args:
            symbol: Chord symbol (e.g., 'C', 'Am', 'F7')
            
        Returns:
            Chord: New chord instance
        """
        # Parse root note
        root = symbol[0]
        idx = 1
        
        # Handle sharp/flat
        if idx < len(symbol) and symbol[idx] in '#b':
            root += symbol[idx]
            idx += 1
        
        # Parse quality
        quality_str = symbol[idx:] if idx < len(symbol) else ''
        # Default to MAJOR if no quality specified
        quality = ChordQuality.MAJOR if not quality_str else ChordQuality.from_string(quality_str)
        
        return cls(root=root, quality=quality)


class ChordProgressionItem(BaseModelWithConfig):
    """
    Represents an item in a chord progression.
    
    Attributes:
        chord: The chord
        duration: Duration in beats
        position: Position in beats from start
    """
    chord: Chord
    duration: float = Field(default=1.0, gt=0)
    position: float = Field(default=0.0, ge=0)

    def transpose(self, semitones: int) -> 'ChordProgressionItem':
        """
        Create a new ChordProgressionItem with transposed chord.
        
        Args:
            semitones: Number of semitones to transpose by
            
        Returns:
            ChordProgressionItem: New transposed item
        """
        return ChordProgressionItem(
            chord=self.chord.transpose(semitones),
            duration=self.duration,
            position=self.position
        )
