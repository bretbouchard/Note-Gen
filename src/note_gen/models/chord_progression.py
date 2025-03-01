from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.chord_quality import ChordQualityType
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from pydantic import BaseModel, Field, ConfigDict, field_validator, validator, ValidationError
from typing import List, Optional, Union, Dict, Any, Callable, Set, ForwardRef
import logging
import uuid
from bson import ObjectId
import json
from fastapi.encoders import jsonable_encoder
import warnings

logger = logging.getLogger(__name__)

class ChordProgression(BaseModel):
    """A progression of chords."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    chords: List[Chord]
    key: str = Field(default="C")
    scale_type: str = Field(default="MAJOR")
    complexity: Optional[float] = Field(default=0.5)
    scale_info: Union[ScaleInfo, FakeScaleInfo]
    duration: float = Field(default=1.0, description="Duration of each chord in bars")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ChordQualityType: lambda v: v.value if isinstance(v, ChordQualityType) else str(v),
            Note: lambda v: jsonable_encoder(v),
            ScaleInfo: lambda v: jsonable_encoder(v),
            FakeScaleInfo: lambda v: jsonable_encoder(v),
            ObjectId: lambda v: str(v)
        }
        from_attributes = True

    @property
    def progression(self) -> List[str]:
        """Get the chord progression as a list of strings."""
        logger.debug('Getting chord progression: %s', self.chords)
        return [str(chord) for chord in self.chords]

    @property
    def progression_quality(self) -> List[str]:
        """Get the chord progression quality as a list of strings."""
        logger.debug('Getting chord progression quality: %s', self.chords)
        return [chord.quality.value for chord in self.chords]

    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        """
        Enhanced name validation:
        - Minimum 4 characters
        - Allows alphanumeric, spaces, hyphens, and underscores
        - Trims whitespace
        """
        if not v or len(v.strip()) < 4:
            raise ValueError('Name must be at least 4 characters long and not just whitespace')
        
        # Remove leading/trailing whitespace
        cleaned_name = v.strip()
        
        # Optional: Add regex validation for allowed characters
        import re
        if not re.match(r'^[a-zA-Z0-9\s_-]+$', cleaned_name):
            raise ValueError('Name can only contain letters, numbers, spaces, underscores, and hyphens')
        
        return cleaned_name

    @field_validator('chords')
    def validate_chords(cls, v: List[Chord]) -> List[Chord]:
        """
        Enhanced chord validation:
        - Non-empty list
        - Each chord is a valid Chord instance
        - Validate chord qualities
        - Minimum and maximum chord progression length
        """
        if not v:
            raise ValueError("Value error, Chords list cannot be empty")
        
        if len(v) > 16:
            raise ValueError("Chord progression cannot have more than 16 chords")
        
        # Validate chord qualities
        valid_qualities = set(ChordQualityType)

        for chord in v:
            if chord.quality not in valid_qualities:
                raise ValueError(f"Invalid chord quality: {chord.quality}. Must be one of {valid_qualities}")
    
        
        # Warn about complexity if fewer than 2 chords
        if len(v) < 2:
            warnings.warn("Chord progression with fewer than 2 chords might lack musical complexity", UserWarning)
        
        return v

    @field_validator('key')
    def validate_key(cls, v: str) -> str:
        """
        Enhanced key validation:
        - Case-insensitive matching
        - Normalize to standard notation
        - More comprehensive key validation
        """
        valid_keys = {
            'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 
            'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'
        }
        
        # Normalize key
        normalized_key = v.capitalize()
        
        if normalized_key not in valid_keys:
            raise ValueError(f"Invalid key '{v}'. Must be one of {', '.join(valid_keys)}")
        
        return normalized_key

    @field_validator('scale_type')
    def validate_scale_type(cls, v: str) -> str:
        """
        Enhanced scale type validation:
        - Case-insensitive
        - Normalize to uppercase
        - Provide clear error message
        - Support more scale types
        """
        valid_types = {
            "MAJOR", 
            "MINOR", 
            "HARMONIC_MINOR", 
            "MELODIC_MINOR",
            "DORIAN",
            "PHRYGIAN",
            "LYDIAN",
            "MIXOLYDIAN",
            "LOCRIAN"
        }
        
        normalized_type = v.upper()
        
        if normalized_type not in valid_types:
            raise ValueError(
                f"Invalid scale type '{v}'. Must be one of: " + 
                ", ".join(valid_types)
            )
        
        return normalized_type

    @field_validator('complexity')
    @classmethod
    def validate_complexity(cls, v: float) -> float:
        """
        Validate the complexity of the chord progression.
        Ensures complexity is between 0 and 1.
        
        Args:
            v (float): Complexity value to validate
        
        Returns:
            float: Validated complexity value
        
        Raises:
            ValidationError: If complexity is outside valid range
        """
        if not (0 <= v <= 1):
            raise ValueError(f"Complexity must be between 0 and 1. Got {v}")
        return v

    @field_validator('scale_info')
    def validate_scale_info(cls, value: Union[ScaleInfo, FakeScaleInfo]) -> Union[ScaleInfo, FakeScaleInfo]:
        """
        Enhanced scale info validation:
        - Allow both ScaleInfo and FakeScaleInfo
        - Check for required attributes
        - Validate scale info consistency
        """
        if not hasattr(value, 'scale_type') or not hasattr(value, 'root'):
            raise ValueError("Scale info must have 'scale_type' and 'root' attributes")
        
        # Optional: Cross-validate scale info with progression
        try:
            if value.scale_type not in {"MAJOR", "MINOR"}:
                raise ValueError(f"Invalid scale type in scale info: {value.scale_type}")
        except Exception as e:
            logger.error(f"Scale info validation error: {e}")
            raise
        
        return value

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Custom serialization method."""
        exclude_none = kwargs.pop('exclude_none', True)
        by_alias = kwargs.pop('by_alias', True)
        
        # Get the base dictionary
        data = super().model_dump(exclude_none=exclude_none, by_alias=by_alias, **kwargs)
        
        # Ensure proper serialization of nested objects
        if 'chords' in data:
            data['chords'] = [jsonable_encoder(chord) for chord in self.chords]
        if 'scale_info' in data:
            data['scale_info'] = jsonable_encoder(self.scale_info)
            
        return data

    def json(self, *args: Any, **kwargs: Any) -> str:
        """Convert model to JSON string."""
        return json.dumps(jsonable_encoder(self))

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert the model to a dictionary, preserving raw objects for testing."""
        logger.debug('Converting model to dictionary')
        return self.model_dump(*args, mode='python', **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert ChordProgression to a dictionary for database storage."""
        try:
            serialized = {
                'id': self.id,
                'name': self.name,
                'chords': [
                    {
                        'root': chord.root.to_dict() if chord.root else None,
                        'quality': chord.quality.name if chord.quality else None,
                        'notes': [note.to_dict() for note in chord.notes] if chord.notes else [],
                        'inversion': chord.inversion
                    }
                    for chord in self.chords
                ],
                'key': self.key,
                'scale_type': self.scale_type,
                'complexity': self.complexity,
                'scale_info': self.scale_info.model_dump() if self.scale_info else None,
                'duration': self.duration
            }
            return serialized
        except Exception as e:
            logger.error(f"Error serializing chord progression: {e}")
            raise ValueError(f"Failed to serialize chord progression: {e}")

    def add_chord(self, chord: Chord) -> None:
        """Add a chord to the progression."""
        logger.debug('Adding chord: %s', chord)
        logger.info('Chord added successfully: %s', chord)
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        """Get a chord at a specific index."""
        logger.debug('Getting chord at index: %s', index)
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:
        """Get all chords in the progression."""
        logger.debug('Getting all chords')
        return self.chords

    def get_chord_names(self) -> List[str]:
        """Get the names of all chords in the progression."""
        logger.debug('Getting chord names')
        return [chord.root.note_name for chord in self.chords]

    def transpose(self, interval: int) -> None:
        """Transpose the chord progression by a given interval."""
        logger.debug('Transposing chord progression by interval: %s', interval)
        pass

    def __str__(self) -> str:
        """Convert the model to a string."""
        logger.debug('Converting model to string')
        return f"{self.name}: {' '.join(str(chord) for chord in self.chords)}"

    def __repr__(self) -> str:
        """Convert the model to a representation."""
        logger.debug('Converting model to representation')
        return (f"ChordProgression(key: {self.key!r}, "
                f"scale_type: {self.scale_type!r}, "
                f"chords: List[Chord]={self.chords!r})")

    def generate_chord_notes(self, root: Note, quality: ChordQualityType, inversion: int = 0) -> List[Note]:
        """Generate chord notes for a given root and quality."""
        logger.debug('Generating chord notes for root: %s, quality: %s, inversion: %s', root, quality, inversion)
        intervals = ChordQualityType.get_intervals(quality)  
        notes = []
        base_octave = root.octave
        
        for interval in intervals:
            note_name = root.get_note_at_interval(interval, self.key, self.scale_type)
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
        """Get the root note of a chord."""
        logger.debug('Getting root note from chord: %s', chord)
        if chord is None or chord.root is None:
            return None
        return Note(note_name=chord.root.note_name, octave=chord.root.octave, duration=1, velocity=100)

    def to_roman_numerals(self) -> List['RomanNumeral']:
        """Convert the chord progression to Roman numerals."""
        logger.debug('Converting chord progression to roman numerals')
        from src.note_gen.models.roman_numeral import RomanNumeral
        scale = Scale(root=Note(note_name=self.key, octave=4, duration=1, velocity=100), scale_type=self.scale_type)
        return []  # Add a return statement to avoid missing return error

    def chord_progression_function(self) -> None:
        """Chord progression function."""
        # Implementation
        pass

    @classmethod
    def validate_chord_progression(cls, chord_progression: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a chord progression."""
        logger.debug('Validating chord_progression: %s', chord_progression)
        required_keys = {'id', 'name', 'chords', 'key', 'scale_type', 'scale_info', 'complexity'}
        if not isinstance(chord_progression, dict) or not all(key in chord_progression for key in required_keys):
            raise ValueError("Chord progression must be a dictionary with 'id', 'name', 'chords', 'key', 'scale_type', 'scale_info', and 'complexity' keys")
        return chord_progression  # Now this is valid

    def generate_progression_from_pattern(
        self,
        pattern: List[str],
        scale_info: ScaleInfo,
        progression_length: int = 4
    ) -> 'ChordProgression':
        """
        Generate a chord progression from a pattern.

        Args:
            pattern (List[str]): List of chord patterns (e.g., ['I', 'V', 'vi', 'IV'])
            scale_info (ScaleInfo): Scale information
            progression_length (int, optional): Desired progression length. Defaults to 4.

        Returns:
            ChordProgression: Generated chord progression

        Raises:
            ValueError: If pattern is invalid or cannot generate progression
        """
        if not pattern:
            raise ValueError("Pattern must not be empty")
        
        if progression_length < 2:
            raise ValueError("Progression length must be at least 2")
        
        # Validate pattern elements
        valid_roman_numerals = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII'}
        for p in pattern:
            if p.upper() not in valid_roman_numerals:
                raise ValueError(f"Invalid chord pattern element: {p}")
        
        # Actual progression generation logic would go here
        # This is a placeholder implementation that generates basic chords
        generated_chords = []
        root_note = scale_info.root

        # Map of Roman numerals to scale degrees (for C Major scale)
        roman_to_scale_degree = {
            'I': 0,   # C
            'II': 1,  # D
            'III': 2, # E
            'IV': 3,  # F
            'V': 4,   # G
            'VI': 5,  # A
            'VII': 6  # B
        }

        # Create a Scale object with the correct arguments
        scale = Scale(scale_type=scale_info.scale_type, root=root_note)
        scale.generate_notes()  # Ensure notes are generated

        for roman_numeral in pattern[:progression_length]:
            # Determine the scale degree
            scale_degree = roman_to_scale_degree[roman_numeral.upper()]
            
            # Create a chord based on the scale degree
            chord_root = scale.get_scale_degree(scale_degree + 1)  # +1 for 1-based indexing
            
            # Ensure that the quality matches the expected type
            chord_quality = ChordQualityType.MAJOR if roman_numeral.isupper() else ChordQualityType.MINOR
            
            chord = Chord(
                root=chord_root, 
                quality=chord_quality
            )
            generated_chords.append(chord)

        # Create a name without parentheses
        progression_name = f"{scale_info.key} {scale_info.scale_type} Progression"

        return ChordProgression(
            name=progression_name,
            chords=generated_chords,
            key=scale_info.key,
            scale_type=scale_info.scale_type,
            scale_info=scale_info,
            complexity=0.5  # Default complexity
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChordProgression':
        """
        Create a ChordProgression instance from a dictionary.
        Handles nested serialization and deserialization.
        
        Args:
            data (Dict[str, Any]): Serialized chord progression data
        
        Returns:
            ChordProgression: Reconstructed chord progression instance
        """
        try:
            # Convert chord data
            if 'chords' in data:
                chords = []
                for chord_data in data['chords']:
                    chord = Chord(
                        root=Note.from_dict(chord_data.get('root', {})) if 'root' in chord_data else None,
                        quality=ChordQualityType[chord_data.get('quality', 'MAJOR')] if 'quality' in chord_data else ChordQualityType.MAJOR,
                        notes=[Note.from_dict(note) for note in chord_data.get('notes', [])] if 'notes' in chord_data else None,
                        inversion=chord_data.get('inversion')
                    )
                    chords.append(chord)
                data['chords'] = chords

            # Remove any extra fields not in the model
            filtered_data = {k: v for k, v in data.items() if k in cls.model_fields}
            
            return cls(**filtered_data)
        except Exception as e:
            logger.error(f"Error deserializing chord progression: {e}")
            raise ValueError(f"Failed to deserialize chord progression: {e}")

class Note(BaseModel):
    note_name: str
    octave: int
    duration: float
    velocity: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert Note to a dictionary."""
        return {
            'note_name': self.note_name,
            'octave': self.octave,
            'duration': self.duration,
            'velocity': self.velocity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Note':
        """
        Create a Note instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Serialized note data
        
        Returns:
            Note: Reconstructed note instance
        """
        return cls(**data)

class ChordProgressionResponse(BaseModel):
    """Response model for chord progressions."""
    name: str
    chords: List[Union[Note, dict]]  # Allow for both Note instances and dictionaries
    scale_info: dict
    key: str
    scale_type: str
    complexity: Optional[float] = None
    duration: Optional[float] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Note: lambda v: jsonable_encoder(v),
            ChordQualityType: lambda v: v.value,
            ScaleInfo: lambda v: jsonable_encoder(v),
            FakeScaleInfo: lambda v: jsonable_encoder(v),
            ObjectId: lambda v: str(v)
        }

    @field_validator('chords')
    def validate_chords(cls, v: List[Union[Note, dict]]) -> List[Union[Note, dict]]:
        """Validate chords list."""
        if not v:
            raise ValueError("Chords list cannot be empty")
        return v

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Custom serialization method."""
        result = super().model_dump(**kwargs)
        result['chords'] = [jsonable_encoder(chord) for chord in self.chords]
        result['scale_info'] = jsonable_encoder(self.scale_info)
        return result

    def json(self, *args: Any, **kwargs: Any) -> str:
        """Convert model to JSON string."""
        return json.dumps(jsonable_encoder(self))

    def __init__(self, *args, **kwargs):
        logger.debug(f"Incoming data for ChordProgressionResponse: {kwargs}")
        try:
            super().__init__(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error for ChordProgressionResponse: {e}")
            raise

class ChordProgressionCreate(BaseModel):
    """Request model for creating chord progressions."""
    name: str
    chords: List[Chord]
    key: str
    scale_type: str
    complexity: Optional[float] = None
    scale_info: Union[ScaleInfo, FakeScaleInfo]

    @field_validator('chords')
    def validate_chords(cls, v: List[Chord]) -> List[Chord]:
        """Validate chords list."""
        if not v:
            raise ValueError("Chords list cannot be empty")
        
        for chord in v:
            if chord.quality not in ChordQualityType.__members__:
                raise ValueError(f"Invalid chord quality: {chord.quality}")
        
        return v

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/v1/chord-progressions/create", response_model=ChordProgressionResponse)
async def create_chord_progression(chord_progression: ChordProgressionCreate):
    if not chord_progression.chords:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Chords are required.")
    
    for chord in chord_progression.chords:
        if chord.quality not in ChordQualityType.__members__:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid chord quality.")
    
    # Proceed with saving the chord progression
    
    return JSONResponse(content={"message": "Chord progression created successfully"}, status_code=status.HTTP_201_CREATED)