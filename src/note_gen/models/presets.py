# src/note_gen/models/presets.py

"""Presets for chord progressions, note patterns, and rhythm patterns."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
import uuid
import logging

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.patterns import Patterns, NotePattern, NotePatternData, RhythmNote, ChordProgressionPattern, RhythmPattern, RhythmPatternData
from src.note_gen.models.scale import Scale
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.scale_info import ScaleInfo 
from src.note_gen.models.roman_numeral import RomanNumeral

from src.note_gen.models.patterns import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS

# Default values for musical components
DEFAULT_KEY = "C"
DEFAULT_SCALE_TYPE = ScaleType.MAJOR
DEFAULT_CHORD_PROGRESSION = "I-IV-V"
DEFAULT_NOTE_PATTERN = "Simple Triad"
DEFAULT_RHYTHM_PATTERN = "Basic Rhythm"
DEFAULT_RHYTHM_PATTERN_NAME = "Basic"

class ChordProgressionPreset(BaseModel):
    """Represents a preset chord progression pattern with proper Roman numeral handling."""
    name: str = Field(..., description="Name of the chord progression")
    numerals: List[str] = Field(..., description="List of Roman numerals representing the progression")
    qualities: Optional[List[str]] = Field(default=None, description="Optional chord qualities")
    durations: Optional[List[float]] = Field(default=None, description="Optional durations for each chord")
    description: str = Field(default="", description="Description of the progression")
    tags: List[str] = Field(default_factory=lambda: ["default"], description="Tags for categorization")
    complexity: float = Field(default=0.5, ge=0.0, le=1.0, description="Complexity rating")
    genre: Optional[str] = Field(default=None, description="Musical genre")

    @field_validator('numerals')
    @classmethod
    def validate_numerals(cls, v: List[str]) -> List[str]:
        """Validate Roman numerals are in correct format."""
        for numeral in v:
            try:
                # This will raise ValueError if invalid
                RomanNumeral.from_string(numeral)
            except ValueError as e:
                raise ValueError(f"Invalid Roman numeral '{numeral}': {str(e)}")
        return v

    @field_validator('qualities')
    @classmethod
    def validate_qualities(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate chord qualities if provided."""
        if v is None:
            return v
        valid_qualities = {"MAJOR", "MINOR", "DIMINISHED", "AUGMENTED", "DOMINANT", 
                         "MAJOR7", "MINOR7", "DOMINANT7", "DIMINISHED7", "HALF_DIMINISHED7"}
        for quality in v:
            base_quality = quality.split('7')[0].upper() if '7' in quality else quality.upper()
            if base_quality not in valid_qualities and quality not in valid_qualities:
                raise ValueError(f"Invalid chord quality: {quality}")
        return v

    @field_validator('durations')
    @classmethod
    def validate_durations(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate durations if provided."""
        if v is None:
            return v
        if any(d <= 0 for d in v):
            raise ValueError("All durations must be positive")
        return v

    def to_pattern(self) -> ChordProgressionPattern:
        """Convert to a ChordProgressionPattern."""
        from src.note_gen.models.patterns import ChordProgressionPattern, ChordPatternItem
        
        pattern_items = []
        for i, numeral in enumerate(self.numerals):
            roman = RomanNumeral.from_string(numeral)
            quality = self.qualities[i] if self.qualities and i < len(self.qualities) else "DEFAULT"
            duration = self.durations[i] if self.durations and i < len(self.durations) else 4.0
            
            pattern_items.append(ChordPatternItem(
                degree=roman.to_scale_degree(),
                quality=quality,
                duration=duration
            ))
        
        return ChordProgressionPattern(
            name=self.name,
            description=self.description,
            tags=self.tags,
            complexity=self.complexity,
            genre=self.genre,
            pattern=pattern_items
        )

class Patterns(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    chord_progressions: Dict[str, ChordProgressionPreset] = Field(
        default_factory=lambda: {
            name: ChordProgressionPreset(
                name=name,
                numerals=numerals,
                description=f"Common {name} progression",
                tags=["default"],
                complexity=0.5
            )
            for name, numerals in COMMON_PROGRESSIONS_ROMAN.items()
        },
        description='Common chord progression patterns with Roman numeral support'
    )
    
    note_patterns: Dict[str, NotePattern] = Field(
        default_factory=lambda: {
            'Simple Triad': NotePattern(
                name='Simple Triad',
                pattern=[0, 2, 4],
                complexity=0.5,
                tags=['default']
            ),
            'Minor Triad': NotePattern(
                name='Minor Triad',
                pattern=[0, 1, 4],
                complexity=0.5,
                tags=['default']
            )
        },
        description='Note pattern configurations'
    )
    
    rhythm_patterns: Dict[str, RhythmPattern] = Field(
        default_factory=lambda: RHYTHM_PATTERNS,
        description='Rhythm pattern configurations'
    )

    @model_validator(mode='after')
    def validate_patterns(self) -> 'Patterns':
        """Ensure all patterns are properly initialized and validated."""
        # Convert any raw progression data to ChordProgressionPreset objects
        for name, progression in self.chord_progressions.items():
            if isinstance(progression, dict):
                self.chord_progressions[name] = ChordProgressionPreset(**progression)
            elif isinstance(progression, list):
                self.chord_progressions[name] = ChordProgressionPreset(
                    name=name,
                    numerals=progression,
                    description=f"Common {name} progression"
                )
        return self

    def get_chord_progression(self, name: str) -> Optional[ChordProgressionPattern]:
        """Get a chord progression pattern by name."""
        if name not in self.chord_progressions:
            return None
        return self.chord_progressions[name].to_pattern()

    def add_chord_progression(self, name: str, numerals: List[str], 
                            qualities: Optional[List[str]] = None,
                            durations: Optional[List[float]] = None,
                            description: str = "",
                            tags: Optional[List[str]] = None,
                            complexity: float = 0.5,
                            genre: Optional[str] = None) -> None:
        """Add a new chord progression pattern."""
        self.chord_progressions[name] = ChordProgressionPreset(
            name=name,
            numerals=numerals,
            qualities=qualities,
            durations=durations,
            description=description,
            tags=tags or ["default"],
            complexity=complexity,
            genre=genre
        )

class Presets(BaseModel):
    patterns: Patterns = Field(default_factory=Patterns)
    common_progressions: Dict[str, List[str]] = Field(
        default_factory=lambda: dict(COMMON_PROGRESSIONS)
    )
    default_key: str = DEFAULT_KEY
    default_scale_type: ScaleType = DEFAULT_SCALE_TYPE

    @classmethod
    def load(cls) -> List['Presets']:
        # Implement loading logic here
        presets = []
        if cls.common_progressions:
            presets.append(cls())
        return presets  # Example return, replace with actual loading logic

    def get_default_chord_progression(self, root_note: Note, scale: Scale) -> ChordProgression:
        """Get the default chord progression."""
        chords: List[Chord] = []  # Initialize an empty list of Chord instances if needed
        complexity: float = 0.5  # Define complexity here
        
        # Ensure all required fields are provided
        scale_info: ScaleInfo = ScaleInfo(
            scale_type=scale.scale_type,
            root=scale.root  # Ensure this is included
        )
        
        return ChordProgression(
            name="Default Progression",
            root=root_note,
            scale=scale,
            progression=DEFAULT_CHORD_PROGRESSION,
            chords=chords,
            complexity=complexity,
            scale_info=scale_info
        )

    def get_default_note_pattern(self) -> Patterns:
        """Get the default note pattern."""
        return Patterns(
            id=uuid.uuid4(),
            name="Default Pattern",
            pattern=[],
            pattern_type="simple",
            description="A simple pattern",
            tags=["default"],
            complexity=0.5,
            data=NOTE_PATTERNS[DEFAULT_NOTE_PATTERN]
        )

    def get_default_rhythm_pattern(self) -> Patterns:
        """Get the default rhythm pattern."""
        return Patterns(
            name="Default Rhythm Pattern",
            data=RHYTHM_PATTERNS[DEFAULT_RHYTHM_PATTERN],
            complexity=0.5
        )

    def get_available_chord_progressions(self) -> List[str]:
        """Get a list of available chord progression names."""
        return list(COMMON_PROGRESSIONS.keys())

    def get_available_note_patterns(self) -> List[str]:
        """Get a list of available note pattern names."""
        return list(NOTE_PATTERNS.keys())

    def get_available_rhythm_patterns(self) -> List[str]:
        """Get a list of available rhythm pattern names."""
        return list(RHYTHM_PATTERNS.keys())

# Chord progressions
Patterns.CHORD_PROGRESSIONS = {
    "I-IV-V": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["popular", "progression"],
        "complexity": 0.5,
        "description": "A common chord progression in popular music."
    },
    "Pop Ballad_I-V-vi-IV": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["pop", "ballad"],
        "complexity": 0.5,
        "description": "A popular pop ballad progression."
    },
    "ii-V-I": {
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["jazz", "progression"],
        "complexity": 0.6,
        "description": "A common ii-V-I progression in jazz music."
    },
    "I-vi-IV-V (50s Doo-Wop)": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["doo-wop", "classic"],
        "complexity": 0.5,
        "description": "A classic 50s Doo-Wop progression."
    },
    "vi-IV-I-V (Modern Pop)": {
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["modern", "pop"],
        "complexity": 0.5,
        "description": "A common modern pop progression."
    },
    "I-V-vi-iii-IV-I-IV-V (Pop Canon)": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "E", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["pop", "canon"],
        "complexity": 0.5,
        "description": "A popular pop canon progression."
    },
    "I-IV-V-I": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["classic", "progression"],
        "complexity": 0.5,
        "description": "A classic I-IV-V-I progression."
    },
    "ii-V-I": {
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["jazz", "progression"],
        "complexity": 0.6,
        "description": "A common ii-V-I progression in jazz music."
    },
    "I-V-ii-V (Classic)": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["classic", "progression"],
        "complexity": 0.5,
        "description": "A classic I-V-ii-V progression."
    },
    "I-vi-ii-V (Classic)": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["classic", "progression"],
        "complexity": 0.5,
        "description": "A classic I-vi-ii-V progression."
    },
    "IV-I-ii-V (Classic)": {
        "chords": [
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["classic", "progression"],
        "complexity": 0.5,
        "description": "A classic IV-I-ii-V progression."
    },
    "Rock Power": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["rock", "power"],
        "complexity": 0.5,
        "description": "A simple rock power progression."
    },
    "Andalusian Cadence": {
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "E", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "A",
        "scale_type": "MINOR",
        "tags": ["andalusian", "cadence"],
        "complexity": 0.5,
        "description": "A classic Andalusian cadence."
    },
    "EDM Build": {
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "E", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C#", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G#", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "A",
        "scale_type": "MINOR",
        "tags": ["edm", "build"],
        "complexity": 0.5,
        "description": "An EDM build progression."
    },
    "Pop Minor": {
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F#", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C#", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G#", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "A",
        "scale_type": "MINOR",
        "tags": ["pop", "minor"],
        "complexity": 0.5,
        "description": "A common pop minor progression."
    },
    "Funk Groove": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["funk", "groove"],
        "complexity": 0.5,
        "description": "A funky groove progression."
    },
    "I7-IV7-V7 Turnaround": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["turnaround", "classic"],
        "complexity": 0.5,
        "description": "A classic I7-IV7-V7 turnaround."
    },
    "Bird Blues": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["jazz", "blues"],
        "complexity": 0.5,
        "description": "A classic Bird blues progression."
    },
    "So What": {
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MINOR7"}
        ],
        "key": "D",
        "scale_type": "MINOR",
        "tags": ["jazz", "so what"],
        "complexity": 0.5,
        "description": "The famous So What progression."
    },
    "Giant Steps Bridge": {
        "chords": [
            {"root": {"note_name": "B", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "Bb", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F#", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "B",
        "scale_type": "MAJOR",
        "tags": ["jazz", "giant steps"],
        "complexity": 0.5,
        "description": "The bridge of the Giant Steps progression."
    },
    "Misty": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MINOR",
        "tags": ["jazz", "misty"],
        "complexity": 0.5,
        "description": "The Misty progression."
    },
    "Minor Blues": {
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "E", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR7"}
        ],
        "key": "A",
        "scale_type": "MINOR",
        "tags": ["blues", "minor"],
        "complexity": 0.5,
        "description": "A common minor blues progression."
    },
    "Funk Groove": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["funk", "groove"],
        "complexity": 0.5,
        "description": "A funky groove progression."
    },
    "I7-IV7-V7 Turnaround": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["turnaround", "classic"],
        "complexity": 0.5,
        "description": "A classic I7-IV7-V7 turnaround."
    },
    "Bird Blues": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["jazz", "blues"],
        "complexity": 0.5,
        "description": "A classic Bird blues progression."
    },
    "So What": {
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MINOR7"}
        ],
        "key": "D",
        "scale_type": "MINOR",
        "tags": ["jazz", "so what"],
        "complexity": 0.5,
        "description": "The famous So What progression."
    },
    "Giant Steps Bridge": {
        "chords": [
            {"root": {"note_name": "B", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "Bb", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F#", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "B",
        "scale_type": "MAJOR",
        "tags": ["jazz", "giant steps"],
        "complexity": 0.5,
        "description": "The bridge of the Giant Steps progression."
    },
    "Misty": {
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MINOR",
        "tags": ["jazz", "misty"],
        "complexity": 0.5,
        "description": "The Misty progression."
    }
}

def get_default_chord_progression(root_note: Note, scale: Scale) -> ChordProgression:
    """Get the default chord progression."""
    from .chord_progression_generator import ChordProgressionGenerator
    
    # Ensure scale_type is of type ScaleType
    scale_info = ScaleInfo(
        root=root_note, 
        scale_type=ScaleType(scale.scale_type) if isinstance(scale.scale_type, str) and scale.scale_type in [ScaleType.MAJOR, ScaleType.MINOR] else ScaleType.MAJOR
    )

    scale_info.compute_scale_degrees()  # Ensure degrees are populated
    
    # Create a ChordProgressionGenerator with all required arguments
    generator = ChordProgressionGenerator( 
        scale_info=scale_info,  
        name="Default Progression",
        chords=[],
        key=scale_info.root.note_name, 
        scale_type=ScaleType(scale.scale_type) if isinstance(scale.scale_type, str) and scale.scale_type in [ScaleType.MAJOR, ScaleType.MINOR] else ScaleType.MAJOR
    )

    numerals = COMMON_PROGRESSIONS[DEFAULT_CHORD_PROGRESSION]
    chords = []
    for numeral in numerals:  
        note = RomanNumeral.convert_to_note(numeral, scale)  # New logic using RomanNumeral
        chord = generator.generate_chord(note, quality=ChordQualityType.MAJOR)  # Provide a quality argument
        chords.append(chord)
    
    return ChordProgression(
        name="Default Progression",
        root=root_note,
        scale=scale,
        progression=DEFAULT_CHORD_PROGRESSION,
        chords=chords,
        complexity=0.5,
        scale_info=scale_info
    )

def get_available_chord_progressions() -> List[str]:
    """Get a list of available chord progression names."""
    return list(COMMON_PROGRESSIONS.keys())

def get_available_note_patterns() -> List[str]:
    """Get a list of available note pattern names."""
    return list(NOTE_PATTERNS.keys())

def get_available_rhythm_patterns() -> List[str]:
    """Get a list of available rhythm pattern names."""
    return list(RHYTHM_PATTERNS.keys())

# Count the number of chord progressions, note patterns, and rhythm patterns
chord_progressions_count = len(Patterns.CHORD_PROGRESSIONS)
note_patterns_count = len(NOTE_PATTERNS)
rhythm_patterns_count = len(RHYTHM_PATTERNS)

print(f"Chord Progressions: {chord_progressions_count}, Note Patterns: {note_patterns_count}, Rhythm Patterns: {rhythm_patterns_count}")
