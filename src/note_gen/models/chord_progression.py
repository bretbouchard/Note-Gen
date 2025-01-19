# src/note_gen/models/chord_progression.py

from typing import List, Any, Dict, Optional, TypeVar
from pydantic import BaseModel, Field, ConfigDict, validator
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.scale import Scale, ScaleType
import logging
import uuid

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ChordProgression(BaseModel):
    """Class representing a progression of chords."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the chord progression")
    name: str = Field(description="Name of the chord progression")
    chords: List[Chord] = Field(description="List of chords in the progression", min_length=1)
    key: str = Field(description="Key of the chord progression")
    scale_type: str = Field(description="Type of scale (e.g., major, minor)")
    complexity: float = Field(default=1.0, description="Complexity rating between 0 and 1", ge=0, le=1)

    @validator('chords', each_item=True)
    def validate_and_convert_chord(cls, v):
        if isinstance(v, dict):
            root_data = v.get('root')
            root = None
            if isinstance(root_data, str):
                root = Note(note_name=root_data, octave=4, duration=1, velocity=100)
            elif isinstance(root_data, dict):
                root = Note(
                    note_name=root_data.get('note_name', 'C'),
                    octave=root_data.get('octave', 4),
                    duration=root_data.get('duration', 1),
                    velocity=root_data.get('velocity', 100)
                )
            quality = v.get('quality')
            if isinstance(quality, str):
                try:
                    quality = ChordQualityType(quality)
                except ValueError:
                    quality = ChordQualityType.MAJOR  # Default to major if invalid
            return Chord(root=root, quality=quality)
        elif isinstance(v, Chord):
            return v
        else:
            raise ValueError("Invalid chord type")

    @validator('key')
    def validate_key(cls, v):
        if not isinstance(v, str) or not v:
            raise ValueError("Key must be a non-empty string")
        return v

    @validator('scale_type')
    def validate_scale_type(cls, v):
        valid_types = ['major', 'minor']
        if v not in valid_types:
            raise ValueError(f'Invalid scale type: {v}. Must be one of {valid_types}')
        return v

    def add_chord(self, chord: Chord) -> None:
        """Add a chord to the progression."""
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:
        """Get all chords in the progression."""
        return self.chords

    def get_chord_names(self) -> List[str]:
        """Get the names of all chords in the progression."""
        return [f"{chord.root.note_name} {chord.quality.name.lower()}" for chord in self.chords]

    def transpose(self, interval: int) -> None:
        """Transpose the entire chord progression by a number of semitones."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert the chord progression to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "chords": [f"{chord.root.note_name} {chord.quality.name.lower()}" for chord in self.chords],
            "key": self.key,
            "scale_type": self.scale_type,
            "complexity": self.complexity,
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
            notes.append(Note(note_name=note_name, octave=base_octave, duration=1, velocity=100))
            
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

    def get_root_note_from_chord(self, chord: Chord) -> Optional[Note]:
        """Get the root note from a chord."""
        if chord is None or chord.root is None:
            return None
        return chord.root

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        d = super().model_dump(*args, **kwargs)
        d["chords"] = [f"{chord.root.note_name} {chord.quality.name.lower()}" for chord in self.chords]
        d["id"] = self.id
        d["name"] = self.name
        d["key"] = self.key
        d["scale_type"] = self.scale_type
        d["complexity"] = self.complexity
        return d

    def to_roman_numerals(self) -> List[RomanNumeral]:
        """Convert the chord progression to Roman numerals."""
        scale = Scale(root=Note(note_name=self.key, octave=4, duration=1, velocity=100), scale_type=ScaleType(self.scale_type))
        # This function needs to be updated to handle the new chord type
        pass

    def __str__(self) -> str:
        """Get string representation of the chord progression."""
        return f"{self.name}: {' '.join(str(chord) for chord in self.chords)}"

    def __repr__(self) -> str:
        return (f"ChordProgression(key: {self.key!r}, "
                f"scale_type: {self.scale_type!r}, "
                f"chords: List[Chord]={self.chords!r})")

    def some_function(self, param: T) -> T:
        return param

    def another_function(self, param: Any) -> None:
        pass

    def yet_another_function(self, param: Any) -> None:
        pass

    def final_function(self, param: Any) -> None:
        pass