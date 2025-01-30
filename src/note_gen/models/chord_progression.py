from typing import List, Any, Dict, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator, validator, root_validator
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
    chords: List[Chord] = Field(..., description="List of chords")
    key: str = Field(description="Key of the chord progression")
    scale_type: str = Field(description="Type of scale (e.g., MAJOR, MINOR)")
    complexity: float = Field(default=0.0, description="Complexity of the chord progression")
    scale_info: ScaleInfo = Field(description="Scale information")
    quality: ChordQualityType = Field(description="Quality of the chord progression")

    def __init__(self, **data: Dict[str, Any]) -> None:
        logger.debug(f"Creating ChordProgression with data: {data}")
        logger.debug(f"Data keys: {data.keys()}")
        logger.debug(f"Data values: {data.values()}")
        try:
            super().__init__(**data)
        except Exception as e:
            logger.error(f"Error during ChordProgression initialization: {e}")
            raise

    @root_validator(pre=True)
    def check_quality(cls, values):
        chords = values.get('chords', [])
        if not chords:
            raise ValueError("Chords must be a non-empty list.")
        # Set quality from the first chord if not provided
        if 'quality' not in values:
            values['quality'] = chords[0].quality
        return values

    @field_validator('scale_info')
    def validate_scale_info(cls, value):
        # Add any validation logic needed for scale_info
        return value

    @field_validator('chords')
    def validate_chords(cls, value):
        logger.debug(f"Validating chords: {value}")
        if not value:
            raise ValueError("Chords must be a non-empty list.")
        for chord in value:
            logger.debug(f"Validating chord: {chord}")
            if not isinstance(chord, Chord):
                raise ValueError("Each chord must be an instance of Chord.")
            if not isinstance(chord.root, Note):
                raise ValueError("Chord root must be a valid Note instance.")
            if not isinstance(chord.root.note_name, str) or not chord.root.note_name:
                raise ValueError("Note name must be a valid non-empty string.")
        return value

    @field_validator('name')
    def validate_name(cls, value):
        logger.debug(f"Validating progression name: {value}")
        if not isinstance(value, str) or not value:
            raise ValueError("Name must be a non-empty string")
        return value

    @field_validator('key')
    def validate_key(cls, v: str) -> str:
        logger.debug(f"Validating progression key: {v}")
        if not isinstance(v, str) or not v:
            raise ValueError("Key must be a non-empty string")
        return v

    @field_validator('scale_type')
    def validate_scale_type(cls, v: str) -> str:
        logger.debug(f"Validating progression scale type: {v}")
        valid_types = ['MAJOR', 'MINOR']
        if v not in valid_types:
            logger.error(f'Invalid scale type: {v}. Must be one of {valid_types}')
            raise ValueError(f'Invalid scale type: {v}. Must be one of {valid_types}')
        return v

    @field_validator('complexity')
    def validate_complexity(cls, v: Optional[float]) -> Optional[float]:
        logger.debug(f"Validating progression complexity: {v}")
        if v is not None and (v < 0 or v > 1):
            logger.error("Complexity must be between 0 and 1")
            raise ValueError("Complexity must be between 0 and 1")
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
        return [chord.root.note_name for chord in self.chords]

    def transpose(self, interval: int) -> None:
        """Transpose the entire chord progression by a number of semitones."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the chord progression."""
        return {
            'id': self.id,
            'name': self.name,
            'chords': [chord.to_dict() for chord in self.chords], 
            'key': self.key,
            'scale_type': self.scale_type,
            'complexity': self.complexity,
        }

    def dict(self, *args, **kwargs):
        original_dict = super().dict(*args, **kwargs)
        # Convert ChordQualityType instances to strings
        if 'chords' in original_dict:
            for chord in original_dict['chords']:
                if isinstance(chord['quality'], ChordQualityType):
                    chord['quality'] = chord['quality'].value
        return original_dict

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
        if not isinstance(quality, ChordQualityType):
            raise ValueError("Quality must be an instance of ChordQualityType")
        intervals = ChordQualityType(quality).get_intervals()
        
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
                f"chords: List[Chord]={self.chords!r})")

    def json(self, *args, **kwargs):
        original_dict = self.dict(*args, **kwargs)
        # Convert ChordQualityType instances to strings
        if 'chords' in original_dict:
            for chord in original_dict['chords']:
                if isinstance(chord['quality'], ChordQualityType):
                    chord['quality'] = chord['quality'].value
        return original_dict