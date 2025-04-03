from __future__ import annotations
from typing import (
    List, 
    Optional, 
    Union, 
    Dict, 
    Any, 
    Tuple,
    Sequence,
    cast
)
from pydantic import (
    BaseModel, 
    Field,
    ConfigDict
)

from note_gen.models.patterns import (
    NotePattern,
    NotePatternData,
    TransformationType,
    TransformationModel
)
from note_gen.models.note import Note
from note_gen.models.scale import Scale
from note_gen.core.enums import ScaleType, PatternDirection
from note_gen.models.note_event import NoteEvent
from note_gen.models.rhythm import RhythmNote, RhythmPattern
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.note_sequence import NoteSequence
from note_gen.models.scale_degree import ScaleDegree
from note_gen.models.base import BaseModelWithConfig  # Fixed import path

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

PatternElement = Union[int, str, Note, ScaleDegree, Dict[str, Any]]

@dataclass
class InterpreterContext:
    """Context for pattern interpretation."""
    scale: Scale
    velocity: int = 100
    position: float = 0.0
    duration: float = 1.0

class PatternInterpreter(BaseModel):
    """Base class for pattern interpreters."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )
    
    scale: Scale
    pattern: List[PatternElement]
    _current_index: int = 0

    def get_note_by_degree(self, degree: int, octave: int = 4) -> Note:
        """Get note by scale degree."""
        base_note = self.scale.get_note_by_degree(degree)
        return Note(
            note_name=base_note.note_name,
            octave=octave,
            duration=1.0,
            velocity=64
        )
    
    def interpret_pattern_item(
        self, 
        item: PatternElement,
        context: Optional[InterpreterContext] = None
    ) -> Optional[Note]:
        """
        Interpret a single pattern item.
        Returns None if the item should be skipped.
        """
        if context is None:
            context = InterpreterContext(scale=self.scale)

        try:
            if isinstance(item, Note):
                return item
            elif isinstance(item, int):
                if 0 <= item <= 127:  # Valid MIDI range
                    return Note.from_midi_number(
                        item,
                        velocity=context.velocity,
                        duration=context.duration,
                        position=context.position
                    )
                logger.warning(f"Invalid MIDI number: {item}")
                return None
            elif isinstance(item, str):
                if item.lower() in {'name', 'pattern', 'index', 'data', 
                                  'use_chord_tones', 'use_scale_mode', 
                                  'arpeggio_mode', 'restart_on_chord', 
                                  'direction'}:
                    return None
                return Note.from_full_name(
                    item,
                    duration=context.duration,
                    velocity=context.velocity,
                    position=context.position
                )
            elif isinstance(item, ScaleDegree):
                if item.value is not None:
                    return context.scale.get_note_by_degree(int(item.value))
                return None
            elif isinstance(item, dict):
                if 'midi' in item:
                    return Note.from_midi_number(
                        item['midi'],
                        duration=item.get('duration', context.duration),
                        position=item.get('position', context.position),
                        velocity=item.get('velocity', context.velocity)
                    )
                elif 'note' in item:
                    return Note.from_full_name(
                        item['note'],
                        duration=item.get('duration', context.duration),
                        position=item.get('position', context.position),
                        velocity=item.get('velocity', context.velocity)
                    )
            return None
        except ValueError as e:
            logger.warning(f"Error interpreting pattern item: {e}")
            return None

    def get_next_note(self) -> Note:
        """Get the next note in the pattern."""
        if not self.pattern:
            raise ValueError("Pattern is empty")

        note = None
        while note is None and self._current_index < len(self.pattern):
            element = self.pattern[self._current_index]
            note = self.interpret_pattern_item(element)
            self._current_index = (self._current_index + 1) % len(self.pattern)

        if note is None:
            raise ValueError("No valid notes found in pattern")
        
        return note

    def interpret(
        self,
        pattern: Sequence[PatternElement],
        chord: Optional[Any] = None,
        scale_info: Optional[ScaleInfo] = None,
        velocity: int = 100
    ) -> List[NoteEvent]:
        """Interpret a pattern into a sequence of NoteEvents."""
        context = InterpreterContext(
            scale=self.scale,
            velocity=velocity
        )
        
        note_events = []
        for element in pattern:
            note = self.interpret_pattern_item(element, context)
            if note is not None:
                note_events.append(NoteEvent(note=note, velocity=velocity))

        return note_events

    def reset(self) -> None:
        """Reset the pattern interpreter."""
        self._current_index = 0

class ScalePatternInterpreter(PatternInterpreter):
    """Interpreter for scale patterns."""

    @classmethod
    async def generate_note_sequence(
        cls,
        scale: Scale,
        note_pattern: NotePattern,
        rhythm_pattern: RhythmNote,
        chord_progression: Optional[ChordProgression] = None,
        scale_info: Optional[ScaleInfo] = None,
        progression_name: str = "",
        note_pattern_name: str = "",
        rhythm_pattern_name: str = ""
    ) -> NoteSequence:
        """Generate a note sequence."""
        default_scale_info = ScaleInfo(
            root=scale.root,
            notes=scale.get_scale_notes(),
            scale_type=scale.scale_type
        )
        
        sequence = NoteSequence(
            notes=[],
            scale_info=scale_info or default_scale_info,
            progression_name=progression_name,
            note_pattern_name=note_pattern_name,
            rhythm_pattern_name=rhythm_pattern_name
        )
        
        base_note = note_pattern.pattern[0]
        
        note = Note(
            note_name=base_note.note_name,
            octave=base_note.octave,
            duration=rhythm_pattern.duration,
            velocity=100,
            position=0.0
        )
        sequence.notes.append(note)
        
        return sequence

def create_pattern_interpreter(
    pattern: Sequence[PatternElement],
    scale: Scale,
    pattern_type: str = "scale",
) -> Union[PatternInterpreter, ScalePatternInterpreter]:
    """Create a pattern interpreter based on type."""
    pattern_list = list(pattern)
    if pattern_type == "scale":
        return ScalePatternInterpreter(scale=scale, pattern=pattern_list)
    return PatternInterpreter(scale=scale, pattern=pattern_list)
