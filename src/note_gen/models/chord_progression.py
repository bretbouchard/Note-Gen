from typing import List, Any, Dict, Optional, Union, ClassVar
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator, validator
from src.note_gen.models.note import Note
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.enums import ChordQualityType, ScaleType
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.scale import Scale
from src.note_gen.models.fake_scale_info import FakeScaleInfo
import logging
import uuid
from bson import ObjectId

logger = logging.getLogger(__name__)

class ChordProgression(BaseModel):
    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        arbitrary_types_allowed=True
    )

    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)  

    id: Optional[str] = None
    name: str
    chords: List[Chord]
    key: str
    scale_type: ScaleType
    scale_info: Union[ScaleInfo, FakeScaleInfo] = Field(...)
    quality: Optional[ChordQualityType] = ChordQualityType.MAJOR
    complexity: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.chords:
            raise ValueError("Chords cannot be empty.")
        if self.complexity is not None and (self.complexity < 0 or self.complexity > 1):
            raise ValueError("Complexity must be between 0 and 1.")

    @field_validator('complexity')
    def validate_complexity(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Complexity must be between 0 and 1.")
        return v

    @field_validator('chords')
    def validate_chords(cls, v):
        if not v:
            raise ValueError("Chords cannot be empty.")
        for chord in v:
            if not isinstance(chord, Chord):
                raise ValueError("All items in chords must be instances of Chord.")
            if not isinstance(chord.quality, ChordQualityType):
                raise ValueError(f"Invalid chord quality: {chord.quality}")
        return v

    @field_validator('key')
    def validate_key(cls, value):
        if not value:
            raise ValueError('Key cannot be empty.')
        return value

    @field_validator('scale_type')
    def validate_scale_type(cls, value):
        if value not in ScaleType:
            raise ValueError('Invalid scale type. Must be either MAJOR or MINOR.')
        return value

    @field_validator('quality')
    def validate_quality(cls, v):
        if not isinstance(v, ChordQualityType):
            raise ValueError('Quality must be an instance of ChordQualityType.')
        return v

    @field_validator('scale_info')
    def validate_scale_info(cls, scale_info):
        if not isinstance(scale_info, (ScaleInfo, FakeScaleInfo)):
            raise ValueError('Scale info must be an instance of ScaleInfo or FakeScaleInfo.')
        return scale_info

    @field_validator('chords')
    def validate_chords_quality(cls, chords):
        for chord in chords:
            logger.debug(f"Validating chord quality: {chord.quality}")
            if not isinstance(chord.quality, ChordQualityType):
                raise ValueError(f"Invalid chord quality: {chord.quality}")
        return chords

    @model_validator(mode='before')
    def check_required_fields(cls, values):
        if not values.get('name'):
            raise ValueError('Name is required')
        if not values.get('key'):
            raise ValueError('Key is required')
        if not values.get('scale_type'):
            raise ValueError('Scale type is required')
        return values

    def add_chord(self, chord: Chord) -> None:
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:
        return self.chords

    def get_chord_names(self) -> List[str]:
        return [chord.root.note_name for chord in self.chords]

    def transpose(self, interval: int) -> None:
        pass

    def to_dict(self, *args, **kwargs):
        original_dict = super().dict(*args, **kwargs)
        if 'chords' in original_dict:
            for idx, chord in enumerate(original_dict['chords']):
                if isinstance(chord, Chord):
                    original_dict['chords'][idx] = {
                        'root': chord.root,
                        'quality': chord.quality.name,
                        'notes': chord.notes,
                        'inversion': chord.inversion
                    }
        return original_dict

    def dict(self, *args, **kwargs):
        original_dict = super().dict(*args, **kwargs)
        if 'chords' in original_dict:
            for idx, chord in enumerate(original_dict['chords']):
                if isinstance(chord, Chord):
                    original_dict['chords'][idx] = {
                        'root': chord.root,
                        'quality': chord.quality.name,
                        'notes': chord.notes,
                        'inversion': chord.inversion
                    }
        return original_dict

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        d = {"id": self.id, "name": self.name, "key": self.key, "scale_type": self.scale_type, "complexity": self.complexity}
        d["chords"] = [f"{chord.root.note_name} {chord.quality}" for chord in self.chords]
        return d

    def generate_chord_notes(self, root: Note, quality: ChordQualityType, inversion: int = 0) -> List[Note]:
        intervals = ChordQualityType.get_intervals(quality)  
        notes = []
        base_octave = root.octave
        
        for interval in intervals:
            note_name = root.get_note_at_interval(interval)
            notes.append(Note(note_name=note_name, octave=base_octave, duration=1, velocity=100))
            
        if inversion > 0:
            effective_inversion = min(inversion, len(notes) - 1)
            
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
        if chord is None or chord.root is None:
            return None
        return Note(note_name=chord.root.note_name, octave=chord.root.octave, duration=1, velocity=100)

    def to_roman_numerals(self) -> List[RomanNumeral]:
        scale = Scale(root=Note(note_name=self.key, octave=4, duration=1, velocity=100), scale_type=ScaleType(self.scale_type))
        pass

    def __str__(self) -> str:
        return f"{self.name}: {' '.join(str(chord) for chord in self.chords)}"

    def __repr__(self) -> str:
        return (f"ChordProgression(key: {self.key!r}, "
                f"scale_type: {self.scale_type!r}, "
                f"chords: List[Chord]={self.chords!r})")

    def json(self, *args, **kwargs):
        original_dict = self.dict(*args, **kwargs)
        if 'chords' in original_dict:
            for chord in original_dict['chords']:
                if isinstance(chord['quality'], ChordQualityType):
                    chord['quality'] = chord['quality'].value
        return original_dict