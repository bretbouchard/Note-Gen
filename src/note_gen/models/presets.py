"""Presets for chord progressions, note patterns, and rhythm patterns."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
import uuid
import logging

from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.note import Note
from src.note_gen.models.patterns import (
    NotePattern,
    NotePatternData,
    RhythmNote,
    RhythmPatternData,
    ChordProgression
)
from src.note_gen.models.scale import Scale
from src.note_gen.core.enums import ScaleType
from src.note_gen.models.scale_info import ScaleInfo 
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.rhythm import RhythmPattern

# Default values
DEFAULT_KEY = "C"
DEFAULT_SCALE_TYPE = ScaleType.MAJOR
DEFAULT_CHORD_PROGRESSION = "I-IV-V"
DEFAULT_NOTE_PATTERN = "Simple Triad"
DEFAULT_RHYTHM_PATTERN = "basic_4_4"
DEFAULT_RHYTHM_PATTERN_NAME = "basic_4_4"

# All pattern definitions consolidated here
COMMON_PROGRESSIONS: Dict[str, List[str]] = {
    "I-IV-V": ["I", "IV", "V"],
    "I-V-vi-IV": ["I", "V", "vi", "IV"],
    "ii-V-I": ["ii", "V", "I"],
    "I-vi-IV-V": ["I", "vi", "IV", "V"],
    "I-V-IV": ["I", "V", "IV"],
    "ii-V-I-IV": ["ii", "V", "I", "IV"],
}

NOTE_PATTERNS: Dict[str, Dict[str, Any]] = {
    'Simple Triad': {
        'name': 'Simple Triad',
        'intervals': [0, 4, 7],
        'data': {
            'notes': [
                {'note_name': 'C', 'octave': 4},
                {'note_name': 'E', 'octave': 4},
                {'note_name': 'G', 'octave': 4}
            ],
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
        },
        'complexity': 0.5,
        'tags': ['default']
    }
}

RHYTHM_PATTERNS: Dict[str, Dict[str, Any]] = {
    'basic_4_4': {
        'name': 'basic_4_4',
        'description': "Basic 4/4 rhythm pattern with quarter notes",
        'tags': ["default", "basic"],
        'pattern': [1.0, 1.0, 1.0, 1.0],
        'data': {
            'time_signature': '4/4',
            'default_duration': 1.0,
            'groove_type': "straight",
            'swing_enabled': False,
            'swing_ratio': 0.67,
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
        }
    }
}

# Count the number of patterns
chord_progressions_count = len(COMMON_PROGRESSIONS)
note_patterns_count = len(NOTE_PATTERNS)
rhythm_patterns_count = len(RHYTHM_PATTERNS)

print(f"Chord Progressions: {chord_progressions_count}, Note Patterns: {note_patterns_count}, Rhythm Patterns: {rhythm_patterns_count}")

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

    def to_pattern(self) -> ChordProgression:
        """Convert preset to a ChordProgression pattern."""
        return ChordProgression(
            name=self.name,
            chords=self.numerals,
            key=DEFAULT_KEY,
            mode=DEFAULT_SCALE_TYPE.value,
            description=self.description,
            tags=self.tags,
            complexity=self.complexity,
            data={
                "qualities": self.qualities,
                "durations": self.durations,
                "genre": self.genre
            }
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
            for name, numerals in COMMON_PROGRESSIONS.items()
        },
        description='Common chord progression patterns with Roman numeral support'
    )
    
    rhythm_patterns: Dict[str, RhythmPattern] = Field(
        default_factory=lambda: {
            name: RhythmPattern(
                name=name,
                pattern=' '.join(map(str, [int(float(x)) for x in data['pattern']])),
                data=RhythmPatternData(
                    pattern=' '.join(map(str, [int(float(x)) for x in data['pattern']])),
                    duration=data['duration'],
                    position=data['position'],
                    velocity=data['velocity'],
                    direction=data['direction'],
                    use_chord_tones=data['use_chord_tones'],
                    use_scale_mode=data['use_scale_mode'],
                    arpeggio_mode=data['arpeggio_mode'],
                    restart_on_chord=data['restart_on_chord'],
                    octave_range=data['octave_range'],
                    default_duration=data['default_duration']
                ),
                description=data['description'],
                complexity=data['complexity'],
                tags=data['tags']
            )
            for name, data in RHYTHM_PATTERNS.items()
        },
        description='Rhythm pattern configurations'
    )
    
    note_patterns: Dict[str, NotePattern] = Field(
        default_factory=lambda: {
            'Simple Triad': NotePattern(
                name='Simple Triad',
                intervals=[0, 4, 7],
                data=NotePatternData(
                    notes=[Note(note_name='C', octave=4), Note(note_name='E', octave=4), Note(note_name='G', octave=4)],
                    intervals=[4, 3],
                    duration=1.0,
                    position=0.0,
                    velocity=100,
                    direction='up',
                    use_chord_tones=False,
                    use_scale_mode=False,
                    arpeggio_mode=False,
                    restart_on_chord=False,
                    octave_range=[4, 5],
                    default_duration=1.0
                ),
                complexity=0.5,
                tags=['default']
            ),
            'Minor Triad': NotePattern(
                name='Minor Triad',
                intervals=[0, 3, 7],
                data=NotePatternData(
                    notes=[Note(note_name='C', octave=4), Note(note_name='Eb', octave=4), Note(note_name='G', octave=4)],
                    intervals=[3, 4],
                    duration=1.0,
                    position=0.0,
                    velocity=100,
                    direction='up',
                    use_chord_tones=False,
                    use_scale_mode=False,
                    arpeggio_mode=False,
                    restart_on_chord=False,
                    octave_range=[4, 5],
                    default_duration=1.0
                ),
                complexity=0.5,
                tags=['default']
            )
        },
        description='Note pattern configurations'
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

    def get_chord_progression(self, name: str) -> Optional[ChordProgression]:
        """Get a chord progression by name."""
        progression_data = COMMON_PROGRESSIONS.get(name)
        if progression_data:
            return ChordProgression(
                name=name,
                chords=progression_data,
                key=DEFAULT_KEY,
                mode=DEFAULT_SCALE_TYPE.value
            )
        return None

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
    default_key: str = Field(DEFAULT_KEY, description="Default key")
    default_scale_type: ScaleType = Field(DEFAULT_SCALE_TYPE, description="Default scale type")
    scale_info: Optional[ScaleInfo] = Field(default=None, description="Scale information")
    style: Optional[str] = Field(default=None, description="Style")

    @classmethod
    def load(cls, default_key: str = DEFAULT_KEY, default_scale_type: ScaleType = DEFAULT_SCALE_TYPE, 
             scale_info: Optional[ScaleInfo] = None, style: Optional[str] = None) -> List['Presets']:
        return [cls(default_key=default_key, default_scale_type=default_scale_type, scale_info=scale_info, style=style)]

    def get_default_chord_progression(self, root_note: Note, scale: Scale) -> ChordProgression:
        return ChordProgression.from_chord_progression_pattern(
            self.patterns.get_chord_progression(DEFAULT_CHORD_PROGRESSION),
            root_note.name,
            scale.scale_type.value
        )

    def get_default_note_pattern(self) -> NotePattern:
        return NotePattern(
            name=DEFAULT_NOTE_PATTERN,
            intervals=[0, 2, 4],
            complexity=0.5,
            tags=['default'],
            data=NotePatternData(
                notes=[Note(note_name='C', octave=4), Note(note_name='E', octave=4), Note(note_name='G', octave=4)],
                intervals=[4, 3],
                duration=1.0,
                position=0.0,
                velocity=100,
                direction='up',
                use_chord_tones=False,
                use_scale_mode=False,
                arpeggio_mode=False,
                restart_on_chord=False,
                octave_range=[4, 5],
                default_duration=1.0
            )
        )

    def get_default_rhythm_pattern(self) -> RhythmPattern:
        return RhythmPattern(
            name=DEFAULT_RHYTHM_PATTERN,
            pattern='4 4 4 4',
            complexity=0.5,
            tags=['default'],
            data=RhythmPatternData(
                name=DEFAULT_RHYTHM_PATTERN_NAME,
                time_signature='4/4',
                default_duration=1.0,
                pattern='4 4 4 4',
                notes=[
                    RhythmNote(position=0.0, duration=1.0),
                    RhythmNote(position=1.0, duration=1.0),
                    RhythmNote(position=2.0, duration=1.0),
                    RhythmNote(position=3.0, duration=1.0)
                ]
            )
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

def get_default_chord_progression(root_note: Note, scale: Scale) -> ChordProgression:
    """Get the default chord progression."""
    from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator
    
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
        scale_type=str(ScaleType(scale.scale_type)) if isinstance(scale.scale_type, str) and scale.scale_type in [ScaleType.MAJOR, ScaleType.MINOR] else str(ScaleType.MAJOR),
        complexity=0.5
    )

    numerals = COMMON_PROGRESSIONS[DEFAULT_CHORD_PROGRESSION]
    chords = []
    for numeral in numerals:  
        note = RomanNumeral.convert_to_note(numeral, scale)  # New logic using RomanNumeral
        chord = generator.generate_chord(note, quality=ChordQuality.MAJOR)  # Updated to use imported ChordQuality
        chords.append(chord)
    
    # Convert Chord objects to their string representations for ChordProgression
    chord_strings = [str(chord) for chord in chords]
    progression = ChordProgression(
        name="Default", 
        chords=chord_strings,
        key=root_note.note_name,
        scale_type=str(scale.scale_type),
        scale_info=str(scale_info),
        complexity=0.5
    )
    
    return progression

def get_available_chord_progressions() -> List[str]:
    """Get a list of available chord progression names."""
    return list(COMMON_PROGRESSIONS.keys())

def get_available_note_patterns() -> List[str]:
    """Get a list of available note pattern names."""
    return list(NOTE_PATTERNS.keys())

def get_available_rhythm_patterns() -> List[str]:
    """Get a list of available rhythm pattern names."""
    return list(RHYTHM_PATTERNS.keys())

# Count the number of patterns
chord_progressions_count = len(COMMON_PROGRESSIONS)
note_patterns_count = len(NOTE_PATTERNS)
rhythm_patterns_count = len(RHYTHM_PATTERNS)

print(f"Chord Progressions: {chord_progressions_count}, Note Patterns: {note_patterns_count}, Rhythm Patterns: {rhythm_patterns_count}")
