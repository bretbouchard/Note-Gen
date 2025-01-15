# src/note_gen/models/chord_progression.py

from typing import List, Any, Dict, Optional, Union, Type, TypeVar, ClassVar
from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.scale import Scale, ScaleType
import logging
import uuid

logger = logging.getLogger(__name__)

class ChordProgression(BaseModel):
    """Class representing a progression of chords."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the chord progression")
    name: str = Field(description="Name of the chord progression")
    chords: List[str] = Field(description="List of chord symbols in the progression", min_length=1)
    key: str = Field(description="Key of the chord progression")
    scale_type: str = Field(description="Type of scale (e.g., major, minor)")
    complexity: float = Field(description="Complexity rating between 0 and 1", ge=0, le=1)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            'example': {
                'key': 'C',
                'scale_type': 'major',
                'chords': ['C', 'G', 'Am'],
                'complexity': 1.0
            }
        }
    )

    T: ClassVar = TypeVar('T')  # Add this line to annotate T as a ClassVar

    @field_validator('key')
    def validate_key(cls, v):
        valid_keys = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F']
        if v not in valid_keys:
            raise ValueError(f'Invalid key: {v}. Must be one of {valid_keys}')
        return v

    @field_validator('scale_type')
    def validate_scale_type(cls, v):
        valid_types = ['major', 'minor', 'harmonic_minor', 'melodic_minor', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'locrian']
        if v not in valid_types:
            raise ValueError(f'Invalid scale type: {v}. Must be one of {valid_types}')
        return v

    @field_validator('chords')
    def validate_chords(cls, v):
        valid_roots = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F']
        valid_qualities = ['', 'm', 'dim', 'aug', '7', 'm7', 'maj7', 'dim7', 'hdim7']
        
        for chord in v:
            # Split chord into root and quality
            if len(chord) > 1 and chord[1] in ['#', 'b']:
                root = chord[:2]
                quality = chord[2:] if len(chord) > 2 else ''
            else:
                root = chord[0]
                quality = chord[1:] if len(chord) > 1 else ''
                
            if root not in valid_roots:
                raise ValueError(f'Invalid chord root: {root}. Must be one of {valid_roots}')
            if quality not in valid_qualities:
                raise ValueError(f'Invalid chord quality: {quality}. Must be one of {valid_qualities}')
        return v

    def add_chord(self, chord: str) -> None:
        """Add a chord to the progression."""
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> str:
        return self.chords[index]

    def get_all_chords(self) -> List[str]:
        """Get all chords in the progression."""
        return self.chords

    def get_chord_names(self) -> List[str]:
        """Get the names of all chords in the progression."""
        return self.chords

    def transpose(self, interval: int) -> None:
        """Transpose the entire chord progression by a number of semitones."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert the chord progression to a dictionary representation."""
        return {
            "key": self.key,
            "scale_type": self.scale_type,
            "chords": self.chords
        }

    def generate_chord_notes(self, root: Note, quality: ChordQualityType, inversion: int = 0) -> List[Note]:
        """Generate notes for a chord based on root, quality, and inversion.
        
        Args:
            root: The root note of the chord
            quality: The quality of the chord
            inversion: The inversion of the chord (0 = root position, 1 = first inversion, etc.)
            
        Returns:
            List[Note]: The notes of the chord in the specified inversion
        """
        # Get the intervals for this chord quality
        intervals = ChordQualityType.get_intervals(quality)
        
        # Generate the notes in root position first
        notes = []
        base_octave = root.octave
        
        for interval in intervals:
            note_name = root.get_note_at_interval(interval)
            notes.append(Note(note_name=note_name, octave=base_octave))
            
        # Apply inversion by moving notes up an octave
        if inversion > 0:
            # Only apply inversion up to the number of notes minus 1
            effective_inversion = min(inversion, len(notes) - 1)
            
            # Move notes up an octave
            for i in range(effective_inversion):
                first_note = notes.pop(0)
                notes.append(Note(
                    note_name=first_note.note_name,
                    octave=first_note.octave + 1,
                    duration=first_note.duration,
                    velocity=first_note.velocity
                ))
                
        return notes

    def get_root_note_from_chord(self, chord: Optional[str]) -> Note:
        """Get the root note from a chord, validating against the scale.
        
        Args:
            chord: The chord to get the root note from
            
        Returns:
            Note: The root note of the chord
            
        Raises:
            ValueError: If the chord is None or the scale type is None
        """
        if chord is None:
            raise ValueError("The root note cannot be None.")
        
        if self.scale_type is None:
            raise ValueError("scale_type cannot be None")
            
        # This function needs to be updated to handle the new chord type
        pass

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        d = super().model_dump(*args, **kwargs)
        d["chords"] = self.chords
        return d

    def to_roman_numerals(self) -> List[RomanNumeral]:
        """Convert the chord progression to Roman numerals."""
        scale = Scale(root=Note(note_name=self.key), scale_type=ScaleType(self.scale_type))
        # This function needs to be updated to handle the new chord type
        pass

    def __str__(self) -> str:
        """Get string representation of the chord progression."""
        return f"{self.name}: {' '.join(str(chord) for chord in self.chords)}"

    def __repr__(self) -> str:
        return (f"ChordProgression(key: {self.key!r}, "
                f"scale_type: {self.scale_type!r}, "
                f"chords: List[str]={self.chords!r})")

    def some_function(self, param: T) -> T:
        return param

    def another_function(self, param: Any) -> None:
        pass

    def yet_another_function(self, param: Any) -> None:
        pass

    def final_function(self, param: Any) -> None:
        pass