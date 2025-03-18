from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
import re
from .note import Note
from .chord_quality import ChordQuality
from .scale_info import ScaleInfo

class Chord(BaseModel):
    """Represents a musical chord."""
    root: Note
    quality: ChordQuality
    inversion: int = Field(default=0, ge=0, le=3)
    notes: List[Note] = Field(default_factory=list)
    
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True
    )
    
    @field_validator('quality', mode='before')
    @classmethod
    def validate_quality(cls, v):
        """Validate the chord quality."""
        if isinstance(v, str):
            if not v:  # Handle empty string
                return ChordQuality.MAJOR
            try:
                return ChordQuality[v.upper()]
            except KeyError:
                raise ValueError(f"Invalid chord quality: {v}")
        return v
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.notes:
            self._generate_notes()

    @staticmethod
    def _enharmonic_note_name(note_name: str) -> str:
        """Convert sharp notes to their flat equivalents."""
        enharmonic_map = {
            'C#': 'Db',
            'D#': 'Eb',
            'F#': 'Gb',
            'G#': 'Ab',
            'A#': 'Bb',
        }
        # Remove any octave number if present
        base_note = note_name.split('/')[0]
        # Check if the note is in our map
        if base_note in enharmonic_map:
            return enharmonic_map[base_note]
        return base_note
    
    def _generate_notes(self):
        """Generate the notes for this chord based on root, quality and inversion."""
        intervals = self.quality.get_intervals()
        base_notes = [self.root.transpose(interval) for interval in intervals]
        
        # Apply inversion
        if self.inversion > 0:
            self.notes = base_notes[self.inversion:] + [note.transpose(12) for note in base_notes[:self.inversion]]
        else:
            self.notes = base_notes

    def transpose(self, semitones: int) -> 'Chord':
        """Transpose the chord by the specified number of semitones."""
        new_root = self.root.transpose(semitones)
        return Chord(root=new_root, quality=self.quality, inversion=self.inversion)

class ChordProgression(BaseModel):
    id: Optional[str] = Field(default=None)
    name: str = Field(..., min_length=2)
    key: str = Field(..., pattern=r"^[A-G][#b]?$")
    scale_type: str = Field(...)
    scale_info: Union[str, ScaleInfo] = Field(...)
    chords: List[Chord] = Field(..., min_length=1, max_length=32)  # Changed from max_items to max_length
    complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    genre: Optional[str] = Field(default=None)

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate and normalize the key."""
        v = v.upper()  # Convert to uppercase first
        if not re.match(r'^[A-G][#b]?$', v):
            raise ValueError("Key must be a valid note name (A-G) with optional sharp (#) or flat (b)")
        return v

    def generate_progression_from_pattern(
        self,
        pattern: List[str],
        scale_info: ScaleInfo,
        progression_length: int
    ) -> 'ChordProgression':
        """Generate chord progression from a pattern string.
        
        Args:
            pattern: List of Roman numerals representing the chord progression
            scale_info: Scale information for the progression
            progression_length: Desired length of the progression
        
        Returns:
            A new ChordProgression instance with the generated chords
        """
        if not pattern:
            raise ValueError("Pattern cannot be empty")
        
        scale = Scale.from_scale_info(scale_info)
        new_chords = []
        
        for numeral in pattern[:progression_length]:
            roman = RomanNumeral.from_roman_numeral(numeral)
            scale_degree = roman.to_scale_degree()
            root_note = scale.get_note_from_degree(scale_degree)
            new_chord = Chord(root=root_note, quality=roman.quality, inversion=roman.inversion)
            new_chords.append(new_chord)
        
        return ChordProgression(
            name=self.name,
            key=self.key,
            scale_type=self.scale_type,
            scale_info=scale_info,
            chords=new_chords,
            complexity=self.complexity,
            genre=self.genre
        )

class MockDatabase:
    data: List[Any] = []

    def __init__(self) -> None:
        self.data = []

    async def insert(self, pattern: Any) -> None:
        self.data.append(pattern)
