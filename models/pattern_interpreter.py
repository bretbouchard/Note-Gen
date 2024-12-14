"""Module for interpreting musical patterns."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union
from pydantic import BaseModel, Field

from .note import Note
from .scale_degree import ScaleDegree
from .scale_info import ScaleInfo
from .scale import Scale

class PatternInterpreter:
    """Interprets musical patterns."""
    def __init__(self, scale: Scale, pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]) -> None:
        self.scale = scale
        self.pattern = pattern
        self._current_index = 0

    def get_next_note(self) -> Note:
        if not self.pattern:
            raise ValueError("Pattern is empty")
        result = self._interpret_current_element()
        self._current_index = (self._current_index + 1) % len(self.pattern)
        return result

    def reset(self) -> None:
        self._current_index = 0

    def _interpret_current_element(self) -> Note:
        element = self.pattern[self._current_index]
        if isinstance(element, Note):
            return element
        elif isinstance(element, ScaleDegree):
            return self.scale.get_scale_degree(element.value)
        return self.scale.get_scale_degree(1)

class ScalePatternInterpreter(PatternInterpreter):
    """Interpreter for scale patterns."""
    pass

class ArpeggioPatternInterpreter(PatternInterpreter):
    """Interpreter for arpeggio patterns."""
    pass

class MelodicPatternInterpreter(PatternInterpreter):
    """Interpreter for melodic patterns."""
    pass

def create_pattern_interpreter(pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]], scale: Scale, pattern_type: str = "scale") -> PatternInterpreter:
    """Create a pattern interpreter based on type."""
    if pattern_type == "arpeggio":
        return ArpeggioPatternInterpreter(scale=scale, pattern=pattern)
    elif pattern_type == "melodic":
        return MelodicPatternInterpreter(scale=scale, pattern=pattern)
    return ScalePatternInterpreter(scale=scale, pattern=pattern)
