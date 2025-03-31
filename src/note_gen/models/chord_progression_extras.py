"""Extra models and utilities for chord progression handling."""

from typing import List, Optional, Union, Dict, Any, Set, Sequence
from pydantic import Field, field_validator, ValidationInfo, ConfigDict
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.core.constants import RANGE_LIMITS, VALID_KEYS
from src.note_gen.models.base import BaseModelWithConfig
from src.note_gen.core.enums import ChordQuality, ScaleType
from fastapi.encoders import jsonable_encoder
from dataclasses import dataclass
from src.note_gen.models.chord_progression_item import ChordProgressionItem

# Constants
valid_qualities: Set[ChordQuality] = set(ChordQuality.__members__.values())

@dataclass(frozen=True)
class MidiRange:
    """MIDI note range limits."""
    min_midi: int = 0
    max_midi: int = 127

MIDI_LIMITS = MidiRange()

class ChordProgressionResponse(BaseModelWithConfig):
    """Response model for chord progressions."""
    id: Optional[str] = None  # Add this for MongoDB _id
    name: str = Field(..., min_length=1, max_length=100)
    chords: List[ChordProgressionItem] = Field(default_factory=list)
    scale_info: Union[ScaleInfo, FakeScaleInfo] = Field(...)
    key: str = Field(..., pattern=r'^[A-G][#b]?$')
    scale_type: ScaleType
    complexity: Optional[float] = Field(None, ge=0.0, le=1.0)
    duration: Optional[float] = Field(None, gt=0.0)

    @classmethod
    def from_db_model(cls, db_model: Dict[str, Any]) -> 'ChordProgressionResponse':
        """Create response model from database model."""
        # Convert _id to string if it exists
        if '_id' in db_model:
            db_model['id'] = str(db_model.pop('_id'))
        return cls(**db_model)

    def to_json(self) -> Dict[str, Any]:
        """Convert the response to JSON-compatible format."""
        return jsonable_encoder(self)

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate key against valid keys."""
        if v not in VALID_KEYS:
            raise ValueError(f"Invalid key: {v}. Must be one of {VALID_KEYS}")
        return v

class ChordProgressionCreate(BaseModelWithConfig):
    """Request model for creating chord progressions."""
    name: str = Field(..., min_length=1, max_length=100)
    chords: List[Chord] = Field(...)
    key: str = Field(
        ..., 
        description="Key of the progression",
        pattern=r'^[A-G][#b]?$'
    )
    scale_type: ScaleType
    complexity: Optional[float] = Field(None, ge=0.0, le=1.0)
    scale_info: Optional[Union[Dict[str, Any], ScaleInfo]] = None
    duration: float = Field(default=1.0, gt=0.0)

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate key against valid keys."""
        if v not in VALID_KEYS:
            raise ValueError(f"Invalid key: {v}. Must be one of {VALID_KEYS}")
        return v

    @field_validator('chords')
    @classmethod
    def validate_chord_qualities(cls, v: List[Chord], info: ValidationInfo) -> List[Chord]:
        """Validate chord qualities."""
        for chord in v:
            if chord.quality not in valid_qualities:
                raise ValueError(f"Invalid chord quality: {chord.quality}")
            
            # Validate chord range
            min_midi = MIDI_LIMITS.min_midi
            max_midi = MIDI_LIMITS.max_midi
            
            # Get notes from the chord
            for note in chord.notes:  # note is already a Note object
                midi_number = note.to_midi_number()
                if midi_number is not None:  # Handle Optional[int]
                    if not (min_midi <= midi_number <= max_midi):
                        raise ValueError(
                            f"Note {note} in chord {chord} is outside valid MIDI range "
                            f"({min_midi}-{max_midi})"
                        )
        return v

    def to_progression(self) -> ChordProgression:
        """Convert create request to ChordProgression instance."""
        scale_info_data = (
            self.scale_info if isinstance(self.scale_info, dict)
            else self.scale_info.model_dump() if isinstance(self.scale_info, ScaleInfo)
            else {"key": self.key, "scale_type": self.scale_type}
        )
        
        progression_items = [
            ChordProgressionItem(
                chord_symbol=chord.to_symbol(),  # Convert Chord to symbol string
                duration=getattr(chord, 'duration', 1.0)
            ) for i, chord in enumerate(self.chords)
        ]
        
        return ChordProgression(
            **{
                "name": self.name,
                "chords": progression_items,
                "key": self.key,
                "scale_type": self.scale_type,
                "complexity": self.complexity,
                "duration": self.duration,
                "scale_info": ScaleInfo(**scale_info_data)
            }
        )

class ChordProgressionPartialUpdate(BaseModelWithConfig):
    """Model for updating existing chord progressions."""
    model_config = ConfigDict(validate_assignment=True)

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    chords: Optional[List[ChordProgressionItem]] = None
    key: Optional[str] = Field(
        None, 
        description="Key of the progression",
        pattern=r'^[A-G][#b]?$'
    )
    scale_type: Optional[ScaleType] = None
    
    def apply_update(self, progression: ChordProgression) -> ChordProgression:
        """Apply update to existing progression."""
        update_data = self.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(progression, field, value)
        return progression

    def _calculate_voice_leading_score(self, current_note: Note, next_note: Note) -> float:
        """Calculate voice leading score between two notes."""
        # Get MIDI numbers using the method instead of accessing attribute
        current_midi = current_note.to_midi_number()
        if current_midi is None:
            return 0.0
        
        next_midi = next_note.to_midi_number()
        if next_midi is None:
            return 0.0
        
        interval = abs(next_midi - current_midi)
        
        # Score based on interval size (smaller intervals preferred)
        if interval == 0:
            return 1.0  # Perfect - same note
        elif interval <= 2:
            return 0.9  # Very good - step-wise motion
        elif interval <= 4:
            return 0.7  # Good - small leap
        elif interval <= 7:
            return 0.5  # Acceptable - medium leap
        else:
            return 0.3  # Less desirable - large leap

