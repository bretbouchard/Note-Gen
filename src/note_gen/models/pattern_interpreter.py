from __future__ import annotations
from pydantic import BaseModel, ConfigDict, field_validator
from src.note_gen.models.note import Note
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.scale import Scale

from typing import Any, Dict, Sequence, Union, List, Optional
import logging

logger = logging.getLogger(__name__)

from .patterns import NotePattern, RhythmPatternData
from .chord_progression import ChordProgression
from .note_sequence import NoteSequence


class PatternInterpreter(BaseModel):
    """Base class for pattern interpreters.

    This class defines the interface for interpreting musical patterns. Subclasses should implement the methods for generating sequences based on specific pattern types.

    Attributes:
        scale (Scale): The scale to use for interpretation.
        pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        _current_index (int): The current index in the pattern. Defaults to 0.
    """

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
    scale: Scale
    pattern: List[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]
    _current_index: int = 0

    def __init__(
        self,
        scale: Scale,
        pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]],
    ) -> None:
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
        
        # Convert pattern elements to the correct types
        valid_elements = []
        for element in pattern:
            if isinstance(element, (int, str, Note, ScaleDegree, dict)):
                valid_elements.append(element)
            elif hasattr(element, 'note_name') and hasattr(element, 'octave'):
                # Convert Note-like objects to Note instances
                valid_elements.append(Note(
                    note_name=element.note_name,
                    octave=element.octave,
                    duration=getattr(element, 'duration', 1.0),
                    velocity=getattr(element, 'velocity', 100)
                ))
            else:
                raise ValueError(f"Invalid pattern element type: {type(element)}")
        
        super().__init__(scale=scale, pattern=valid_elements)

    def get_next_note(self) -> Note:
        """Get the next note in the pattern. Raises an error if the pattern is empty."""
        if not self.pattern:
            raise ValueError("Pattern is empty")

        # Get the current element
        element = self.pattern[self._current_index]

        # Convert element to Note if needed
        if isinstance(element, Note):
            note = element
        elif isinstance(element, ScaleDegree):
            if element.value is not None:
                note = self.scale.get_scale_degree(int(element.value))
            else:
                raise ValueError("ScaleDegree value cannot be None")
        elif isinstance(element, int):
            note = Note.from_midi(element, velocity=64, duration=1)
        elif isinstance(element, str):
            note = Note.from_full_name(element)
        else:
            raise ValueError(f"Unsupported element type: {type(element)}")

        # Check if note is an instance of Note
        if not isinstance(note, Note):
            raise TypeError("Expected a Note instance")

        # Increment index and wrap around
        self._current_index = (self._current_index + 1) % len(self.pattern)

        return note

    def interpret(self, pattern: Sequence[Union[int, str, Note, ScaleDegree]], chord: Any, scale_info: Any, velocity: int = 100) -> List[NoteEvent]:
        """Interpret a pattern into a sequence of NoteEvents."""
        note_events = []
        for element in pattern:
            # Handle dictionary inputs by skipping non-note keys
            if isinstance(element, dict):
                continue

            # Handle string inputs that are not valid note names
            if isinstance(element, str) and element.lower() in ['name', 'pattern', 'index', 'data', 'use_chord_tones', 'use_scale_mode', 'arpeggio_mode', 'restart_on_chord', 'direction']:
                continue

            # Handle Note instances
            if isinstance(element, Note):
                note_events.append(NoteEvent(note=element, velocity=velocity))
            
            # Handle ScaleDegree
            elif isinstance(element, ScaleDegree):
                if element.value is not None:
                    note = scale_info.get_scale_degree(int(element.value))
                    note_events.append(NoteEvent(note=note, velocity=velocity))
                else:
                    raise ValueError("ScaleDegree value cannot be None")
            
            # Handle MIDI numbers
            elif isinstance(element, int):
                # Validate MIDI number range
                if 0 <= element <= 127:
                    note = Note.from_midi(element, velocity=velocity, duration=1)
                    note_events.append(NoteEvent(note=note, velocity=velocity))
                else:
                    logger.warning(f"Skipping invalid MIDI number: {element}")
            
            # Handle string note names
            elif isinstance(element, str):
                try:
                    note = Note.from_full_name(element)
                    note_events.append(NoteEvent(note=note, velocity=velocity))
                except ValueError:
                    logger.warning(f"Skipping invalid note name: {element}")
            
            else:
                logger.warning(f"Unsupported element type: {type(element)}")

        return note_events

    def reset(self) -> None:
        """Reset the pattern interpreter to the beginning of the pattern."""
        self._current_index = 0

    def _interpret_current_element(self) -> Note:
        element = self.pattern[self._current_index]
        if element is None:
            raise ValueError("Current element cannot be None")

        # If it's already a Note instance, just return it
        if isinstance(element, Note):
            return element
        
        # If it's a ScaleDegree, convert it to a Note using the scale
        if isinstance(element, ScaleDegree):
            return self.scale.get_scale_degree(element.value)
            
        # If it's an int, treat it as a MIDI note number
        if isinstance(element, int):
            return Note.from_midi(element, velocity=100, duration=1)
            
        # If it's a str, parse it into a Note
        if isinstance(element, str):
            return Note.from_full_name(element)
            
        raise ValueError(f"Unsupported pattern element type: {type(element)}")

    def process(self) -> List[Note]:
        """Process the pattern based on the current scale and generate musical sequences."""
        result = []

        for element in self.pattern:
            if isinstance(element, Note):
                result.append(element)
            elif isinstance(element, ScaleDegree):
                note = self.scale.get_scale_degree(int(element.value)) if isinstance(element.value, str) and element.value.isdigit() else None
            elif isinstance(element, int):
                note = Note.from_midi(
                    element, velocity=64, duration=1
                )  # Assuming a method exists to create Note from MIDI number
                result.append(note)
            elif isinstance(element, str):
                note = Note.from_full_name(
                    element
                )  # Assuming a method exists to create Note from full name
                result.append(note)
            else:
                raise ValueError(f"Unsupported pattern element type: {type(element)}")

        return result


class ScalePatternInterpreter(PatternInterpreter):
    """Interpreter for scale patterns.

    This class interprets scale patterns and generates musical sequences based on the provided scale information.
    """

    def __init__(
        self,
        scale: Scale,
        pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]],
    ) -> None:
        """Initialize the scale pattern interpreter.

        Args:
            scale (Scale): The scale to use for interpretation.
            pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        """
        super().__init__(scale=scale, pattern=pattern)

    @classmethod
    async def generate_note_sequence(
        cls,
        scale: Scale,
        note_pattern: NotePattern,
        rhythm_pattern: RhythmPatternData,
        chord_progression: Optional[ChordProgression] = None
    ) -> NoteSequence:
        """Generate a note sequence using the given scale, patterns and optional chord progression."""
        # Initialize the sequence with empty notes list
        sequence = NoteSequence(notes=[])
        
        # Get the base note from the pattern
        base_note = note_pattern.notes[0]
        
        # Create single note from rhythm pattern base duration
        note = Note(
            note_name=base_note.note_name,
            octave=base_note.octave,
            duration=rhythm_pattern.default_duration,
            velocity=100  # Use default velocity
        )
        sequence.notes.append(note)
        
        return sequence


class ArpeggioPatternInterpreter(PatternInterpreter):
    """Interpreter for arpeggio patterns."""

    def __init__(
        self,
        scale: Scale,
        pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]],
    ) -> None:
        """Initialize the arpeggio pattern interpreter.

        Args:
            scale (Scale): The scale to use for interpretation.
            pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        """
        super().__init__(scale=scale, pattern=pattern)


class MelodicPatternInterpreter(PatternInterpreter):
    """Interpreter for melodic patterns."""

    def __init__(
        self,
        scale: Scale,
        pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]],
    ) -> None:
        """Initialize the melodic pattern interpreter.

        Args:
            scale (Scale): The scale to use for interpretation.
            pattern (Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]): The pattern to interpret.
        """
        super().__init__(scale=scale, pattern=pattern)


def create_pattern_interpreter(
    pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]],
    scale: Scale,
    pattern_type: str = "scale",
) -> PatternInterpreter:
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
