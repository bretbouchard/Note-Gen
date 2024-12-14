"""Module for generating chord progressions."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, ClassVar
from pydantic import BaseModel, Field

from .chord import Chord
from .scale_info import ScaleInfo
from .chord_progression import ChordProgression

class ProgressionPattern(str, Enum):
    """Common chord progression patterns."""
    BASIC_I_IV_V_I = "I-IV-V-I"
    POP_I_V_vi_IV = "I-V-vi-IV"
    BLUES_I_IV_I_V = "I-IV-I-V"
    JAZZ_ii_V_I = "ii-V-I"
    FIFTIES_I_vi_IV_V = "I-vi-IV-V"
    CANON_I_V_vi_iii_IV_I_IV_V = "I-V-vi-iii-IV-I-IV-V"
    MINOR_i_iv_v = "i-iv-v"
    MINOR_i_VI_III_VII = "i-VI-III-VII"

class ChordProgressionGenerator(BaseModel):
    """Generator for chord progressions."""
    scale_info: ScaleInfo
    progression_length: int = Field(default=4)
    pattern: Optional[ProgressionPattern] = None

    # Define common chord qualities for major and minor scales
    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, str]] = {
        1: "major",      # I
        2: "minor",      # ii
        3: "minor",      # iii
        4: "major",      # IV
        5: "major",      # V
        6: "minor",      # vi
        7: "diminished"  # vii°
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, str]] = {
        1: "minor",      # i
        2: "diminished", # ii°
        3: "major",      # III
        4: "minor",      # iv
        5: "minor",      # v
        6: "major",      # VI
        7: "major"       # VII
    }

    # Define common progression patterns
    PROGRESSION_PATTERNS: ClassVar[Dict[ProgressionPattern, List[Tuple[int, str]]]] = {
        ProgressionPattern.BASIC_I_IV_V_I: [(1, "major"), (4, "major"), (5, "major"), (1, "major")],
        ProgressionPattern.POP_I_V_vi_IV: [(1, "major"), (5, "major"), (6, "minor"), (4, "major")],
        ProgressionPattern.BLUES_I_IV_I_V: [(1, "major7"), (4, "major7"), (1, "major7"), (5, "dominant7")],
        ProgressionPattern.JAZZ_ii_V_I: [(2, "minor7"), (5, "dominant7"), (1, "major7")],
        ProgressionPattern.FIFTIES_I_vi_IV_V: [(1, "major"), (6, "minor"), (4, "major"), (5, "major")],
        ProgressionPattern.CANON_I_V_vi_iii_IV_I_IV_V: [
            (1, "major"), (5, "major"), (6, "minor"), (3, "minor"),
            (4, "major"), (1, "major"), (4, "major"), (5, "major")
        ],
        ProgressionPattern.MINOR_i_iv_v: [(1, "minor"), (4, "minor"), (5, "minor")],
        ProgressionPattern.MINOR_i_VI_III_VII: [(1, "minor"), (6, "major"), (3, "major"), (7, "major")]
    }

    def get_chord_quality(self, scale_degree: int, is_minor: bool = False) -> str:
        """Get the default chord quality for a scale degree."""
        qualities = self.MINOR_SCALE_QUALITIES if is_minor else self.MAJOR_SCALE_QUALITIES
        return qualities[scale_degree]

    def generate(self, pattern: Optional[ProgressionPattern] = None) -> ChordProgression:
        """Generate a chord progression based on the specified pattern."""
        progression = ChordProgression(scale_info=self.scale_info)
        pattern = pattern or self.pattern or ProgressionPattern.BASIC_I_IV_V_I

        # Get the progression pattern
        progression_pattern = self.PROGRESSION_PATTERNS[pattern]

        # Generate chords based on the pattern
        for degree, quality in progression_pattern:
            root = self.scale_info.get_scale_degree(degree)
            chord = Chord(root=root, quality=quality)
            progression.add_chord(chord)

        return progression

    def generate_custom(self, degrees: List[int], qualities: Optional[List[str]] = None) -> ChordProgression:
        """Generate a custom chord progression using specified scale degrees."""
        progression = ChordProgression(scale_info=self.scale_info)
        is_minor = self.scale_info.mode.lower() == "minor"

        # If qualities are not specified, use default qualities based on scale
        if qualities is None:
            qualities = [self.get_chord_quality(degree, is_minor) for degree in degrees]

        # Generate chords
        for degree, quality in zip(degrees, qualities):
            root = self.scale_info.get_scale_degree(degree)
            chord = Chord(root=root, quality=quality)
            progression.add_chord(chord)

        return progression

    def generate_random(self, length: Optional[int] = None) -> ChordProgression:
        """Generate a random chord progression."""
        import random

        length = length or self.progression_length
        progression = ChordProgression(scale_info=self.scale_info)
        is_minor = self.scale_info.mode.lower() == "minor"

        # Common scale degrees (1, 4, 5 are most common)
        common_degrees = [1, 4, 5] * 2 + [2, 3, 6] + [7]
        
        # Generate random progression
        for _ in range(length):
            degree = random.choice(common_degrees)
            quality = self.get_chord_quality(degree, is_minor)
            
            # Occasionally add seventh chords
            if random.random() < 0.3:
                if quality == "major":
                    quality = random.choice(["major7", "dominant7"])
                elif quality == "minor":
                    quality = "minor7"

            root = self.scale_info.get_scale_degree(degree)
            chord = Chord(root=root, quality=quality)
            progression.add_chord(chord)

        return progression

    def generate_chord(self, numeral: str) -> Chord:
        """Generate a chord from a Roman numeral."""
        from .roman_numeral import RomanNumeral
        
        # Handle pedal point chords (e.g., I/V)
        if "/" in numeral:
            upper, lower = numeral.split("/")
            upper_chord = Chord.from_roman_numeral(upper, self.scale_info)
            lower_numeral = RomanNumeral.from_str(lower, self.scale_info)
            lower_note = lower_numeral.to_note()
            
            # Add the pedal note to the chord
            notes = upper_chord.notes
            notes.insert(0, lower_note)  # Add bass note at the beginning
            return Chord(
                root=upper_chord.root,
                quality=upper_chord.quality,
                chord_notes=notes,
                duration=upper_chord.duration,
                velocity=upper_chord.velocity
            )
        
        # Parse the roman numeral with scale context
        roman = RomanNumeral.from_str(numeral, self.scale_info)
        
        # Get the root note based on the scale degree
        root = roman.get_note()
        
        # Create the chord with the specified quality
        return Chord(root=root, quality=roman.chord_quality)

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = super().dict(*args, **kwargs)
        if self.scale_info:
            d['scale_info'] = self.scale_info.dict()
        return d