# src/note_gen/models/chord_progression.py

from typing import List, Any, Dict, Optional, Union
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

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    scale_info: ScaleInfo
    chords: List[Chord] = Field(default_factory=list)
    root: Optional[Note] = None
    key: str
    scale_type: str = "major"
    description: str = ""
    tags: List[str] = []
    complexity: float = 1.0
    is_test: bool = Field(default=False)

    class Config:
        arbitrary_types_allowed = True
        schema_extra = {
            'example': {
                'scale_info': {'key': 'C', 'mode': 'major'},
                'chords': [{'name': 'I', 'quality': 'major'}, {'name': 'IV', 'quality': 'major'}, {'name': 'V', 'quality': 'major'}],
                'root': {'note_name': 'C', 'octave': 4},
                'key': 'C',
                'scale_type': 'major',
                'description': '',
                'tags': [],
                'complexity': 1.0
            }
        }

    @field_validator("scale_info", mode="before")
    def validate_scale_info(cls, v: Any) -> ScaleInfo:
        if isinstance(v, ScaleInfo):
            return v
        if isinstance(v, dict):
            return ScaleInfo(**v)
        raise ValueError(f"Invalid scale_info type: {type(v)}")

    @field_validator("chords", mode="before")
    def validate_chords(cls, v: list[Any]) -> list[Chord]:
        if v is None:
            return []
        for item in v:
            if not isinstance(item, Chord):
                raise ValueError("All items in chords must be instances of Chord.")
        return v

    @field_validator("chords")
    @classmethod
    def validate_chords_length(cls, v: List[Chord]) -> List[Chord]:
        """Validate that the chords list is not empty and contains only Chord instances."""
        if not v:
            raise ValueError("Chord progression must contain at least one chord")
        return v

    @field_validator("key")
    def validate_key(cls, v):
        valid_keys = ["C", "G", "D", "A", "E", "B", "F#", "Gb", "Db", "Ab", "Eb", "Bb", "F"]
        if v not in valid_keys:
            raise ValueError(f"Invalid key. Must be one of: {', '.join(valid_keys)}")
        return v

    @field_validator("scale_type")
    def validate_scale_type(cls, v):
        valid_types = ["major", "minor", "harmonic_minor", "melodic_minor", "dorian", "phrygian", "lydian", "mixolydian", "locrian"]
        if v not in valid_types:
            raise ValueError(f"Invalid scale type. Must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("complexity")
    def validate_complexity(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Complexity must be between 0 and 1")
        return v

    @field_validator("tags")
    def validate_tags(cls, v):
        valid_tags = ["basic", "jazz", "rock", "pop", "classical", "blues", "folk"]
        for tag in v:
            if tag not in valid_tags:
                raise ValueError(f"Invalid tag: {tag}. Must be one of: {', '.join(valid_tags)}")
        return v

    def add_chord(self, chord: Chord) -> None:
        """Add a chord to the progression."""
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:
        return self.chords

    def get_chord_names(self) -> List[str]:
        """Get the names of all chords in the progression."""
        # Mapping of chord qualities to Roman numerals
        roman_numerals = {
            'major': 'I',
            'minor': 'ii',
            'diminished': 'vii',
            'dominant': 'V',
            'major_7': 'I7',
            'minor_7': 'ii7',
            # Add other mappings as necessary
        }
        return [roman_numerals[chord.quality.value] for chord in self.chords]

    def transpose(self, interval: int) -> None:
        """Transpose the entire chord progression by a number of semitones."""
        for chord in self.chords:
            # Update root note name based on transposition
            root_note = Note(**chord.root.dict())
            root_note.transpose(interval)
            chord.root = root_note

    def to_dict(self) -> Dict[str, Any]:
        """Convert the chord progression to a dictionary representation."""
        return {
            "scale_info": self.scale_info.dict(),
            "chords": [chord.dict() for chord in self.chords]
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

    def get_root_note_from_chord(self, chord: Optional[Chord]) -> Note:
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
        
        if self.scale_info.scale_type is None:
            raise ValueError("scale_type cannot be None")
            
        return chord.root

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        d = super().model_dump(*args, **kwargs)
        d["chords"] = [chord.model_dump() for chord in self.chords]
        d["scale_info"] = self.scale_info.model_dump()
        return d

    def __repr__(self) -> str:
        return (f"ChordProgression(scale_info: {self.scale_info.__class__.__name__}={self.scale_info!r}, "
                f"chords: List[{self.chords[0].__class__.__name__ if self.chords else 'Chord'}]={self.chords!r})")