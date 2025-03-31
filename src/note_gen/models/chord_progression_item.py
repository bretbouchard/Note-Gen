"""Model for chord progression items and their properties."""

from typing import Optional
from pydantic import Field, model_validator
from src.note_gen.models.base import BaseModelWithConfig
from src.note_gen.core.enums import ChordQuality
from src.note_gen.models.chord import Chord

class ChordProgressionItem(BaseModelWithConfig):
    """
    Represents a chord within a progression with additional properties.
    
    Attributes:
        chord_symbol: The chord symbol (e.g., 'C', 'Am', 'F7')
        duration: Duration of the chord in beats
        position: Position of the chord in beats from start
        chord: The actual Chord object
    """
    chord_symbol: str
    duration: float = Field(default=1.0, gt=0)
    position: float = Field(default=0.0, ge=0)
    chord: Optional[Chord] = None

    @model_validator(mode='after')
    def create_chord(self) -> 'ChordProgressionItem':
        """Create the Chord object from the chord symbol."""
        if self.chord is None:
            self.chord = Chord.from_symbol(self.chord_symbol)
        return self

    @classmethod
    def create(cls, chord_symbol: str, duration: float = 1.0, position: float = 0.0) -> 'ChordProgressionItem':
        """
        Create a new ChordProgressionItem.
        
        Args:
            chord_symbol: The chord symbol (e.g., 'C', 'Am', 'F7')
            duration: Duration of the chord in beats
            position: Position of the chord in beats from start
            
        Returns:
            ChordProgressionItem: A new chord progression item
        """
        return cls(
            chord_symbol=chord_symbol,
            duration=duration,
            position=position
        )

    def from_chord(cls, chord: Chord, duration: float = 1.0, position: float = 0.0) -> 'ChordProgressionItem':
        """
        Create a new ChordProgressionItem from a Chord object.
        
        Args:
            chord: The Chord object
            duration: Duration of the chord in beats
            position: Position of the chord in beats from start
            
        Returns:
            ChordProgressionItem: A new chord progression item
        """
        return cls(
            chord_symbol=chord.to_symbol(),
            duration=duration,
            position=position,
            chord=chord
        )

    def transpose(self, semitones: int) -> 'ChordProgressionItem':
        """
        Create a new ChordProgressionItem transposed by the specified number of semitones.
        
        Args:
            semitones: Number of semitones to transpose by
            
        Returns:
            ChordProgressionItem: New transposed chord progression item
        """
        # Create a Chord object to handle the transposition
        chord = Chord.from_symbol(self.chord_symbol)
        transposed_chord = chord.transpose(semitones)
        
        return ChordProgressionItem(
            chord_symbol=transposed_chord.to_symbol(),
            duration=self.duration,
            position=self.position
        )
