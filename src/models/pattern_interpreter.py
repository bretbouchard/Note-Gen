"""Module for interpreting musical patterns.

This module provides classes and functions for interpreting musical patterns, including scale patterns and rhythmic patterns. It allows for the generation of musical sequences based on defined patterns and scales.

Pattern Interpretation
----------------------

The classes in this module are designed to interpret various musical patterns, enabling the generation of sequences that adhere to specific musical rules. They provide a flexible framework for working with musical patterns, making it easier to create complex musical compositions.

Classes:
--------

- `PatternInterpreter`: A base class for all pattern interpreters. It defines the interface for interpreting musical patterns and generating sequences.
- `ScalePatternInterpreter`: A subclass of `PatternInterpreter` that specifically interprets scale patterns and generates sequences based on scale information.
- `ArpeggioPatternInterpreter`: A subclass of `PatternInterpreter` that specifically interprets arpeggio patterns.
- `MelodicPatternInterpreter`: A subclass of `PatternInterpreter` that specifically interprets melodic patterns.

Usage:
------

To use the pattern interpreter, create an instance of a specific interpreter class (e.g., `ScalePatternInterpreter`) and call the `get_next_note` method with the appropriate pattern data. This will return a generated sequence based on the provided patterns and scales.

Examples:
---------

```python
# Example of using the ScalePatternInterpreter
scale_info = ...  # Define your scale information here
pattern_data = ...  # Define your pattern data here
interpreter = ScalePatternInterpreter(scale=scale_info, pattern=pattern_data)
sequence = []
while True:
    try:
        sequence.append(interpreter.get_next_note())
    except ValueError:
        break
```

This module is designed to be extensible, allowing for the addition of new pattern interpreters as needed."""

from __future__ import annotations

from typing import Any, Dict, Sequence, Union
import logging

logger = logging.getLogger(__name__)

from pydantic import BaseModel, ConfigDict
from .note import Note
from .scale_degree import ScaleDegree
from .scale import Scale

class PatternInterpreter(BaseModel):
    """Base class for pattern interpreters.

    This class defines the interface for interpreting musical patterns. Subclasses should implement the methods for generating sequences based on specific pattern types.

    Attributes:
        scale (Scale): The scale to use for interpretation.
        pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        _current_index (int): The current index in the pattern. Defaults to 0.
    """

    scale: Scale
    pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]
    _current_index: int = 0

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, scale: Scale, pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]) -> None:
        """Initialize PatternInterpreter with a scale and pattern.

        Args:
            scale (Scale): The scale to use for interpretation.
            pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.

        Raises:
            ValueError: If the scale is not an instance of Scale or if the pattern is empty.
        """
        if not isinstance(scale, Scale):
            raise ValueError("Scale must be an instance of Scale.")
        if not pattern:
            raise ValueError("Pattern cannot be empty.")
        super().__init__(scale=scale, pattern=pattern)
        self.scale = scale
        self.pattern = pattern
        self._current_index = 0

    def get_next_note(self) -> Note:
        """Get the next note in the pattern. Raises an error if the pattern is empty.

        Returns:
            Note: The next note in the pattern.

        Raises:
            ValueError: If the pattern is empty.
        """
        if not self.pattern:
            raise ValueError("Pattern is empty. Cannot retrieve next note.")
        result = self._interpret_current_element()
        self._current_index = (self._current_index + 1) % len(self.pattern)
        return result

    def reset(self) -> None:
        """Reset the pattern interpreter to the beginning of the pattern."""
        self._current_index = 0

    def _interpret_current_element(self) -> Note:
        """Interpret the current element in the pattern.

        Returns:
            Note: The interpreted note.
        """
        element = self.pattern[self._current_index]
        if element is None:
            logger.error("Current element is None.")
            raise ValueError("Current element cannot be None.")
        if isinstance(element, Note):
            return element
        elif isinstance(element, ScaleDegree):
            if element.value is None:
                logger.error("ScaleDegree value is None.")
                raise ValueError("ScaleDegree value cannot be None.")
            return self.scale.get_scale_degree(element.value)
        return self.scale.get_scale_degree(1)

class ScalePatternInterpreter(PatternInterpreter):
    """Interpreter for scale patterns.

    This class interprets scale patterns and generates musical sequences based on the provided scale information."""

    def __init__(self, scale: Scale, pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]) -> None:
        """Initialize the scale pattern interpreter.

        Args:
            scale (Scale): The scale to use for interpretation.
            pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        """
        super().__init__(scale=scale, pattern=pattern)

class ArpeggioPatternInterpreter(PatternInterpreter):
    """Interpreter for arpeggio patterns."""

    def __init__(self, scale: Scale, pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]) -> None:
        """Initialize the arpeggio pattern interpreter.

        Args:
            scale (Scale): The scale to use for interpretation.
            pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        """
        super().__init__(scale=scale, pattern=pattern)

class MelodicPatternInterpreter(PatternInterpreter):
    """Interpreter for melodic patterns."""

    def __init__(self, scale: Scale, pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]) -> None:
        """Initialize the melodic pattern interpreter.

        Args:
            scale (Scale): The scale to use for interpretation.
            pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        """
        super().__init__(scale=scale, pattern=pattern)

def create_pattern_interpreter(pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]], scale: Scale, pattern_type: str = "scale") -> PatternInterpreter:
    """Create a pattern interpreter based on type.

    Args:
        pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        scale (Scale): The scale to use for interpretation.
        pattern_type (str, optional): The type of pattern interpreter to create. Defaults to "scale".

    Returns:
        PatternInterpreter: The created pattern interpreter.
    """
    if pattern_type == "arpeggio":
        return ArpeggioPatternInterpreter(scale=scale, pattern=pattern)
    elif pattern_type == "melodic":
        return MelodicPatternInterpreter(scale=scale, pattern=pattern)
    return ScalePatternInterpreter(scale=scale, pattern=pattern)
