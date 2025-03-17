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

MAX_CHORDS = 10  # Maximum number of chords allowed in a progression

VALID_KEYS = {'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'}

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
    scale_info: str

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