"""Factory for creating musical patterns."""
from typing import Union, Tuple, Optional, List
from ..models.patterns import NotePattern, RhythmPattern
from ..models.note import Note
from ..models.rhythm_note import RhythmNote
from ..core.constants import NOTE_PATTERNS, RHYTHM_PATTERNS

class PatternFactory:
    """Factory class for creating musical patterns."""

    def _create_note_pattern(
        self,
        name: str,
        octave_range: Tuple[int, int],
        use_scale_mode: bool,
        **kwargs
    ) -> NotePattern:
        """Create a note pattern."""
        pattern_data = {
            "name": name,
            "pattern": [],  # Will be populated based on parameters
            "octave_range": octave_range,
            "use_scale_mode": use_scale_mode,
            **kwargs
        }
        return NotePattern(**pattern_data)

    def _create_rhythm_pattern(
        self,
        name: str,
        **kwargs
    ) -> RhythmPattern:
        """Create a rhythm pattern."""
        pattern_data = {
            "name": name,
            "pattern": [],  # Will be populated based on parameters
            **kwargs
        }
        return RhythmPattern(**pattern_data)

    def create_pattern(
        self,
        pattern_type: str,
        name: str,
        **kwargs
    ) -> Union[NotePattern, RhythmPattern]:
        """Create a new pattern instance."""
        if pattern_type == "note":
            return self._create_note_pattern(name=name, **kwargs)
        elif pattern_type == "rhythm":
            return self._create_rhythm_pattern(name=name, **kwargs)
        else:
            raise ValueError(f"Unknown pattern type: {pattern_type}")
