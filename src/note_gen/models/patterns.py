from typing import Any, List, Optional, Dict, Union, Tuple
from pydantic import BaseModel, Field, model_validator, root_validator, ConfigDict, field_validator, PrivateAttr, ValidationInfo
from src.note_gen.models.note import Note
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.chord import Chord, ChordQuality
import uuid
import logging
import re

logger = logging.getLogger(__name__)

NoteType = Union[Note, ScaleDegree]

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
        'pattern': [0, 4, 7],  # Root, major third, perfect fifth
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
        'pattern': [0, 3, 7],  # Root, minor third, perfect fifth
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
    notes: list[Union[str, dict[str, Any], Note, int, float]] = Field(default_factory=list, description="Optional list of notes in the pattern. Can be empty if intervals are provided.")
    intervals: list[int] = Field(default_factory=list, description="List of intervals that define the pattern. This is the primary way to define note patterns.")
    duration: Optional[Union[int, float]] = Field(default=1.0, gt=0, description="Duration of the pattern in beats")
    position: Optional[Union[int, float]] = Field(default=0.0, ge=0, description="Position of the pattern in beats")
    velocity: Optional[int] = Field(default=100, ge=0, le=127, description="Velocity of the pattern (0-127)")
    direction: Optional[str] = Field(default="up", description="Direction of the pattern (up, down, random)")
    use_chord_tones: Optional[bool] = Field(default=False, description="Use chord tones")
    use_scale_mode: Optional[bool] = Field(default=False, description="Use scale mode")
    arpeggio_mode: Optional[bool] = Field(default=False, description="Use arpeggio mode")
    restart_on_chord: Optional[bool] = Field(default=False, description="Restart pattern on each chord")
    octave_range: Optional[tuple[int, int]] = Field(default_factory=lambda: (4, 5), description="Range of octaves to use")
    default_duration: Optional[Union[int, float]] = Field(default=1.0, gt=0, description="Default duration for notes in the pattern")

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
    def _convert_interval(interval: Union[str, dict[str, Any], int, float]) -> Union[str, dict[str, Any], int, float]:
        if isinstance(interval, str):
            return interval
        elif isinstance(interval, dict):
            return interval
        elif isinstance(interval, (int, float)):
            return float(interval)
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

    @model_validator(mode='after')
    def validate_structure(self) -> 'NotePatternData':
        """Ensure at least one of notes or intervals is present, with intervals taking precedence."""
        if not self.notes and not self.intervals:
            raise ValueError("Either notes or intervals must be provided")

        # If both are present, intervals take precedence
        if self.intervals and self.notes:
            self.notes = []  # Clear notes if intervals are present

        return self

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary with proper handling of Note objects."""
        data = super().model_dump(**kwargs)
        
        # Convert Note objects to dictionaries
        if data.get('notes'):
            data['notes'] = [
                note.model_dump() if hasattr(note, 'model_dump') else note 
                for note in data['notes']
            ]
            
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
    notes: Optional[List[Note]] = Field(default=None, description="List of notes in the pattern")
    data: Optional[Union[NotePatternData, Dict[str, Any]]] = Field(default=None, description="Additional pattern data")
    style: Optional[str] = Field(default=None, description="Pattern style")
    is_test: Optional[bool] = Field(default=False, description="Test flag")
    pattern: Optional[list[Union[int, str]]] = Field(default_factory=list, description="Pattern intervals. Can include any integer values, including large intervals for octave jumps.")
    direction: Optional[str] = Field(default=None, description="Direction for compatibility")
    use_chord_tones: Optional[bool] = Field(default=None, description="Use chord tones for compatibility")
    use_scale_mode: Optional[bool] = Field(default=None, description="Use scale mode for compatibility")
    arpeggio_mode: Optional[bool] = Field(default=None, description="Arpeggio mode for compatibility")
    restart_on_chord: Optional[bool] = Field(default=None, description="Restart on chord for compatibility")
    duration: Optional[float] = Field(default=None, description="Duration for compatibility")
    position: Optional[float] = Field(default=None, description="Position for compatibility")
    velocity: Optional[int] = Field(default=None, ge=0, le=127, description="Velocity for compatibility")
    
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
    @field_validator('pattern')
    def validate_pattern(cls, v: str) -> str:
        if not v:
            raise ValueError('pattern field is required')
        if not isinstance(v, str):
            raise ValueError('Pattern must be a string')
        try:
            pattern_values = [int(float(val)) for val in v.split()]
            if not pattern_values:
                raise ValueError('Pattern cannot be empty')
            return ' '.join(map(str, pattern_values))
        except ValueError as exc:
            raise ValueError('Pattern must contain only numbers separated by spaces') from exc

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

        # Ensure pattern is not None
        if self.pattern is None:
            self.pattern = []

        # Copy compatible fields from data to top level if they exist
        if self.direction is None and hasattr(self.data, 'direction'):
            self.direction = self.data.direction
        if self.use_chord_tones is None and hasattr(self.data, 'use_chord_tones'):
            self.use_chord_tones = self.data.use_chord_tones
        if self.use_scale_mode is None and hasattr(self.data, 'use_scale_mode'):
            self.use_scale_mode = self.data.use_scale_mode
        if self.arpeggio_mode is None and hasattr(self.data, 'arpeggio_mode'):
            self.arpeggio_mode = self.data.arpeggio_mode
        if self.restart_on_chord is None and hasattr(self.data, 'restart_on_chord'):
            self.restart_on_chord = self.data.restart_on_chord
        if self.duration is None and hasattr(self.data, 'duration'):
            self.duration = self.data.duration
        if self.position is None and hasattr(self.data, 'position'):
            self.position = self.data.position
        if self.velocity is None and hasattr(self.data, 'velocity'):
            self.velocity = self.data.velocity

        return self

    def total_duration(self) -> float:
        """Calculate the total duration of the pattern."""
        if not self.data or not self.data.notes:
            return 0.0
        return sum(note.duration for note in self.data.notes)

    def get_notes(self) -> List[Note]:
        """Get the list of notes in the pattern."""
        if self.notes is None:
            self.notes = []
        return self.notes

    def add_note(self, note: Note) -> None:
        """Add a note to the pattern."""
        if self.notes is None:
            self.notes = []
        self.notes.append(note)

    def remove_note(self, index: int) -> None:
        """Remove a note from the pattern."""
        if self.notes and 0 <= index < len(self.notes):
            self.notes.pop(index)

    def clear_notes(self) -> None:
        """Clear all notes from the pattern."""
        self.notes = []

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Enhanced model_dump to ensure data is properly serialized."""
        data = super().model_dump(**kwargs)
        
        # Convert Note objects to dictionaries
        if data.get('notes'):
            data['notes'] = [
                note.model_dump() if hasattr(note, 'model_dump') else note 
                for note in data['notes']
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
    quality: ChordQuality = Field(
        default=ChordQuality.MAJOR,
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
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="allow"
    )
    
    @classmethod
    @field_validator('degree')
    def validate_degree(cls, v: Union[int, str]) -> Union[int, str]:
        """Convert Roman numerals to integers and validate range."""
        if isinstance(v, str):
            # Handle Roman numerals
            v = v.strip()  # Keep original case for quality determination
            roman_map = {
                'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
                'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7
            }
            try:
                # Keep the original string to preserve case information
                if v in roman_map:
                    return v
                raise ValueError(f"Invalid Roman numeral: {v}")
            except KeyError:
                raise ValueError(f"Invalid Roman numeral: {v}")
        elif isinstance(v, int):
            if not 1 <= v <= 7:
                raise ValueError("Scale degree must be between 1 and 7")
            return v
        else:
            raise ValueError("Degree must be a Roman numeral string or integer")

    @classmethod
    @field_validator('quality', mode='before')
    def validate_quality(cls, v: Union[ChordQuality, dict[str, Any]]) -> dict[str, Any]:
        if isinstance(v, ChordQuality):
            return {
                'name': v.name,
                'symbol': v.value,
                'intervals': v.intervals,
                'description': v.description
            }
        return v

    @classmethod
    @field_validator('quality')
    def validate_quality(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize chord quality."""
        if isinstance(v, dict):
            v = v.copy()
            try:
                v['name'] = v['name'].upper().strip()
                if v['name'] not in [q.name for q in ChordQuality]:
                    raise ValueError(f"Invalid chord quality: {v['name']}. Must be one of {[q.name for q in ChordQuality]}")
            except KeyError:
                raise ValueError("Quality dictionary must contain 'name' key")
            return v
        
        raise ValueError("Quality must be a string or ChordQuality enum")

    @model_validator(mode='after')
    def validate_chord_pattern_item(self) -> 'ChordPatternItem':
        """Validate the complete chord pattern item and infer quality from numeral case if needed."""
        if self.duration <= 0:
            raise ValueError("Duration must be greater than 0")
            
        # If degree is a Roman numeral, infer quality from case if not explicitly set
        if isinstance(self.degree, str) and self.quality == ChordQuality.MAJOR:
            is_minor = self.degree.islower()
            if is_minor:
                self.quality = ChordQuality.MINOR
                
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
        """Validate that pattern is not empty."""
        if not self.pattern:
            raise ValueError("Pattern cannot be empty")
        return self

    def roman_numerals(self) -> list[str]:
        """Get the chord progression as Roman numerals."""
        roman_map = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'}
        return [roman_map[item.degree] for item in self.pattern]

    def total_duration(self) -> float:
        """Calculate the total duration of the chord progression pattern."""
        return sum(item.duration for item in self.pattern)

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
        if not qualities:
            qualities = [ChordQuality.MAJOR] * len(degrees)
        if not durations:
            durations = [4.0] * len(degrees)
        
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
        if not durations:
            durations = [4.0] * len(numerals)
        
        if len(durations) != len(numerals):
            raise ValueError("Number of durations must match number of numerals")
            
        if qualities and len(qualities) != len(numerals):
            raise ValueError("Number of qualities must match number of numerals")
        
        # Create pattern items directly using ChordPatternItem validation
        pattern = []
        for i, numeral in enumerate(numerals):
            quality = qualities[i] if qualities else None
            pattern_item = ChordPatternItem(
                degree=numeral,  # ChordPatternItem will handle validation
                quality=quality if quality else ChordQuality.MAJOR,  # Will be updated based on case if needed
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
    def from_chord_progression(cls, progression, name: Optional[str] = None,
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
            
        pattern = []
        for chord in progression.chords:
            pattern.append(ChordPatternItem(
                degree=chord.scale_degree,
                quality=chord.quality,
                duration=chord.duration,
                inversion=chord.inversion
            ))
            
        return cls(
            name=name,
            description=description,
            tags=tags or progression.tags,
            complexity=progression.complexity,
            genre=progression.genre,
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
            root_note = scale.get_note_at_degree(degree)
            
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
    time_signature: str = Field(default='4/4', description='Time signature of the rhythm pattern')
    default_duration: float = Field(default=1.0, gt=0, description='Default duration in beats')
    groove_type: str = Field(default='straight', description='Type of groove')
    swing_enabled: bool = Field(default=False, description='Whether swing rhythm is enabled')
    swing_ratio: float = Field(
        default=0.67,
        ge=0.5,
        le=0.75,
        description='Swing ratio between 0.5 and 0.75. Default is 0.67 regardless of swing_enabled.'
    )
    notes: Optional[list[RhythmNote]] = Field(default_factory=list, description='List of rhythm notes')
    total_duration: Optional[float] = Field(default=4.0, gt=0, description='Total duration of the pattern in beats')
    accent_pattern: list[Union[str, int, float]] = Field(default_factory=list, description='Pattern of accent velocities')
    humanize_amount: float = Field(default=0.0, ge=0.0, le=1.0, description='Amount of humanization to apply (0.0-1.0)')
    variation_probability: float = Field(default=0.0, ge=0.0, le=1.0, description='Probability of variation (0.0-1.0)')
    complexity: Optional[float] = Field(default=None, ge=0.0, description='Complexity rating')
    style: str = Field(default="basic", description='Style of the rhythm pattern')
    duration: float = Field(default=1.0, gt=0, description='Duration of the pattern in beats')

    @classmethod
    @field_validator('time_signature')
    def validate_time_signature(cls, v: str) -> str:
        if not re.match(r'^\d+/\d+$', v):
            raise ValueError('Invalid time signature format')
        numerator, denominator = map(int, v.split('/'))
        if numerator <= 0 or denominator <= 0:
            raise ValueError('Numerator and denominator must be positive')
        return v

    @classmethod
    @field_validator('groove_type')
    def validate_groove_type(cls, v: str) -> str:
        if v not in ['straight', 'swing']:
            raise ValueError('Invalid groove type')
        return v

    @classmethod
    @field_validator('pattern')
    def validate_pattern(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError('Pattern must be a string')
        if not v.strip():
            raise ValueError('Pattern cannot be empty')
        if not re.match(r'^[\d\s]+$', v):
            raise ValueError('Pattern must contain only numbers separated by spaces')
        return v

    @model_validator(mode='after')
    def validate_swing_settings(self) -> 'RhythmPatternData':
        """Validate swing settings.
        
        The swing_ratio is always allowed and defaults to 0.67 regardless of swing_enabled.
        This allows patterns to maintain a consistent swing_ratio value even when
        swing is disabled, making it easier to toggle swing on/off without losing the ratio setting.
        """
        if not (0.5 <= self.swing_ratio <= 0.75):
            raise ValueError('Swing ratio must be between 0.5 and 0.75')
        return self

    @classmethod
    @field_validator('accent_pattern')
    def validate_accent_pattern(cls, v: list) -> list:
        if not isinstance(v, list):
            raise ValueError('Accent pattern must be a list')
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError('Accent pattern must contain only numbers')
        return v

    @model_validator(mode='after')
    def validate_note_durations(self) -> 'RhythmPatternData':
        """Check that notes don't have zero durations."""
        for note in self.notes:
            if note.duration == 0:
                raise ValueError('Duration cannot be zero. Use positive values for notes and negative values for rests.')
        return self

    @model_validator(mode='after')
    def validate_duration(self) -> 'RhythmPatternData':
        """Check that duration is greater than zero."""
        if self.duration <= 0:
            raise ValueError('Duration must be greater than zero')
        return self

    def calculate_total_duration(self, default_duration: Optional[float] = None) -> float:
        """Calculate and update total duration based on the position and duration of notes."""
        # Initialize with either the field value or the passed default
        if hasattr(self, 'total_duration') and self.total_duration is not None:
            return self.total_duration
            
        # If pattern is empty, return 0.0
        if not self.pattern:
            return 0.0
            
        # For each item in the pattern, sum the absolute values
        # This handles negative durations (rests)
        total = 0.0
        for duration in self.pattern:
            # Ensure we're working with a float
            if isinstance(duration, str):
                try:
                    # Check if it can be converted to a valid float
                    duration = float(duration)
                except (ValueError, TypeError):
                    # Skip invalid values
                    continue
            # Only add to total if it's a number
            if isinstance(duration, (int, float)):
                total += abs(float(duration))
                
        # Return the calculated total duration
        return total

class RhythmPattern(BaseModel):
    """
    A pattern of rhythm information.
    """
    id: Optional[str] = Field(None, description="ID of the rhythm pattern")
    name: str = Field(..., min_length=1, description="Name of the rhythm pattern")
    description: str = Field(default="", description="Pattern description")
    tags: list[str] = Field(default_factory=lambda: ["default"], description="Pattern tags")
    data: Optional[Union[RhythmPatternData, Dict[str, Any]]] = Field(
        default=None,
        description="Rhythm pattern data. Can be either a RhythmPatternData object or raw dictionary"
    )
    complexity: float | None = Field(default=1.0, ge=0.0, le=5.0, description="Pattern complexity rating from 0 to 5")
    style: Optional[str] = Field(default=None, description="Style of the rhythm pattern")
    pattern: Union[list[float], str] = Field(..., description="Pattern of note durations")
    swing_enabled: bool = Field(default=False, description='Whether swing rhythm is enabled')
    swing_ratio: float = Field(
        default=0.67,
        ge=0.5,
        le=0.75,
        description='Swing ratio between 0.5 and 0.75. Default is 0.67 regardless of swing_enabled.'
    )
    duration: Optional[float] = Field(default=1.0, gt=0, description="Duration in beats")
    is_test: Optional[bool] = Field(default=None, description="Test flag")
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )
    
    @model_validator(mode='before')
    @classmethod
    def normalize_data_field(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure data field is properly converted to RhythmPatternData"""
        if isinstance(values, dict):
            data = values.get('data')
            if isinstance(data, dict):
                # Ensure swing settings are consistent
                if 'swing_ratio' not in data:
                    data['swing_ratio'] = values.get('swing_ratio', 0.67)
                if 'swing_enabled' not in data:
                    data['swing_enabled'] = values.get('swing_enabled', False)
                values['data'] = RhythmPatternData(**data)
        return values

    @classmethod
    @field_validator('pattern')
    def validate_pattern(cls, v):
        if not v:
            raise ValueError('Pattern cannot be empty')
        if not isinstance(v, str):
            raise ValueError('Pattern must be a string')
        try:
            pattern_values = [int(float(val)) for val in v.split()]
            if not pattern_values:
                raise ValueError('Pattern cannot be empty')
            return ' '.join(map(str, pattern_values))
        except ValueError:
            raise ValueError('Invalid pattern format')

    @model_validator(mode='after')
    def validate_rhythm_pattern(self) -> 'RhythmPattern':
        """Final validation of the complete rhythm pattern."""
        # Validate swing ratio range
        if not (0.5 <= self.swing_ratio <= 0.75):
            raise ValueError('Swing ratio must be between 0.5 and 0.75')
            
        # Validate complexity
        if self.complexity is not None and not (0.0 <= self.complexity <= 5.0):
            raise ValueError('Complexity must be between 0 and 5')
            
        # Validate duration
        if self.duration is not None and self.duration <= 0:
            raise ValueError('Duration must be greater than zero')
            
        return self
    
    def get_pattern_duration(self) -> float:
        """Calculate the total duration of the pattern."""
        return self.data.total_duration
    
    def get_events_in_range(self, start_time: float, end_time: float) -> list[RhythmNote]:
        """
        Get all rhythm events within a specific time range.
        
        Args:
            start_time: Start time in beats
            end_time: End time in beats
            
        Returns:
            List of rhythm note events within the range as RhythmNote objects
        """
        events = []
        
        for note in self.data.notes:
            if note.position + note.duration > start_time and note.position < end_time:
                events.append(note)
                
        return events

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
            'data': self.data,
            'complexity': self.complexity,
            'style': self.style,
            'pattern': self.pattern,
            'swing_enabled': self.swing_enabled,
            'swing_ratio': self.swing_ratio,
            'duration': self.duration
        }

    def get(self, key: str, default=None):
        """Get a value from the pattern's dictionary representation."""
        return self.model_dump().get(key, default)

    @classmethod
    @field_validator('accent_pattern')
    def validate_accent_pattern(cls, v: list) -> list:
        if not isinstance(v, list):
            raise ValueError('Accent pattern must be a list')
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError('Accent pattern must contain only numbers')
        return v

    @classmethod
    @field_validator('pattern')
    def validate_pattern(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError('Pattern must be a string')
        if not v.strip():
            raise ValueError('Pattern cannot be empty')
        if not re.match(r'^[\d\s]+$', v):
            raise ValueError('Pattern must contain only numbers separated by spaces')
        return v

    @model_validator(mode='after')
    def validate_required_fields(self) -> 'RhythmPattern':
        if not self.name:
            raise ValueError('Name is required')
        if not self.pattern:
            raise ValueError('Pattern is required')
        return self

class Patterns(BaseModel):
    """Container class for all pattern types"""
    note_patterns: Dict[str, NotePattern] = Field(
        default_factory=lambda: dict(NOTE_PATTERNS),
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
    COMMON_PROGRESSIONS: list[list[str]] = Field(
        default_factory=lambda: [
            # Major progressions
            ['I', 'IV', 'V', 'I'],
            ['I', 'vi', 'IV', 'V'],
            ['I', 'V', 'vi', 'IV'],
            # Minor progressions
            ['i', 'iv', 'v', 'i'],
            ['i', 'VI', 'iv', 'v'],
            ['i', 'v', 'VI', 'iv'],
        ],
        description='Common chord progressions'
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    @model_validator(mode='after')
    def validate_patterns(self) -> 'Patterns':
        """Ensure all patterns are properly initialized."""
        # Convert any raw note pattern data to NotePattern objects
        for name, pattern in self.note_patterns.items():
            if isinstance(pattern, dict):
                self.note_patterns[name] = NotePattern(
                    name=name,
                    pattern=pattern.get('pattern', []),
                    data=NotePatternData(**pattern)
                )

        # Convert any raw rhythm pattern data to RhythmPattern objects
        for name, pattern in self.rhythm_patterns.items():
            if isinstance(pattern, dict):
                self.rhythm_patterns[name] = RhythmPattern(
                    name=name,
                    pattern=pattern.get('pattern', [1.0]),  # Default pattern
                    data=RhythmPatternData(**pattern)
                )

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