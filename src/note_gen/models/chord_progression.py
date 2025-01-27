from typing import List, Any, Dict, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator, validator
from src.note_gen.models.note import Note
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.scale import Scale, ScaleType
import logging
import uuid
from bson import ObjectId

logger = logging.getLogger(__name__)

class ChordProgression(BaseModel):
    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        arbitrary_types_allowed=True
    )

    id: Optional[str] = None
    name: str = Field(description="Name of the chord progression")
    chords: List[Union[Chord, Dict[str, Any]]] = Field(description="List of chords", min_length=1)
    key: str = Field(description="Key of the chord progression")
    scale_type: str = Field(description="Type of scale (e.g., major, minor)")
    complexity: float = Field(default=0.0, description="Complexity of the chord progression")
    scale_info: ScaleInfo = Field(description="Scale information")

    @field_validator('scale_info')
    def validate_scale_info(cls, value):
        # Add any validation logic needed for scale_info
        return value

    @field_validator('chords')
    def validate_chords(cls, chords: List[Union[Chord, Dict[str, Any]]]) -> List[Chord]:
        processed_chords = [
            Chord(**chord) if isinstance(chord, dict) else chord
            for chord in chords
        ]
        return processed_chords

    @field_validator('key')
    def validate_key(cls, v: str) -> str:
        if not isinstance(v, str) or not v:
            raise ValueError("Key must be a non-empty string")
        return v

    @field_validator('scale_type')
    def validate_scale_type(cls, v: str) -> str:
        valid_types = ['major', 'minor']
        if v not in valid_types:
            raise ValueError(f'Invalid scale type: {v}. Must be one of {valid_types}')
        return v

    @field_validator('complexity')
    def validate_complexity(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Complexity must be between 0 and 1")
        return v

    def add_chord(self, chord: Dict) -> None:
        """Add a chord to the progression."""
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Dict:
        return self.chords[index]

    def get_all_chords(self) -> List[Dict]:
        """Get all chords in the progression."""
        return self.chords

    def get_chord_names(self) -> List[str]:
        """Get the names of all chords in the progression."""
        return [f"{chord.root.note_name} {chord.quality}" for chord in self.chords]

    def transpose(self, interval: int) -> None:
        """Transpose the entire chord progression by a number of semitones."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert the chord progression to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "chords": [f"{chord.root.note_name} {chord.quality}" for chord in self.chords],
            "key": self.key,
            "scale_type": self.scale_type,
            "complexity": self.complexity
        }

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        d = {"id": self.id, "name": self.name, "key": self.key, "scale_type": self.scale_type, "complexity": self.complexity}
        d["chords"] = [f"{chord.root.note_name} {chord.quality}" for chord in self.chords]
        return d

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
        return Note(note_name=chord.root.note_name, octave=chord.root.octave, duration=1, velocity=100)

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
                f"chords: List[Dict]={self.chords!r})")

    def json(self, *args: Any, **kwargs: Any) -> str:
        # Override json method to serialize ObjectId to string
        data = super().json(*args, **kwargs)
        return data.replace('ObjectId(', '"').replace(')', '"')