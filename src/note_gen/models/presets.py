"""Presets for chord progressions, note patterns, and rhythm patterns."""

from typing import List, Dict, Any, Optional, Union, Sequence
from pydantic import BaseModel, Field

from .rhythm import RhythmPattern, RhythmNote  # Updated import
from .roman_numeral import RomanNumeral
from .chord import Chord
from .chord_progression import (
    ChordProgression,
    ChordProgressionItem
)
from .scale_info import ScaleInfo
from .note import Note
from .patterns import NotePattern, NotePatternData
from note_gen.core.enums import ScaleType, ChordQuality
from note_gen.core.constants import COMMON_PROGRESSIONS, DEFAULTS

# Default values
DEFAULT_KEY = "C"
DEFAULT_SCALE_TYPE = ScaleType.MAJOR
DEFAULT_CHORD_PROGRESSION = "I-IV-V"
DEFAULT_NOTE_PATTERN = "Simple Triad"
DEFAULT_RHYTHM_PATTERN = "basic_4_4"

class ChordProgressionPreset(BaseModel):
    """Represents a preset chord progression pattern."""
    name: str = Field(..., description="Name of the chord progression")
    numerals: List[str] = Field(..., description="List of Roman numerals")
    qualities: Optional[List[str]] = Field(default=None)
    durations: Optional[List[float]] = Field(default=None)
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=lambda: ["default"])
    complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    genre: Optional[str] = Field(default=None)

    def to_chord_progression(self, key: str, scale_type: ScaleType) -> ChordProgression:
        """Convert preset to ChordProgression."""
        scale_info = ScaleInfo(key=key, scale_type=scale_type)
        chords: Sequence[ChordProgressionItem] = []

        for i, numeral in enumerate(self.numerals):
            duration = self.durations[i] if self.durations else 1.0
            quality_str = self.qualities[i] if self.qualities else None
            roman = RomanNumeral.from_string(numeral)
            chord = roman.to_chord(scale_info)

            # Determine the quality
            if quality_str is not None:
                quality = ChordQuality(quality_str)  # Convert string to enum
            else:
                quality = (ChordQuality.MINOR if roman.is_minor()
                          else ChordQuality.MAJOR)

            # Create ChordProgressionItem
            chord_item = ChordProgressionItem(
                chord=numeral,  # Use the roman numeral string
                root=chord.root.note_name,  # Get the note name string from the root Note object
                duration=duration,
                position=float(sum(self.durations[:i] if self.durations else [1.0] * i)),
                quality=quality  # Now properly typed as ChordQuality
            )
            chords.append(chord_item)

        return ChordProgression(
            name=self.name,
            chords=list(chords),  # Convert Sequence to List
            key=key,
            scale_type=scale_type,
            scale_info=scale_info
        )

def create_default_note_pattern() -> NotePattern:
    """Create default note pattern."""
    return NotePattern(
        name=DEFAULT_NOTE_PATTERN,
        pattern=[
            Note(
                pitch='C',
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=100
            )
        ],
        data=NotePatternData(
            octave_range=(4, 5),
            max_interval_jump=12,
            allow_chromatic=False
        )
    )

def create_default_rhythm_pattern() -> RhythmPattern:
    """Create default rhythm pattern."""
    return RhythmPattern(
        name=DEFAULT_RHYTHM_PATTERN,
        pattern=[
            RhythmNote(
                position=float(i),
                duration=1.0,
                velocity=100
            ) for i in range(4)
        ],
        time_signature=(4, 4)
    )

class Presets(BaseModel):
    """Model for musical presets."""
    default_key: str = Field(default="C")
    default_scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    common_progressions: Dict[str, Any] = Field(
        default_factory=lambda: COMMON_PROGRESSIONS
    )

    def get_progression_chords(self, name: str, scale_info: ScaleInfo) -> List[Chord]:
        """Get chords for a named progression."""
        if name not in self.common_progressions:
            raise ValueError(f"Unknown progression: {name}")

        return [
            RomanNumeral.from_string(numeral).to_chord(scale_info)
            for numeral in self.common_progressions[name]
        ]

    def create_pattern(self, pattern_data: Dict[str, Any]) -> NotePattern:
        """Create a note pattern from pattern data."""
        return NotePattern(
            pattern=[],  # Initialize with empty pattern
            data=NotePatternData(**pattern_data)
        )

    @classmethod
    def load(cls) -> List['Presets']:
        """Load presets from configuration."""
        return [cls()]

    @classmethod
    def from_preset(cls, preset_data: Dict[str, Any]) -> 'Presets':
        """Create a preset from preset data."""
        return cls(
            default_key=preset_data.get('default_key', DEFAULT_KEY),
            default_scale_type=preset_data.get('default_scale_type', DEFAULT_SCALE_TYPE)
        )

class RhythmPreset(BaseModel):
    """Model for rhythm presets."""
    def create_pattern(self, name: str) -> RhythmPattern:
        """Create a rhythm pattern from preset."""
        return RhythmPattern(
            name=name,
            pattern=[
                RhythmNote(
                    position=0.0,
                    duration=1.0,
                    velocity=100
                )
            ],
            time_signature=(4, 4)
        )

class Preset(BaseModel):
    name: str
    key: str = DEFAULTS["key"]
    scale_type: ScaleType = ScaleType.MAJOR  # Default scale type
    bpm: int = 120  # Default BPM
    time_signature: str = "4/4"  # Default time signature
