from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.patterns import ChordProgression
from pydantic import BaseModel, Field, ConfigDict, field_validator, validator, ValidationError
from typing import List, Optional, Union, Dict, Any, Callable, Set, ForwardRef, TypeVar, Type, Literal
import logging
import uuid
from bson import ObjectId
import json
from fastapi.encoders import jsonable_encoder
import warnings
import re

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
            Chord: lambda v: jsonable_encoder(v),
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
        return [chord.quality.name for chord in self.chords]

    @validator('name')
    def validate_name(cls, v: str) -> str:
        """
        Enhanced name validation:
        - Minimum 4 characters
        - Allows alphanumeric, spaces, hyphens, underscores, and parentheses
        - Trims whitespace
        """
        if not v or len(v.strip()) < 4:
            raise ValueError('Name must be at least 4 characters long and not just whitespace')
        
        # Remove leading/trailing whitespace
        cleaned_name = v.strip()
        
        # Optional: Add regex validation for allowed characters
        if not re.match(r'^[\w\s\-()\(\)]+$', cleaned_name):
            raise ValueError('Name can only contain letters, numbers, spaces, underscores, hyphens, and parentheses')
        
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
        
        # Get enum values for valid qualities
        valid_qualities = set(ChordQuality.__members__.values())
        
        for chord in v:
            # Handle dictionary quality
            if isinstance(chord.quality, dict):
                try:
                    if 'name' in chord.quality:
                        chord.quality = ChordQuality.from_string(chord.quality['name'])
                    elif 'quality_type' in chord.quality:
                        chord.quality = ChordQuality.from_string(chord.quality['quality_type'])
                    else:
                        raise ValueError("Quality dictionary must contain 'name' or 'quality_type'")
                except (KeyError, TypeError, ValueError) as e:
                    raise ValueError(f"Invalid chord quality format: {chord.quality}") from e
            
            # Handle string quality
            elif isinstance(chord.quality, str):
                try:
                    chord.quality = ChordQuality.from_string(chord.quality)
                except ValueError as e:
                    raise ValueError(f"Invalid chord quality: {chord.quality}") from e
            
            # Handle ChordQuality enum directly
            elif not isinstance(chord.quality, ChordQuality):
                raise TypeError(f"Chord quality must be a string, dict, or ChordQuality enum, got {type(chord.quality)}")
            
            if chord.quality not in valid_qualities:
                raise ValueError(f"Invalid chord quality: {chord.quality}")
        
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

    def model_dump(self, *, mode: Literal['json', 'python'] | str = 'python', 
                 include: Any | None = None, exclude: Any | None = None, 
                 context: Any | None = None, by_alias: bool = False, 
                 exclude_unset: bool = False, exclude_defaults: bool = False, 
                 exclude_none: bool = False, round_trip: bool = False, 
                 warnings: Literal['none', 'warn', 'error'] | bool = True, 
                 serialize_as_any: bool = False) -> Dict[str, Any]:
        """Convert the model to a dictionary representation."""
        logger.debug("ChordProgression.model_dump called with mode=%s", mode)
        result = super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any
        )
        
        # Convert any enum values to their string representations for MongoDB
        if 'chords' in result and isinstance(result['chords'], list):
            for chord in result['chords']:
                if isinstance(chord, dict) and 'quality' in chord and hasattr(chord['quality'], 'value'):
                    # Convert enum to string value
                    chord['quality'] = chord['quality'].value if hasattr(chord['quality'], 'value') else str(chord['quality'])
                    
        return result

    def json(self, *args: Any, **kwargs: Any) -> str:
        """Convert model to JSON string."""
        return json.dumps(jsonable_encoder(self))

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert the model to a dictionary, preserving raw objects for testing."""
        logger.debug('Converting model to dictionary')
        return self.model_dump(*args, mode='python', **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert ChordProgression to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "chords": [chord.to_dict() for chord in self.chords] if self.chords else [],
            "key": self.key,
            "scale_type": self.scale_type,
            "complexity": self.complexity,
            "scale_info": self.scale_info.model_dump() if self.scale_info else None,
            "quality": self.scale_info.scale_type if self.scale_info else None
        }

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
        if self.chords is None:
            return []
        return [chord.root.note_name for chord in self.chords if chord is not None and chord.root is not None]

    def calculate_complexity(self) -> float:
        """Calculate the complexity of the chord progression."""
        logger.debug('Calculating complexity')
        if self.chords is None:
            return 0.0
        return sum(1 for chord in self.chords if chord is not None) / len(self.chords) if self.chords else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert ChordProgression to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "chords": [chord.to_dict() for chord in self.chords] if self.chords else [],
            "key": self.key,
            "scale_type": self.scale_type,
            "complexity": self.complexity,
            "scale_info": self.scale_info.to_dict(),
            "quality": self.scale_info.scale_type if self.scale_info else None
        }

    def unreachable_example(self) -> str:
        """Unreachable example."""
        if False:
            return "This will never execute"
        return "This will execute"

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

    def generate_chord_notes(self, chord: Chord, inversion: int = 0) -> List[Note]:
        """Generate notes for a chord based on its root and quality.
        
        Args:
            chord (Chord): The chord to generate notes for
            inversion (int, optional): Chord inversion (0 = root position,
                                      1 = first inversion, etc). Defaults to 0.
        
        Returns:
            List[Note]: List of notes in the chord
        """
        logger.debug(f"Generating notes for chord with root: {chord.root}, quality: {chord.quality}")
        
        if not chord or not chord.root:
            logger.error("Invalid chord or missing root")
            return []
            
        # Get intervals based on chord quality
        intervals = Chord.get_intervals(chord.quality)
        logger.debug(f"Intervals for quality {chord.quality}: {intervals}")
        
        notes = []
        base_octave = chord.root.octave
        logger.debug(f"Base octave from chord root: {base_octave}")
        
        # Create scale for reference
        scale = Scale(root=Note(note_name=self.key, octave=base_octave), scale_type=self.scale_type)
        scale_notes = scale._generate_scale_notes()
        scale_size = len(scale_notes)
        logger.debug(f"Generated scale with {scale_size} notes: {[n.note_name for n in scale_notes]}")
        
        # Find the position of the chord root in the scale
        root_index = -1
        for i, note in enumerate(scale_notes):
            if note.note_name == chord.root.note_name:
                root_index = i
                break
                
        if root_index == -1:
            logger.warning(f"Chord root {chord.root.note_name} not found in scale, using approximate position")
            # Fallback: use approximate position
            root_index = 0
            
        logger.debug(f"Root note position in scale: {root_index}")
        
        for interval in intervals:
            # Calculate the actual position in the scale
            note_index_in_scale = (root_index + interval) % scale_size
            target_note = scale_notes[note_index_in_scale]
            
            # Calculate octave adjustment based on how many times we wrap around the scale
            octave_adjustment = (root_index + interval) // scale_size
            final_octave = base_octave + octave_adjustment
            
            logger.debug(f"  - Interval {interval}: Scale index={note_index_in_scale}, " 
                        f"Note={target_note.note_name}, Octave adj={octave_adjustment}, "
                        f"Final octave={final_octave}")
            
            notes.append(Note(
                note_name=target_note.note_name,
                octave=final_octave,
                duration=1,
                velocity=100
            ))
        
        # Apply inversions if needed    
        if inversion > 0:
            effective_inversion = min(inversion, len(notes) - 1)
            logger.debug(f"Applying inversion: {effective_inversion}")
            
            for i in range(effective_inversion):
                first_note = notes.pop(0)
                logger.debug(f"  - Moving {first_note.note_name}{first_note.octave} up an octave")
                notes.append(Note(
                    note_name=first_note.note_name,
                    octave=first_note.octave + 1,
                    duration=first_note.duration,
                    velocity=first_note.velocity
                ))
        
        logger.debug(f"Final chord notes: {[f'{n.note_name}{n.octave}' for n in notes]}")            
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
        scale = Scale(root=Note(note_name=self.key, octave=4), scale_type=self.scale_type)
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
            
            # Determine chord quality based on roman numeral case
            from src.note_gen.models.chord import ChordQuality
            
            # Default quality based on case (uppercase = MAJOR, lowercase = MINOR)
            chord_quality = ChordQuality.MAJOR if roman_numeral.isupper() else ChordQuality.MINOR
            
            # Detect specific chord qualities from roman numeral notation
            if 'o' in roman_numeral:
                chord_quality = ChordQuality.DIMINISHED
            elif '+' in roman_numeral:
                chord_quality = ChordQuality.AUGMENTED
            elif '7' in roman_numeral:
                # Check if it's minor_seventh or dominant_seventh
                if roman_numeral.islower():
                    chord_quality = ChordQuality.MINOR_SEVENTH
                else:
                    chord_quality = ChordQuality.DOMINANT_SEVENTH
            elif 'Δ' in roman_numeral or 'maj7' in roman_numeral:
                chord_quality = ChordQuality.MAJOR_SEVENTH
                
            logger.debug(f"Creating chord with root {chord_root.note_name} and quality {chord_quality}")
                
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
                        quality=ChordQuality[chord_data.get('quality', 'MAJOR')] if 'quality' in chord_data else ChordQuality.MAJOR,
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
    chords: List[Union[Note, dict, Chord]]
    scale_info: dict
    key: str
    scale_type: str
    complexity: Optional[float] = None
    duration: Optional[float] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Note: lambda v: jsonable_encoder(v),
            Chord: lambda v: jsonable_encoder(v),
            ScaleInfo: lambda v: jsonable_encoder(v),
            FakeScaleInfo: lambda v: jsonable_encoder(v),
            ObjectId: lambda v: str(v)
        }
    )

    @field_validator('chords', mode='before')
    def validate_chords(cls, v: List[Any]) -> List[Union[Note, dict, Chord]]:
        """Validate and normalize chords list."""
        if not v:
            raise ValueError("Chords list cannot be empty")
        
        normalized_chords = []
        for chord in v:
            if isinstance(chord, str):
                # Convert string chord to proper chord dict
                logger.debug(f"Converting string chord: {chord}")
                try:
                    # Create a simple chord dict with the string as the note name
                    normalized_chord = {
                        "root": {"note_name": chord, "octave": 4, "duration": 1.0, "velocity": 64},
                        "quality": "MAJOR",
                        "notes": []
                    }
                    normalized_chords.append(normalized_chord)
                except Exception as e:
                    logger.error(f"Error converting string chord '{chord}': {e}")
                    raise ValueError(f"Invalid chord format: {chord}")
            elif isinstance(chord, dict):
                normalized_chords.append(chord)
            elif isinstance(chord, Chord) or isinstance(chord, Note):
                normalized_chords.append(chord)
            else:
                logger.error(f"Invalid chord type: {type(chord)}, value: {chord}")
                raise TypeError(f"Chord must be a string, dictionary, Chord, or Note instance, not {type(chord)}")
        
        return normalized_chords

    def model_dump(self, *, mode: Literal['json', 'python'] | str = 'python', 
                 include: Any | None = None, exclude: Any | None = None, 
                 context: Any | None = None, by_alias: bool = False, 
                 exclude_unset: bool = False, exclude_defaults: bool = False, 
                 exclude_none: bool = False, round_trip: bool = False, 
                 warnings: Literal['none', 'warn', 'error'] | bool = True, 
                 serialize_as_any: bool = False) -> Dict[str, Any]:
        """Convert the model to a dictionary representation."""
        logger.debug("ChordProgressionResponse.model_dump called with mode=%s", mode)
        result = super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any
        )
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
            # Handle dictionary quality
            if isinstance(chord.quality, dict):
                try:
                    if 'name' in chord.quality:
                        chord.quality = ChordQuality.from_string(chord.quality['name'])
                    elif 'quality_type' in chord.quality:
                        chord.quality = ChordQuality.from_string(chord.quality['quality_type'])
                    else:
                        raise ValueError("Quality dictionary must contain 'name' or 'quality_type'")
                except (KeyError, TypeError, ValueError) as e:
                    raise ValueError(f"Invalid chord quality format: {chord.quality}") from e
            
            # Handle string quality
            elif isinstance(chord.quality, str):
                try:
                    chord.quality = ChordQuality.from_string(chord.quality)
                except ValueError as e:
                    raise ValueError(f"Invalid chord quality: {chord.quality}") from e
            
            # Handle ChordQuality enum directly
            elif not isinstance(chord.quality, ChordQuality):
                raise TypeError(f"Chord quality must be a string, dict, or ChordQuality enum, got {type(chord.quality)}")
            
            if chord.quality not in valid_qualities:
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
        if chord.quality not in ChordQuality.__members__:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid chord quality.")
    
    # Proceed with saving the chord progression
    
    return JSONResponse(content={"message": "Chord progression created successfully"}, status_code=status.HTTP_201_CREATED)