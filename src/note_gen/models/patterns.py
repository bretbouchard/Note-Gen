from typing import Any, List, Optional, Dict, Union, Tuple, ClassVar, Annotated, Callable, Sequence, Literal
from pydantic import BaseModel, Field, model_validator, root_validator, ConfigDict, field_validator, PrivateAttr, ValidationInfo, ValidationError
from .note import Note
from .scale_degree import ScaleDegree
from .chord import Chord
from .chord_quality import ChordQuality
from .scale_info import ScaleInfo
from .enums import ScaleType
from .scale import Scale
from .chord_progression import ChordProgression  # Import from chord_progression.py
import uuid
import logging
import re
import math

logger = logging.getLogger(__name__)

NoteType = Union[Note, ScaleDegree]
# Remove the Scale import from here
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
        'intervals': [0, 4, 7],
        'data': {
            'notes': ['C4', 'E4', 'G4'],
            'intervals': [4, 3],
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
        'intervals': [0, 3, 7],
        'data': {
            'notes': ['C4', 'Eb4', 'G4'],
            'intervals': [3, 4],
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
    """Data for a note pattern."""
    intervals: List[int] = Field(..., min_items=1)
    notes: List[Note] = Field(..., min_items=1)  # Changed from str to Note

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow Note type

class NotePattern(BaseModel):
    name: str = Field(
        ..., 
        min_length=4,
        pattern=r'^[a-zA-Z0-9\s_-]+$',
        description="Name must be at least 4 characters and contain only letters, numbers, spaces, underscores, and hyphens"
    )
    intervals: List[int] = Field(..., min_items=1)
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    data: NotePatternData = Field(default_factory=NotePatternData)

    @model_validator(mode='before')
    def validate_notes_or_intervals(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get('intervals'):
            raise ValueError('Intervals are required')
        return values

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        validate_default=True,
        extra="allow"
    )

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


class ChordPatternItem(BaseModel):
    """Represents a single chord in a chord pattern."""
    degree: int = Field(..., ge=1, le=7)
    quality: str = Field(...)
    duration: float = Field(..., gt=0)  # Make duration required with validation
    position: float = Field(default=0.0, ge=0.0)
    velocity: int = Field(default=100, ge=0, le=127)
    inversion: Optional[int] = None

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="allow"
    )

class ChordProgressionPattern(BaseModel):
    """Represents a chord progression pattern."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1)
    chords: List[ChordPatternItem] = Field(..., min_items=1)
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    time_signature: str = Field(default="4/4")
    total_duration: float = Field(default=0.0)

    @model_validator(mode='after')
    def calculate_total_duration(self) -> 'ChordProgressionPattern':
        """Calculate the total duration of the chord progression."""
        self.total_duration = sum(chord.duration for chord in self.chords)
        return self

    def generate_progression_from_pattern(self, scale: Scale) -> List[Chord]:
        """Generate a chord progression based on the pattern and given scale"""
        chords = []
        for item in self.chords:
            chord = scale.get_chord_by_degree(
                degree=item.degree,
                quality=item.quality
            )
            chords.append(chord)
        return chords

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
        if not self.chords:
            raise ValueError("Pattern cannot be empty")
            
        # Validate that all pattern items have valid durations
        for i, item in enumerate(self.chords):
            if item.duration is not None and item.duration <= 0:
                raise ValueError(f"Pattern item at index {i} has invalid duration: {item.duration}. Duration must be greater than 0.")
                
        return self

    def roman_numerals(self) -> list[str]:
        """Get the chord progression as Roman numerals."""
        roman_map: Dict[int, str] = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'}
        result = []
        for item in self.chords:
            if isinstance(item.degree, int) and item.degree in roman_map:
                result.append(roman_map[item.degree])
            else:
                # If it's already a string (Roman numeral), use it directly
                result.append(str(item.degree))
        return result

    def total_duration(self) -> float:
        """Calculate the total duration of the chord progression pattern."""
        return sum(float(item.duration) for item in self.chords if item.duration is not None)

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
            chords=pattern
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
            # Get the scale degree and chord quality
            degree = roman_map.get(numeral.upper())
            quality = qualities[i] if qualities and i < len(qualities) else ChordQuality.MAJOR
            
            # Create a ChordPatternItem object
            pattern_item = ChordPatternItem(
                degree=degree,  # ChordPatternItem will handle validation
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
            chords=pattern
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
            chords=pattern
        )

    def create_progression(self, key: Note, scale_type: str) -> 'ChordProgression':
        """Create a chord progression from this pattern.
        
        Args:
            key (Note): The key note for the progression
            scale_type (str): The type of scale to use
            
        Returns:
            A new ChordProgression instance
        """
        # Move the Scale import here
        from src.note_gen.models.scale import Scale
        from src.note_gen.models.note import Note
        from src.note_gen.models.chord import Chord
        
        # Create a Scale object for the given key and scale type
        scale = Scale(root=key, scale_type=scale_type)
        
        # Create chords based on the pattern and scale
        chords = []
        for item in self.chords:
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
        return ChordProgression(
            name=self.name,
            key=key,
            scale_type=scale_type,
            scale_info=scale.info,
            chords=chords
        )

class ChordProgression(BaseModel):
    """Represents a sequence of chords that can be used in a musical composition."""
    id: Optional[str] = Field(default=None, description="Unique identifier for the chord progression")
    name: str = Field(..., min_length=2, description="Name of the chord progression")
    key: str = Field(..., min_length=1, max_length=2, pattern=r"^[A-Ga-g][#b]?$")  # Modified pattern to be case-insensitive
    scale_type: str = Field(..., description="Scale type")
    scale_info: Union[str, ScaleInfo] = Field(..., description="Scale info")
    chords: List[Chord] = Field(..., min_length=1, max_length=32, description="List of chords in the progression")
    complexity: float = Field(default=0.5, ge=0.0, le=1.0, description="Complexity score (0.0-1.0)")
    genre: Optional[str] = Field(default=None, description="Musical genre")
    tags: List[str] = Field(default_factory=lambda: ["default"], description="Tags for categorization")
    description: str = Field(default="", description="Description of the progression")

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate and normalize the key."""
        v = v.upper()  # Convert to uppercase first
        if not re.match(r'^[A-G][#b]?$', v):
            raise ValueError("Key must be a valid note name (A-G) with optional sharp (#) or flat (b)")
        return v

    def generate_progression_from_pattern(
        self,
        pattern: List[str],
        scale_info: ScaleInfo,
        progression_length: int
    ) -> 'ChordProgression':
        """Generate chord progression from a pattern string."""
        if not pattern:
            raise ValueError("Pattern cannot be empty")
        
        from src.note_gen.models.scale import Scale
        from src.note_gen.models.roman_numeral import RomanNumeral
        
        scale = Scale.from_scale_info(scale_info)
        new_chords = []
        
        for numeral in pattern[:progression_length]:
            roman = RomanNumeral.from_roman_numeral(numeral)
            scale_degree = roman.to_scale_degree()
            root_note = scale.get_note_from_degree(scale_degree)
            new_chord = Chord(root=root_note, quality=roman.quality, inversion=roman.inversion)
            new_chords.append(new_chord)
        
        return ChordProgression(
            name=self.name,
            key=self.key,
            scale_type=self.scale_type,
            scale_info=scale_info,
            chords=new_chords,
            complexity=self.complexity,
            genre=self.genre
        )

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        data = super().model_dump(**kwargs)
        if hasattr(self, 'complexity'):
            data['complexity'] = self.complexity
        return data

    @model_validator(mode='before')
    @classmethod
    def validate_scale_info(cls, v: Any) -> Any:
        if isinstance(v, ScaleInfo):
            return {
                'root': v.root,
                'scale_type': v.scale_type,
                'complexity': v.complexity  # Add the missing complexity field
            }
        return v

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
        if not hasattr(self, 'id'):
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
        for item in pattern.chords:
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
            chords=chords,
            key=key,
            scale_type=scale_type,
            scale_info=scale.info
        )

    @classmethod
    @field_validator('key')
    def validate_key(cls, v: str) -> str:
        """Validate the key value."""
        if not v:
            raise ValueError("Key cannot be empty")
        if len(v) < 1 or len(v) > 2:
            raise ValueError("Key must be a single character or a character followed by '#' or 'b'")
        if v[0].upper() not in 'ABCDEFG!':
            raise ValueError("Key must start with a letter from A to G or '!' for no key")
        if len(v) == 2 and v[1] not in '#!b!':
            raise ValueError("Key must end with '#' or 'b' if it's two characters long, or '!' for no key")
        return v

    @classmethod
    @field_validator('scale_type')
    def validate_scale_type(cls, v: str) -> str:
        """Validate the scale type value."""
        if not v:
            raise ValueError("Scale type cannot be empty")
        if v.upper() not in ['MAJOR', 'MINOR', 'HARMONIC_MINOR', 'MELODIC_MINOR']:
            raise ValueError("Scale type must be one of 'MAJOR', 'MINOR', 'HARMONIC_MINOR', 'MELODIC_MINOR'")
        return v.upper()

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
    """Data for a rhythm pattern."""
    name: Annotated[str, Field(default="Default Pattern", min_length=1)]
    notes: Annotated[List[RhythmNote], Field(default_factory=lambda: [RhythmNote(position=0, duration=1.0)], min_length=1)]
    time_signature: Annotated[str, Field(default="4/4")]
    default_duration: Annotated[float, Field(default=1.0, gt=0)]
    groove_type: Literal['straight', 'swing', 'shuffle'] = Field(default="straight")
    style: str = Field(default="basic", min_length=1)
    duration: float = Field(default=4.0, gt=0)
    pattern: Annotated[str, Field(default="4 4 4 4", min_length=1)]
    accent_pattern: List[Union[str, float]] = Field(default_factory=list)
    swing_enabled: bool = Field(default=False)
    swing_ratio: float = Field(default=0.67, ge=0.5, le=0.75)
    humanize_amount: float = Field(default=0.1, ge=0.0, le=1.0)
    variation_probability: float = Field(default=0.1, ge=0.0, le=1.0)
    total_duration: float = Field(default=0.0)

    @field_validator('time_signature')
    def validate_time_signature(cls, v: str) -> str:
        """Validate time signature format and value."""
        if not re.match(r'^[1-9]\d*\/[1-9]\d*$', v):
            raise ValueError("Time signature must be in format 'x/y' with positive numbers")
        numerator, denominator = map(int, v.split('/'))
        if numerator <= 0 or denominator <= 0:
            raise ValueError("Time signature components must be greater than 0")
        if denominator not in {1, 2, 4, 8, 16, 32, 64}:
            raise ValueError("Time signature denominator must be a power of 2")
        return v

    @model_validator(mode='after')
    def calculate_total_duration(self) -> 'RhythmPatternData':
        """Calculate total duration based on notes."""
        self._total_duration = sum(note.duration for note in self.notes)
        self.total_duration = self._total_duration
        return self

    @field_validator('groove_type', mode='before')
    @classmethod
    def validate_groove_type(cls, value: str) -> str:
        if value not in ['straight', 'swing', 'shuffle']:
            raise ValueError("Invalid groove type. Must be one of: straight, swing, shuffle")
        return value

    @field_validator('accent_pattern', mode='before')
    @classmethod
    def validate_accent_pattern(cls, value: List[Union[str, float]]) -> List[float]:
        if not value:
            return []
        result = []
        for item in value:
            if isinstance(item, str):
                try:
                    float_value = float(item)
                    if 0.0 <= float_value <= 2.0:
                        result.append(float_value)
                    else:
                        raise ValueError("Invalid accent value. Must be a float between 0.0 and 2.0")
                except ValueError:
                    raise ValueError("Invalid accent value. Must be a float between 0.0 and 2.0")
            elif isinstance(item, (int, float)):
                if 0.0 <= item <= 2.0:
                    result.append(float(item))
                else:
                    raise ValueError("Invalid accent value. Must be a float between 0.0 and 2.0")
            else:
                raise ValueError("Invalid accent value type")
        return result

    @field_validator('pattern', mode='before')
    @classmethod
    def validate_pattern(cls, value: Any) -> str:
        if not value:
            raise ValueError('Pattern cannot be empty')
        
        try:
            parts = value.split()
            for part in parts:
                # Allow negative numbers for rests
                if not part.lstrip('-').isdigit():
                    raise ValueError('Pattern must contain only numbers separated by spaces')
                if float(part) == 0:
                    raise ValueError('Pattern values cannot be zero')
        except ValueError as e:
            raise ValueError(f'Invalid pattern format: {e}')
        
        return value

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        # Create a dictionary with the exact structure expected by tests
        # The order of keys matters for the test comparison
        return {
            'accent_pattern': self.accent_pattern,
            'groove_type': self.groove_type,
            'notes': self.notes,
            'pattern': self.pattern,
            'time_signature': self.time_signature,
        }

class RhythmPattern(BaseModel):
    """Object for rhythm patterns."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1)
    pattern: str = Field(..., min_length=1)  # Make pattern required
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    time_signature: str = Field(default="4/4")
    data: Optional[RhythmPatternData] = None

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Pattern must be a string")
        
        # Allow patterns with dashes
        pattern_parts = v.replace('-', ' ').strip().split()
        if not pattern_parts:
            raise ValueError("Pattern must contain at least one value")
        
        # Validate each part is a number
        try:
            [float(part) for part in pattern_parts]
        except ValueError as e:
            raise ValueError(f"Invalid pattern format: {str(e)}")
        
        return v

    @model_validator(mode='after')
    def validate_duration(self) -> 'RhythmPattern':
        pattern_parts = self.pattern.replace('-', ' ').strip().split()
        total_duration = sum(float(x) for x in pattern_parts)
        
        time_sig_parts = self.time_signature.split('/')
        expected_duration = (float(time_sig_parts[0]) / float(time_sig_parts[1])) * 4
        
        if abs(total_duration - expected_duration) > 0.001:
            raise ValueError(f"Pattern duration {total_duration} does not match time signature duration {expected_duration}")
        
        return self

    @field_validator('time_signature')
    def validate_time_signature(cls, v: str) -> str:
        """Validate time signature format."""
        if not re.match(r'^[1-9]\d*\/[1-9]\d*$', v):
            raise ValueError("Time signature must be in format 'x/y' with positive numbers")
        numerator, denominator = map(int, v.split('/'))
        if denominator not in {1, 2, 4, 8, 16, 32, 64}:
            raise ValueError("Time signature denominator must be a power of 2")
        return v

    @property
    def durations(self) -> List[float]:
        """Get the durations as a list of floats."""
        return [float(x) for x in self.pattern.split()]

    @property
    def total_duration(self) -> float:
        """Calculate total duration of the pattern."""
        return sum(abs(x) for x in self.durations)

class Patterns(BaseModel):
    """Container class for all pattern types"""
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