from typing import Any, List, Optional, Dict, Union, Tuple, ClassVar, Annotated, Callable, Sequence, Literal
from pydantic import BaseModel, Field, model_validator, root_validator, ConfigDict, field_validator, PrivateAttr, ValidationInfo
from src.note_gen.models.note import Note
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.chord import Chord, ChordQuality
import uuid
import logging
import re
import math

logger = logging.getLogger(__name__)

NoteType = Union[Note, ScaleDegree]
from src.note_gen.models.scale import Scale

__all__ = ['COMMON_PROGRESSIONS', 'NOTE_PATTERNS', 'RHYTHM_PATTERNS', 'Patterns']

COMMON_PROGRESSIONS: Dict[str, List[str]] = {
    # Basic progressions
    "I-IV-V-I": ["I", "IV", "V", "I"],
    "ii-V-I": ["ii", "V", "I"],
    "I-vi-ii-V": ["I", "vi", "ii", "V"],
    
    # Extended progressions
    "I-V-vi-IV": ["I", "V", "vi", "IV"],  # Pop progression
    "I-vi-IV-V": ["I", "vi", "IV", "V"],  # 50s progression
    "vi-IV-I-V": ["vi", "IV", "I", "V"],  # Pop progression variant
    
    # Jazz progressions
    "ii-V-I-vi": ["ii", "V", "I", "vi"],  # Basic jazz
    "iii-vi-ii-V": ["iii", "vi", "ii", "V"],  # Jazz turnaround
    "I-vi-ii-V-I": ["I", "vi", "ii", "V", "I"],  # Extended jazz
    
    # Blues progressions
    "I-I-I-I-IV-IV-I-I-V-IV-I-V": ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"],  # 12-bar blues
    "i-iv-i-V": ["i", "iv", "i", "V"],  # Minor blues
    
    # Minor progressions
    "i-iv-v": ["i", "iv", "v"],  # Natural minor
    "i-iv-V": ["i", "iv", "V"],  # Harmonic minor
    "i-VI-III-VII": ["i", "VI", "III", "VII"],  # Epic minor
    
    # Modal progressions
    "i-VII-VI": ["i", "VII", "VI"],  # Aeolian
    "I-II-IV": ["I", "II", "IV"],  # Lydian
    
    # Contemporary progressions
    "vi-IV-I-V": ["vi", "IV", "I", "V"],  # Modern pop
    "I-V-vi-iii-IV": ["I", "V", "vi", "iii", "IV"],  # Extended pop
    "i-III-VII-VI": ["i", "III", "VII", "VI"],  # Modern rock
    
    # Circle progressions
    "I-IV-vii-iii-vi-ii-V": ["I", "IV", "vii", "iii", "vi", "ii", "V"],  # Circle of fifths
    "vi-ii-V-I": ["vi", "ii", "V", "I"]  # Jazz circle
}

NOTE_PATTERNS = {
    'Simple Triad': {
        'name': 'Simple Triad',
        'description': 'Basic major triad pattern (root, major third, perfect fifth)',
        'tags': ['default', 'triad', 'major'],
        'complexity': 0.5,
        'intervals': [0, 4, 7],  # Root, major third, perfect fifth
        'data': {
            'notes': ['C4', 'E4', 'G4'],
            'intervals': [4, 3],  # Major third (4) and minor third (3)
            'duration': 1.0,
            'position': 0.0,
            'velocity': 100,
            'direction': 'up',
            'use_chord_tones': False,
            'use_scale_mode': False,
            'arpeggio_mode': False,
            'restart_on_chord': False,
            'octave_range': [4, 5],
            'default_duration': 1.0
        }
    },
    'Minor Triad': {
        'name': 'Minor Triad',
        'description': 'Basic minor triad pattern (root, minor third, perfect fifth)',
        'tags': ['default', 'triad', 'minor'],
        'complexity': 0.5,
        'intervals': [0, 3, 7],  # Root, minor third, perfect fifth
        'data': {
            'notes': ['C4', 'Eb4', 'G4'],
            'intervals': [3, 4],  # Minor third (3) and major third (4)
            'duration': 1.0,
            'position': 0.0,
            'velocity': 100,
            'direction': 'up',
            'use_chord_tones': False,
            'use_scale_mode': False,
            'arpeggio_mode': False,
            'restart_on_chord': False,
            'octave_range': [4, 5],
            'default_duration': 1.0
        }
    }
}

RHYTHM_PATTERNS: Dict[str, Dict[str, Any]] = {
    'basic_4_4': {
        'name': 'basic_4_4',
        'description': "Basic 4/4 rhythm pattern with quarter notes",
        'tags': ["default", "basic"],
        'pattern': [1.0, 1.0, 1.0, 1.0],  # Pattern for RhythmPattern
        'data': {
            'time_signature': '4/4',
            'default_duration': 1.0,
            'groove_type': "straight",
            'swing_enabled': False,
            'swing_ratio': 0.67,  # Default swing ratio even when disabled
            'humanize_amount': 0.1,
            'variation_probability': 0.2,
            'style': "basic",
            'duration': 4.0,
            'total_duration': 4.0,
            'notes': [
                {
                    'position': 0.0,
                    'duration': 1.0,
                    'velocity': 100,
                    'is_rest': False
                },
                {
                    'position': 1.0,
                    'duration': 1.0,
                    'velocity': 100,
                    'is_rest': False
                },
                {
                    'position': 2.0,
                    'duration': 1.0,
                    'velocity': 100,
                    'is_rest': False
                },
                {
                    'position': 3.0,
                    'duration': 1.0,
                    'velocity': 100,
                    'is_rest': False
                }
            ]
        },
        'complexity': 0.5,
        'swing_enabled': False,
        'swing_ratio': 0.67,
        'duration': 4.0
    },
    'swing_basic': {
        'name': 'swing_basic',
        'description': "Basic swing rhythm pattern",
        'tags': ["default", "swing"],
        'pattern': [1.0, 1.0, 1.0, 1.0],  # Pattern for RhythmPattern
        'data': {
            'time_signature': '4/4',
            'default_duration': 1.0,
            'groove_type': "swing",
            'swing_enabled': True,
            'swing_ratio': 0.67,
            'humanize_amount': 0.1,
            'variation_probability': 0.2,
            'style': "swing",
            'duration': 4.0,
            'total_duration': 4.0,
            'notes': [
                {
                    'position': 0.0,
                    'duration': 1.0,
                    'velocity': 100,
                    'is_rest': False,
                    'swing_ratio': 0.67
                },
                {
                    'position': 1.0,
                    'duration': 1.0,
                    'velocity': 100,
                    'is_rest': False,
                    'swing_ratio': 0.67
                },
                {
                    'position': 2.0,
                    'duration': 1.0,
                    'velocity': 100,
                    'is_rest': False,
                    'swing_ratio': 0.67
                },
                {
                    'position': 3.0,
                    'duration': 1.0,
                    'velocity': 100,
                    'is_rest': False,
                    'swing_ratio': 0.67
                }
            ]
        },
        'complexity': 0.7,
        'swing_enabled': True,
        'swing_ratio': 0.67,
        'duration': 4.0
    }
}

class NotePatternData(BaseModel):
    """Data structure for note pattern parameters.
    
    IMPORTANT: In musical notation, negative values often represent rests.
    Throughout this class and related models, we follow this convention:
    - Positive durations represent regular notes
    - Negative durations represent rests, with the absolute value as the duration
    - Zero durations are not allowed and will raise a ValueError during validation
    """
    intervals: List[int]
    notes: List[Note]

    @model_validator(mode='before')
    def validate_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get('intervals') and not data.get('notes'):
            raise ValueError('Either intervals or notes must be provided')
        return data

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        validate_default=True,
        extra="allow"
    )

    @classmethod
    @field_validator('notes')
    def validate_notes(cls, v: Optional[list[Union[str, dict[str, Any], Note, int, float]]]) -> list[Union[str, dict[str, Any], Note, int, float]]:
        if v is None:
            return []
        return [cls._convert_note(note) for note in v]

    @staticmethod
    def _convert_note(note: Union[str, dict[str, Any], Note, int, float]) -> Union[str, dict[str, Any], Note, int, float]:
        if isinstance(note, str):
            return note
        elif isinstance(note, dict):
            return note
        elif isinstance(note, (int, float)):
            return float(note)
        return note

    @classmethod
    @field_validator('intervals')
    def validate_intervals(cls, v: Optional[list[Union[str, dict[str, Any], int, float]]]) -> list[Union[str, dict[str, Any], int, float]]:
        if v is None:
            return []
        return [cls._convert_interval(interval) for interval in v]

    @staticmethod
    def _convert_interval(interval: Union[str, dict[str, Any], int, float, None]) -> Union[str, dict[str, Any], int, float, None]:
        if isinstance(interval, str):
            return interval
        elif isinstance(interval, dict):
            return interval
        elif isinstance(interval, (int, float)):
            return float(interval)
        # Handle None or other types
        return interval

    @classmethod
    @field_validator('duration')
    def validate_duration(cls, v: Optional[Union[int, float]]) -> Union[int, float]:
        if v is None:
            return 1.0
        if v <= 0:
            raise ValueError('Duration must be greater than 0')
        return float(v)

    @classmethod
    @field_validator('direction')
    def validate_direction(cls, v: Optional[str]) -> str:
        """Validate direction value."""
        if not v:
            return "up"
        v = v.lower().strip()
        if v not in ["up", "down", "random"]:
            raise ValueError("Direction must be 'up', 'down', or 'random'")
        return v

    @classmethod
    @field_validator('octave_range')
    def validate_octave_range(cls, v: Optional[tuple[int, int]]) -> tuple[int, int]:
        if v is None:
            return (0, 0)
        if len(v) != 2 or v[0] > v[1]:
            raise ValueError("Octave range must be a tuple of two integers where the first is less than or equal to the second")
        return v

    @classmethod
    @field_validator('default_duration')
    def validate_default_duration(cls, v: Optional[Union[int, float]]) -> Union[int, float]:
        if v is None:
            return 1.0
        if v <= 0:
            raise ValueError('Default duration must be greater than 0')
        return float(v)

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert model to dictionary with proper handling of Note objects."""
        data = super().model_dump(**kwargs)
        
        # Convert Note objects to dictionaries
        if data.get('notes'):
            notes_list = []
            for note in data['notes']:
                if hasattr(note, 'model_dump'):
                    notes_list.append(note.model_dump())
                else:
                    notes_list.append(note)
            data['notes'] = notes_list
            
        return data

class NotePattern(BaseModel):
    """
    A pattern of musical notes.
    
    IMPORTANT: In musical notation, negative values often represent rests.
    Throughout this class and related models, we follow this convention:
    - Positive durations represent regular notes
    - Negative durations represent rests, with the absolute value as the duration
    """
    id: Optional[str] = Field(None, description="ID of the note pattern")
    name: str = Field(min_length=2, description="Name must be at least 2 characters long")
    description: str = Field(default="", description="Pattern description")
    tags: list[str] = Field(default_factory=lambda: ["default"], description="Pattern tags")
    complexity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Complexity must be between 0 and 1")
    intervals: List[int]
    data: Optional[Union[NotePatternData, Dict[str, Any]]] = Field(default=None, description="Additional pattern data")
    style: Optional[str] = Field(default=None, description="Pattern style")
    is_test: Optional[bool] = Field(default=False, description="Test flag")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        validate_default=True,
        extra="allow"
    )

    @classmethod
    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty or whitespace-only."""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty or whitespace-only")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v

    @classmethod
    @field_validator('intervals')
    def validate_intervals(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError('Intervals must not be empty')
        if not all(isinstance(i, int) for i in v):
            raise ValueError('Intervals must be integers')
        return v

    @classmethod
    @field_validator('tags')
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate that tags are not empty or whitespace-only."""
        if not v:
            return ["default"]
        validated_tags = []
        for tag in v:
            tag = tag.strip()
            if not tag:
                continue
            validated_tags.append(tag)
        if not validated_tags:
            return ["default"]
        return validated_tags

    @classmethod
    @field_validator('complexity')
    def validate_complexity(cls, v: Optional[float]) -> Optional[float]:
        """Validate complexity is within range."""
        if v is None:
            return 0.5
        if not 0.0 <= v <= 1.0:
            raise ValueError("Complexity must be between 0.0 and 1.0")
        return v

    @model_validator(mode='after')
    def normalize_note_pattern(self) -> 'NotePattern':
        """Normalize the note pattern data structure and ensure required fields exist.
        
        This validator ensures that:
        1. If data field exists, compatible fields are copied to the top level
        2. If top-level fields exist but data doesn't, create a data structure
        3. Required fields like duration, position, and velocity have valid values
        """
        if self.data is None:
            self.data = NotePatternData()

        # Convert dict to NotePatternData if needed
        if isinstance(self.data, dict):
            self.data = NotePatternData(**self.data)

        return self

    def total_duration(self) -> float:
        """Calculate the total duration of the pattern."""
        if not self.data:
            return 0.0
            
        # Handle case where data is a dictionary
        if isinstance(self.data, dict):
            notes = self.data.get('notes', [])
            if not notes:
                return 0.0
            return sum(float(getattr(note, 'duration', 0.0)) for note in notes)
            
        # Handle case where data is a NotePatternData object
        if not hasattr(self.data, 'notes') or not self.data.notes:
            return 0.0
            
        # Sum durations of all notes, handling different types
        total = 0.0
        for note in self.data.notes:
            if hasattr(note, 'duration'):
                total += float(note.duration)
        return total

    def get_notes(self) -> List[Note]:
        """Get the list of notes in the pattern."""
        if self.data is None or not hasattr(self.data, 'notes'):
            return []
        return self.data.notes

    def add_note(self, note: Note) -> None:
        """Add a note to the pattern."""
        if self.data is None:
            self.data = NotePatternData()
        if not hasattr(self.data, 'notes'):
            self.data.notes = []
        self.data.notes.append(note)

    def remove_note(self, index: int) -> None:
        """Remove a note from the pattern."""
        if self.data is not None and hasattr(self.data, 'notes') and self.data.notes and 0 <= index < len(self.data.notes):
            self.data.notes.pop(index)

    def clear_notes(self) -> None:
        """Clear all notes from the pattern."""
        if self.data is not None and hasattr(self.data, 'notes'):
            self.data.notes = []

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Enhanced model_dump to ensure data is properly serialized."""
        data = super().model_dump(**kwargs)
        
        # Convert Note objects to dictionaries
        if data.get('data') and data['data'].get('notes'):
            data['data']['notes'] = [
                note.model_dump() if hasattr(note, 'model_dump') else note 
                for note in data['data']['notes']
            ]
            
        # Convert NotePatternData to dictionary
        if data.get('data') and hasattr(data['data'], 'model_dump'):
            data['data'] = data['data'].model_dump()
            
        return data

    def add_tag(self, tag: str) -> None:
        """Add a tag to the note pattern."""
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note pattern."""
        if tag in self.tags and len(self.tags) > 1:  # Keep at least one tag
            self.tags.remove(tag)

    @classmethod
    @field_validator('position')
    def validate_position(cls, v: Optional[Union[int, float]]) -> Union[int, float]:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('Position cannot be negative')
        return float(v)

    @classmethod
    @field_validator('direction')
    def validate_direction(cls, v: Optional[str]) -> str:
        if v is None:
            return 'forward'
        if v.lower() not in ['forward', 'backward']:
            raise ValueError("Direction must be either 'forward' or 'backward'")
        return v.lower()

    @model_validator(mode='before')
    def validate_notes_or_intervals(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get('notes') and not data.get('intervals'):
            raise ValueError('Either notes or intervals must be provided')
        return data

    @field_validator('intervals')
    @classmethod
    def validate_intervals(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            if not all(isinstance(i, int) for i in v):
                raise ValueError('Intervals must be integers')
        return v

class ChordPatternItem(BaseModel):
    """
    Represents a single chord in a chord progression pattern.
    
    This model is used to define the structure of each chord in a 
    chord progression pattern without tying it to a specific key/scale.
    """
    degree: Union[int, str] = Field(
        ..., 
        description="Scale degree (1-7) or Roman numeral (I-VII)"
    )
    quality: str = Field(
        default=ChordQuality.MAJOR.value,
        description="Chord quality (e.g., MAJOR, MINOR, DOMINANT_SEVENTH)"
    )
    duration: Optional[float] = Field(
        4.0, 
        gt=0, 
        description="Duration of the chord in beats"
    )
    inversion: Optional[int] = Field(
        None, 
        description="Chord inversion (0-based index)"
    )
    
    # Internal field to store numeric degree for calculations
    _numeric_degree: Optional[int] = PrivateAttr(default=None)
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="allow"
    )
    
    @field_validator('degree')
    def validate_degree(cls, v: Union[int, str]) -> int:
        """Validate the degree value."""
        if isinstance(v, str):
            # Handle Roman numerals
            v_str = v.strip().upper()
            roman_map = {
                'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7
            }
            
            # Convert to integer
            if v_str in roman_map:
                return roman_map[v_str]
            
            # If we get here, it's not a valid Roman numeral
            raise ValueError(f"Invalid Roman numeral: {v}")
        
        # Validate integer degree
        if not isinstance(v, int):
            raise ValueError(f"Degree must be an integer or Roman numeral, got {type(v).__name__}")
            
        if not 1 <= v <= 7:
            raise ValueError(f"Scale degree must be between 1 and 7, got {v}")
            
        return v
        
    @model_validator(mode='before')
    def set_quality_from_roman_numeral(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set quality based on Roman numeral case if not explicitly provided."""
        degree = data.get('degree')
        if isinstance(degree, str) and 'quality' not in data:
            # Check for lowercase to infer quality
            roman_map_lower = {
                'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7
            }
            
            v_str = degree.strip()
            if v_str in roman_map_lower:
                data['quality'] = ChordQuality.MINOR.value
                
        return data

    @classmethod
    @field_validator('quality', mode='before')
    def validate_quality(cls, v: Union[str, ChordQuality, dict[str, Any]]) -> str:
        """Validate and convert quality to string value."""
        if isinstance(v, str):
            try:
                # Try to convert string to ChordQuality enum and then to string value
                return ChordQuality.from_string(v).value
            except (ValueError, KeyError):
                raise ValueError(f"Invalid chord quality string: {v}")
        elif isinstance(v, ChordQuality):
            return v.value
        elif isinstance(v, dict) and 'name' in v:
            try:
                quality_name = v['name'].upper().strip()
                return ChordQuality[quality_name].value
            except (KeyError, ValueError):
                raise ValueError(f"Invalid chord quality: {v['name']}")
        else:
            raise ValueError("Quality must be a string, ChordQuality enum, or dict with 'name' key")

    @model_validator(mode='after')
    def validate_chord_pattern_item(self) -> 'ChordPatternItem':
        """Validate the complete chord pattern item."""
        if self.duration is not None and self.duration <= 0:
            raise ValueError("Duration must be greater than 0")
                
        return self

    @classmethod
    @field_validator('inversion')
    def validate_inversion(cls, v: Optional[int]) -> Optional[int]:
        """Validate chord inversion."""
        if v is not None and not 0 <= v <= 3:
            raise ValueError("Inversion must be between 0 and 3")
        return v

class ChordProgressionPattern(BaseModel):
    """
    A reusable pattern for chord progressions.
    
    This allows defining patterns like "I-IV-V-I" that can be applied to any key/scale.
    """
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="ID of the chord progression pattern"
    )
    name: str = Field(
        ..., 
        min_length=2,
        description="Name of the chord progression pattern"
    )
    description: str = Field(
        default="",
        description="Description of the pattern"
    )
    tags: list[str] = Field(
        default_factory=lambda: ["default"],
        description="Tags for categorization"
    )
    complexity: Optional[float] = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Complexity score (0.0-1.0)"
    )
    genre: Optional[str] = Field(
        default=None,
        description="Musical genre"
    )
    pattern: list[ChordPatternItem] = Field(
        ...,
        min_length=1,
        description="List of chord pattern items"
    )
    is_test: Optional[bool] = Field(
        default=None,
        description="Test flag"
    )
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )

    @classmethod
    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty or whitespace-only."""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty or whitespace-only")
        return v

    @classmethod
    @field_validator('tags')
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate that tags are not empty or whitespace-only."""
        if not v:
            return ["default"]
        
        # Check if any tags are empty or just whitespace
        for tag in v:
            if not tag or tag.isspace():
                raise ValueError("Tags must contain non-whitespace strings")
                
        clean_tags = []
        for tag in v:
            if tag and tag.strip():
                clean_tags.append(tag.strip())
        if not clean_tags:
            return ["default"]
        return clean_tags
    
    @model_validator(mode='after')
    def validate_pattern_not_empty(self) -> 'ChordProgressionPattern':
        """Validate that pattern is not empty and all items are valid."""
        if not self.pattern:
            raise ValueError("Pattern cannot be empty")
            
        # Validate that all pattern items have valid durations
        for i, item in enumerate(self.pattern):
            if item.duration is not None and item.duration <= 0:
                raise ValueError(f"Pattern item at index {i} has invalid duration: {item.duration}. Duration must be greater than 0.")
                
        return self

    def roman_numerals(self) -> list[str]:
        """Get the chord progression as Roman numerals."""
        roman_map: Dict[int, str] = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'}
        result = []
        for item in self.pattern:
            if isinstance(item.degree, int) and item.degree in roman_map:
                result.append(roman_map[item.degree])
            else:
                # If it's already a string (Roman numeral), use it directly
                result.append(str(item.degree))
        return result

    def total_duration(self) -> float:
        """Calculate the total duration of the chord progression pattern."""
        return sum(float(item.duration) for item in self.pattern if item.duration is not None)

    @classmethod
    def from_degrees_and_qualities(cls, name: str, degrees: list[int], 
                                 qualities: Optional[list[str]] = None,
                                 durations: Optional[list[float]] = None,
                                 description: str = "", tags: Optional[list[str]] = None,
                                 complexity: float = 0.5, genre: Optional[str] = None) -> 'ChordProgressionPattern':
        """
        Create a chord progression pattern from lists of degrees and qualities.
        
        Args:
            name: Name of the pattern
            degrees: List of scale degrees (1-7)
            qualities: Optional list of chord qualities (defaults to MAJOR)
            durations: Optional list of durations (defaults to 4.0)
            description: Optional description
            tags: Optional tags
            complexity: Optional complexity (0.0-1.0)
            genre: Optional genre
            
        Returns:
            A new ChordProgressionPattern instance
        """
        if not degrees:
            raise ValueError("Degrees list cannot be empty")
            
        if not qualities:
            qualities = [ChordQuality.MAJOR] * len(degrees)
        if not durations:
            durations = [4.0] * len(degrees)
            
        # Validate degrees
        for i, degree in enumerate(degrees):
            if not isinstance(degree, int) or not 1 <= degree <= 7:
                raise ValueError(f"Degree at index {i} must be an integer between 1 and 7, got {degree}")
                
        # Validate durations
        for i, duration in enumerate(durations):
            if duration <= 0:
                raise ValueError(f"Duration at index {i} must be greater than 0, got {duration}")
        
        if len(qualities) != len(degrees):
            raise ValueError("Number of qualities must match number of degrees")
        if len(durations) != len(degrees):
            raise ValueError("Number of durations must match number of degrees")
            
        pattern = [
            ChordPatternItem(
                degree=degree,
                quality=quality,
                duration=duration
            )
            for degree, quality, duration in zip(degrees, qualities, durations)
        ]
        
        return cls(
            name=name,
            description=description,
            tags=tags or ["default"],
            complexity=complexity,
            genre=genre,
            pattern=pattern
        )

    @classmethod
    def from_roman_numerals(cls, name: str, numerals: list[str], 
                          qualities: Optional[list[str]] = None,
                          durations: Optional[list[float]] = None,
                          description: str = "", tags: Optional[list[str]] = None,
                          complexity: float = 0.5, genre: Optional[str] = None) -> 'ChordProgressionPattern':
        """
        Create a chord progression pattern from a list of Roman numerals.
        
        Args:
            name: Name of the pattern
            numerals: List of Roman numerals (I-VII)
            qualities: Optional list of chord qualities
            durations: Optional list of durations
            description: Optional description
            tags: Optional tags
            complexity: Optional complexity (0.0-1.0)
            genre: Optional genre
            
        Returns:
            A new ChordProgressionPattern instance
        """
        if not numerals:
            raise ValueError("Numerals list cannot be empty")
            
        if not durations:
            durations = [4.0] * len(numerals)
            
        # Validate Roman numerals
        roman_map = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
            'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7
        }
        for i, numeral in enumerate(numerals):
            if not isinstance(numeral, str) or numeral.upper() not in [r.upper() for r in roman_map.keys()]:
                raise ValueError(f"Invalid Roman numeral at index {i}: {numeral}")
                
        # Validate durations
        for i, duration in enumerate(durations):
            if duration <= 0:
                raise ValueError(f"Duration at index {i} must be greater than 0, got {duration}")
        
        if len(durations) != len(numerals):
            raise ValueError("Number of durations must match number of numerals")
            
        if qualities and len(qualities) != len(numerals):
            raise ValueError("Number of qualities must match number of numerals")
        
        # Create pattern items directly using ChordPatternItem validation
        pattern: List[ChordPatternItem] = []
        for i, numeral in enumerate(numerals):
            quality = qualities[i] if qualities and i < len(qualities) else ChordQuality.MAJOR
            pattern_item = ChordPatternItem(
                degree=numeral,  # ChordPatternItem will handle validation
                quality=quality,  # Will be updated based on case if needed
                duration=durations[i]
            )
            pattern.append(pattern_item)
            
        return cls(
            name=name,
            description=description,
            tags=tags or ["default"],
            complexity=complexity,
            genre=genre,
            pattern=pattern
        )

    @classmethod
    def from_chord_progression(cls, progression: Any, name: Optional[str] = None,
                               description: str = "", tags: Optional[list[str]] = None) -> 'ChordProgressionPattern':
        """
        Extract pattern from an existing chord progression.
        
        This allows saving the abstract pattern for reuse with different keys/scales.
        
        Args:
            progression: The chord progression to extract the pattern from
            name: Optional name for the pattern (defaults to progression's name + " Pattern")
            description: Optional description
            tags: Optional tags
            
        Returns:
            A ChordProgressionPattern instance
        """
        if not name:
            name = f"{progression.name} Pattern"
        
        # Map note names to scale degrees in C major scale
        note_to_degree = {
            "C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "A": 6, "B": 7
        }
            
        pattern: List[ChordPatternItem] = []
        for chord in progression.chords:
            # Get the root note name without octave
            root_name = chord.root.note_name.split('/')[0]
            
            # Map to scale degree
            degree = note_to_degree.get(root_name, 1)  # Default to 1 if not found
            
            pattern.append(ChordPatternItem(
                degree=degree,
                quality=chord.quality,
                duration=getattr(chord, 'duration', None),
                inversion=getattr(chord, 'inversion', None)
            ))
            
        return cls(
            name=name,
            description=description,
            tags=tags or getattr(progression, 'tags', ["default"]),
            complexity=getattr(progression, 'complexity', 0.5),
            genre=getattr(progression, 'genre', None),
            pattern=pattern
        )

class ChordProgression(BaseModel):
    """
    A progression of chords.
    
    This class represents a sequence of chords that can be used in a musical composition.
    """
    id: Optional[str] = Field(default=None, description="ID of the chord progression")
    name: str = Field(..., min_length=2, description="Name of the chord progression")
    description: str = Field(default="", description="Description of the progression")
    tags: list[str] = Field(default_factory=lambda: ["default"], description="Tags for categorization")
    complexity: float = Field(default=0.5, ge=0.0, le=1.0, description="Complexity score (0.0-1.0)")
    genre: Optional[str] = Field(default=None, description="Musical genre")
    chords: list[Chord] = Field(..., min_length=1, description="List of chords in the progression")
    is_test: Optional[bool] = Field(default=None, description="Test flag")
    
    model_config = ConfigDict(
        validate_assignment=True
    )
    
    @classmethod
    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 4:
            raise ValueError('Name must be at least 4 characters long and not just whitespace')

        cleaned_name = v.strip()

        # Allow spaces, hyphens, and underscores in names
        import re
        if not re.match(r'^[a-zA-Z0-9\s_-]+$', cleaned_name):
            raise ValueError('Name can only contain letters, numbers, spaces, underscores, and hyphens')

        return cleaned_name
    
    @classmethod
    @field_validator('tags')
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate that tags are not empty or whitespace-only."""
        if not v:
            return ["default"]  # Default tag if empty
            
        for tag in v:
            if not tag or tag.isspace():
                raise ValueError("Tags must contain non-whitespace strings")
        return v
    
    @model_validator(mode='after')
    def validate_chords_not_empty(self) -> 'ChordProgression':
        """Validate that chords is not empty."""
        if not self.chords:
            raise ValueError("Chord progression cannot be empty")
        
        # Ensure we have an id
        if not self.id:
            self.id = str(uuid.uuid4())
            
        return self
    
    @property
    def total_duration(self) -> float:
        """Calculate the total duration of the chord progression."""
        return sum(chord.duration or 4.0 for chord in self.chords)
    
    @classmethod
    def from_chord_progression_pattern(cls, pattern: ChordProgressionPattern, key: str, scale_type: str, 
                                      description: str = "", tags: Optional[list[str]] = None) -> 'ChordProgression':
        """
        Create a chord progression from a ChordProgressionPattern and a key/scale.
        
        Args:
            pattern: The ChordProgressionPattern to use
            key: The key to use (e.g., "C", "G", "Am")
            scale_type: The scale type to use (e.g., "MAJOR", "MINOR", "HARMONIC_MINOR")
            description: Optional description
            tags: Optional tags
            
        Returns:
            A new ChordProgression instance
        """
        from src.note_gen.models.scale import Scale
        from src.note_gen.models.note import Note
        from src.note_gen.models.chord import Chord
        
        # Create a Scale object for the given key and scale type
        scale = Scale(root=key, scale_type=scale_type)
        
        # Create chords based on the pattern and scale
        chords = []
        for item in pattern.pattern:
            # Get the scale degree and chord quality
            degree = item.degree
            quality = item.quality
            
            # Get the root note of the chord
            root_note = scale.get_note_by_degree(int(degree) if isinstance(degree, (int, str)) else 0)
            
            # Create a Chord object
            chord = Chord(root=root_note, quality=quality, duration=item.duration)
            
            # Add the chord to the list
            chords.append(chord)
        
        # Create the ChordProgression object
        return cls(
            name=pattern.name,
            description=description,
            tags=tags or ["default"],
            complexity=pattern.complexity,
            genre=pattern.genre,
            chords=chords
        )

class RhythmNote(BaseModel):
    """
    Represents a single note in a rhythm pattern.
    
    IMPORTANT: In musical notation, negative values represent rests.
    Throughout this class and related models, we follow this convention:
    - Positive durations represent regular notes
    - Negative durations represent rests, with the absolute value as the duration
    - Zero durations are not allowed and will raise a ValueError during validation
    """
    position: float = Field(..., ge=0.0, description="Position (start time) of the note in beats")
    duration: float = Field(..., description="Duration of the note in beats")
    velocity: Optional[int] = Field(100, ge=0, le=127, description="Velocity (0-127, where 0 is valid for rests)")
    is_rest: Optional[bool] = Field(None, description="Whether this is a rest note")
    accent: Optional[Union[str, float, int]] = Field(None, description="Accent level")
    swing_ratio: float = Field(
        default=0.67,
        ge=0.5,
        le=0.75,
        description='Swing ratio between 0.5 and 0.75. Default is 0.67.'
    )
    
    model_config = ConfigDict(
        validate_assignment=False  # Disable validation during assignment to avoid recursion
    )
    
    @classmethod
    @field_validator('duration')
    def validate_duration(cls, v: float) -> float:
        """
        Validate that duration is not zero.
        
        Negative durations are allowed as they represent rests.
        """
        if v == 0:
            raise ValueError("Duration cannot be zero. Use positive values for notes and negative values for rests.")
        return v
    
    @model_validator(mode='after')
    def post_process(self) -> 'RhythmNote':
        """
        Post-process the note after initialization.
        
        If duration is negative, mark as rest.
        """
        # Store current values
        duration = self.duration
        is_rest = self.is_rest
        
        # Process values without triggering recursion
        is_rest_value = True if duration < 0 else (False if is_rest is None else is_rest)
        
        # Create a new object with the processed values to avoid validation recursion
        object.__setattr__(self, 'is_rest', is_rest_value)
        
        return self

class RhythmPatternData(BaseModel):
    """
    Detailed data for a rhythm pattern.
    
    IMPORTANT: In musical notation, negative values represent rests.
    Throughout this class and related models, we follow this convention:
    - Positive durations represent regular notes
    - Negative durations represent rests, with the absolute value as the duration
    - Zero durations are not allowed and will raise a ValueError during validation
    """
    notes: List[RhythmNote]
    time_signature: str
    default_duration: float
    groove_type: Literal['straight', 'swing', 'shuffle']
    style: str
    duration: float
    variation_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    total_duration: float = Field(default=0.0, description="Total duration of the pattern")
    swing_ratio: float = Field(default=0.67, ge=0.5, le=0.75, description='Swing ratio between 0.5 and 0.75. Default is 0.67.')
    humanize_amount: float = Field(default=0.1, ge=0.0, le=1.0, description='Humanize amount between 0.0 and 1.0. Default is 0.1.')

    @model_validator(mode='before')
    def validate_notes(cls, values):
        if not values.get('notes'):
            raise ValueError('List should have at least 1 item after validation')
        return values

    @field_validator('groove_type')
    def validate_groove_type(cls, v: str) -> str:
        if v not in ['straight', 'swing', 'shuffle']:
            raise ValueError('Invalid groove type. Must be one of: straight, swing, shuffle')
        return v

    @field_validator('total_duration')
    def validate_total_duration(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Total duration must be greater than 0')
        return v

    @field_validator('swing_ratio')
    def validate_swing_ratio(cls, v: float) -> float:
        if not 0.5 <= v <= 0.75:
            raise ValueError('Swing ratio must be between 0.5 and 0.75')
        return v

    @field_validator('humanize_amount')
    def validate_humanize_amount(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('Humanize amount must be between 0.0 and 1.0')
        return v

    def get_pattern_duration(self) -> float:
        return sum(note.duration for note in self.notes)

class RhythmPattern(BaseModel):
    """
    A pattern of rhythm information.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1)
    data: RhythmPatternData
    pattern: Union[List[float], str] = Field(..., description='List of rhythm values or space-separated string')
    complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    style: str = Field(default="jazz", description='Musical style of the pattern')
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        validate_assignment=True,
        extra='allow',  # Allow extra fields for test compatibility
        arbitrary_types_allowed=True
    )

    @classmethod
    @field_validator('pattern', mode='before')
    def validate_pattern(cls, v: Union[List[float], str]) -> Union[List[float], str]:
        if isinstance(v, str):
            try:
                # Convert space-separated string to list of floats
                pattern_values = [float(val) for val in v.split()]
                if not pattern_values:
                    raise ValueError('Pattern cannot be empty')
                return v  # Return original string to maintain format
            except ValueError:
                raise ValueError('Pattern must contain only numbers separated by spaces')
        elif isinstance(v, list):
            if not v:
                raise ValueError('Pattern cannot be empty')
            return v
        else:
            raise ValueError('Pattern must be a list of numbers or a space-separated string of numbers')

    @classmethod
    @field_validator('style')
    def validate_style(cls, v: str) -> str:
        allowed_styles = ['rock', 'jazz', 'pop', 'classical']
        if v not in allowed_styles:
            raise ValueError(f'Style must be one of: {allowed_styles}')
        return v

    @model_validator(mode='after')
    def validate_rhythm_pattern(self) -> 'RhythmPattern':
        """Final validation of the complete rhythm pattern."""
        if not self.name:
            raise ValueError('Name is required')
        if not self.data:
            raise ValueError('Data is required')
        if not self.pattern:
            raise ValueError('Pattern is required')
        return self

    def get_pattern_duration(self) -> float:
        """Calculate the total duration of the pattern."""
        if hasattr(self.data, 'total_duration') and self.data.total_duration is not None:
            return float(self.data.total_duration)
        elif hasattr(self.data, 'duration') and self.data.duration is not None:
            return float(self.data.duration)
        return 0.0
    
    def get_events_in_range(self, start_time: float, end_time: float) -> list[RhythmNote]:
        """
        Get all rhythm events within a specific time range.
        
        Args:
            start_time: Start time in beats
            end_time: End time in beats
            
        Returns:
            List of rhythm note events within the range as RhythmNote objects
        """
        events: List[RhythmNote] = []
        
        if not hasattr(self.data, 'notes'):
            return events
            
        for note in self.data.notes:
            if hasattr(note, 'position') and hasattr(note, 'duration'):
                if float(note.position) + float(note.duration) > start_time and float(note.position) < end_time:
                    events.append(note)
                
        return events

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'data': self.data,
            'complexity': self.complexity,
            'style': self.style,
            'pattern': self.pattern
        }
        
        # Add optional fields if they exist
        if hasattr(self, 'description'):
            result['description'] = self.description
        if hasattr(self.data, 'swing_enabled'):
            result['swing_enabled'] = self.data.swing_enabled
        if hasattr(self.data, 'swing_ratio'):
            result['swing_ratio'] = self.data.swing_ratio
        if hasattr(self.data, 'duration'):
            result['duration'] = self.data.duration
            
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the pattern's dictionary representation."""
        return self.model_dump().get(key, default)

    @classmethod
    @field_validator('accent_pattern')
    def validate_accent_pattern(cls, v: list[Union[str, int, float]]) -> list[float]:
        if not v:
            return []
        try:
            return [float(x) for x in v]
        except (ValueError, TypeError):
            raise ValueError('Accent pattern must contain valid numbers')
    
    @model_validator(mode='after')
    def validate_required_fields(self) -> 'RhythmPattern':
        if not self.name:
            raise ValueError('Name is required')
        if not self.pattern:
            raise ValueError('Pattern is required')
        return self

    @classmethod
    @field_validator('pattern')
    def validate_pattern(cls, v: str) -> str:
        """Validate the rhythm pattern format.
        
        Args:
            v: The pattern string to validate
            
        Returns:
            The validated pattern string
            
        Raises:
            ValueError: If the pattern is empty, not a string, or contains invalid characters
        """
        if not isinstance(v, str):
            raise ValueError('Pattern must be a string')
        if not v.strip():
            raise ValueError('Pattern cannot be empty')
        if not re.match(r'^[\d\s]+$', v):
            raise ValueError('Pattern must contain only numbers separated by spaces')
        return v

class Patterns(BaseModel):
    """Container class for all pattern types"""
    COMMON_PROGRESSIONS: ClassVar[Dict[str, List[str]]] = {
        "I-IV-V": ["I", "IV", "V"],
        "I-vi-IV-V": ["I", "vi", "IV", "V"],
        "ii-V-I": ["ii", "V", "I"],
        "I-V-vi-IV": ["I", "V", "vi", "IV"],
        "I-vi-ii-V": ["I", "vi", "ii", "V"]
    }
    note_patterns: Dict[str, NotePattern] = Field(
        default_factory=lambda: {k: NotePattern(name=k, intervals=v.get('intervals', []), data=NotePatternData(**{key: val for key, val in v.items() if key != 'intervals'})) 
                                if isinstance(v, dict) else v 
                                for k, v in NOTE_PATTERNS.items()},
        description='Note pattern configurations'
    )
    chord_progression_patterns: Dict[str, ChordProgressionPattern] = Field(
        default_factory=dict,
        description='Chord progression pattern configurations'
    )
    rhythm_patterns: Dict[str, RhythmPattern] = Field(
        default_factory=lambda: {
            name: RhythmPattern(name=name, **pattern) 
            for name, pattern in RHYTHM_PATTERNS.items()
        },
        description='Rhythm pattern configurations'
    )
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    @model_validator(mode='after')
    def validate_patterns(self) -> 'Patterns':
        """Ensure all patterns are properly initialized."""
        # Create new dictionaries to hold the converted patterns
        new_note_patterns: Dict[str, NotePattern] = {}
        new_rhythm_patterns: Dict[str, RhythmPattern] = {}
        
        # Convert any raw note pattern data to NotePattern objects
        for name, pattern in self.note_patterns.items():
            if isinstance(pattern, dict):
                try:
                    pattern_data = dict(pattern)  # Create a new dictionary to avoid modifying the original
                    pattern_list = pattern_data.pop('intervals', []) if 'intervals' in pattern_data else []
                    new_pattern = NotePattern(
                        name=name,
                        intervals=pattern_list,
                        data=NotePatternData(**pattern_data)
                    )
                    new_note_patterns[name] = new_pattern
                except Exception:
                    # If conversion fails, create a new NotePattern with minimal data
                    new_note_patterns[name] = NotePattern(name=name, intervals=[])
            else:
                new_note_patterns[name] = pattern

        # Convert any raw rhythm pattern data to RhythmPattern objects
        for name, pattern in self.rhythm_patterns.items():
            if isinstance(pattern, dict):
                try:
                    pattern_data = dict(pattern)  # Create a new dictionary to avoid modifying the original
                    pattern_list = pattern_data.pop('pattern', [1.0]) if 'pattern' in pattern_data else [1.0]
                    new_pattern = RhythmPattern(
                        name=name,
                        pattern=pattern_list,
                        data=RhythmPatternData(**pattern_data)
                    )
                    new_rhythm_patterns[name] = new_pattern
                except Exception:
                    # If conversion fails, create a new RhythmPattern with minimal data
                    new_rhythm_patterns[name] = RhythmPattern(
                        name=name, 
                        pattern=[1.0], 
                        data=RhythmPatternData(time_signature="4/4", default_duration=1.0, groove_type="straight")
                    )
            else:
                new_rhythm_patterns[name] = pattern
                
        # Replace the original dictionaries with the new ones
        self.note_patterns = new_note_patterns
        self.rhythm_patterns = new_rhythm_patterns

        return self

    def get_note_pattern(self, name: str) -> Optional[NotePattern]:
        """Get a note pattern by name."""
        return self.note_patterns.get(name)

    def get_rhythm_pattern(self, name: str) -> Optional[RhythmPattern]:
        """Get a rhythm pattern by name."""
        return self.rhythm_patterns.get(name)

    def get_chord_progression_pattern(self, name: str) -> Optional[ChordProgressionPattern]:
        """Get a chord progression pattern by name."""
        return self.chord_progression_patterns.get(name)