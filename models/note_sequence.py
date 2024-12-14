"""
Module for handling sequences of notes.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel, Field

from .chord import Chord
from .note import Note
from .note_pattern import NotePattern, NotePatternData
from .pattern_interpreter import PatternInterpreter
from .scale_degree import ScaleDegree
from .scale_info import ScaleInfo

NoteType = Union[Note, ScaleDegree, Chord]
PatternElement = Union[int, str, Note, ScaleDegree, Dict[str, Any]]
PatternData = Union[NotePatternData, List[Union[int, Dict[str, Any]]]]
PatternSequence = Sequence[PatternElement]
PatternType = Sequence[Dict[str, Any]]
IntervalDict = Dict[str, Union[int, str, Note, ScaleDegree]]
PatternInterval = Union[int, IntervalDict]
PatternList = List[Dict[str, Any]]

T = TypeVar('T')

def ensure_list(items: Union[List[T], T]) -> List[T]:
    """Convert a sequence to a list."""
    if isinstance(items, list):
        return items
    return [items]

class NoteEvent(BaseModel):
    """A note event in a sequence."""
    note: NoteType
    duration: float = Field(default=1.0)
    velocity: int = Field(default=64)
    position: float = Field(default=0.0)

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = super().dict(*args, **kwargs)
        if isinstance(self.note, BaseModel):
            d['note'] = self.note.dict()
        return d

class NoteSequence(BaseModel):
    """A sequence of musical notes."""
    notes: List[NoteEvent] = Field(default_factory=list)
    current_position: float = Field(default=0.0)
    pattern: Optional[NotePattern] = Field(default=None)
    pattern_interpreter: Optional[PatternInterpreter] = Field(default=None)
    scale_info: Optional[ScaleInfo] = Field(default=None)

    def add_note(self, note: NoteType, duration: float = 1.0, velocity: int = 64, position: Optional[float] = None) -> None:
        """Add a note to the sequence."""
        if isinstance(note, (ScaleDegree, Chord)):
            note_obj = note.to_note()
        else:
            note_obj = note

        pos = position if position is not None else self.current_position
        event = NoteEvent(
            note=note_obj,
            duration=duration,
            velocity=velocity,
            position=pos
        )
        self.notes.append(event)
        self.current_position = pos + duration

    def get_next_note(self) -> Optional[NoteEvent]:
        """Get the next note in the sequence."""
        if not self.notes:
            return None
        return self.notes[0]

    def get_note_at(self, position: float) -> Optional[NoteEvent]:
        """Get the note at a specific position."""
        for event in self.notes:
            if abs(event.position - position) < 0.001:
                return event
        return None

    def get_notes_in_range(self, start: float, end: float) -> List[NoteEvent]:
        """Get all notes within a time range."""
        return [
            event for event in self.notes
            if start <= event.position < end
        ]

    def _convert_pattern_data(self, pattern_data: Union[NotePatternData, List[int]]) -> Sequence[Dict[str, Any]]:
        """Convert pattern data to a format suitable for pattern interpreter."""
        result: List[Dict[str, Any]] = []
        
        if isinstance(pattern_data, NotePatternData) and pattern_data.intervals:
            for interval in pattern_data.intervals:
                if isinstance(interval, int):
                    result.append({"interval": interval})
                elif isinstance(interval, dict):
                    result.append(interval)
                else:
                    result.append({"interval": int(interval)})
        elif isinstance(pattern_data, list):
            result = [{"interval": x} for x in pattern_data]
            
        return result

    def _create_pattern_interpreter(self, pattern_data: Union[NotePatternData, List[int]]) -> PatternInterpreter:
        """Create a pattern interpreter from pattern data."""
        if self.scale_info is None:
            raise ValueError("Scale info is required to create pattern interpreter")

        converted_data = self._convert_pattern_data(pattern_data)
        return create_pattern_interpreter(converted_data, self.scale_info.scale)

    def set_pattern(self, pattern: Union[List[int], NotePatternData, NotePattern]) -> None:
        """Set the pattern for the sequence."""
        if self.scale_info is None:
            raise ValueError("Scale info is required to set pattern")

        if isinstance(pattern, list):
            pattern_data = pattern
        elif isinstance(pattern, NotePattern):
            if isinstance(pattern.data, NotePatternData):
                pattern_data = pattern.data
            else:
                pattern_data = pattern.data if pattern.data is not None else []
        else:
            pattern_data = pattern

        self.pattern_interpreter = self._create_pattern_interpreter(pattern_data)

    def apply_pattern(self, pattern_data: Union[NotePatternData, List[int]], scale_info: Optional[ScaleInfo] = None) -> None:
        """Apply a pattern to the sequence."""
        if scale_info is not None:
            self.scale_info = scale_info

        if self.scale_info is None:
            raise ValueError("Scale info is required to apply pattern")

        self.pattern_interpreter = self._create_pattern_interpreter(pattern_data)

    def get_chord_notes(self, chord: Chord) -> List[Note]:
        """Get the notes from a chord."""
        return chord.get_notes()

    def add_chord(self, chord: Chord, duration: float = 1.0, velocity: int = 64, position: Optional[float] = None) -> None:
        """Add a chord to the sequence."""
        pos = position if position is not None else self.current_position
        notes = self.get_chord_notes(chord)
        for note in notes:
            self.add_note(note, duration, velocity, position=pos)

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = super().dict(*args, **kwargs)
        notes_dict = []
        for event in self.notes:
            event_dict = event.dict()
            if isinstance(event.note, BaseModel):
                event_dict['note'] = event.note.dict()
            notes_dict.append(event_dict)
        d['notes'] = notes_dict
        if self.scale_info:
            d['scale_info'] = self.scale_info.dict()
        return d

class NoteSequenceGenerator(BaseModel):
    """Generator for sequences of notes based on patterns."""
    scale_info: ScaleInfo
    pattern: NotePattern
    _interpreter: Optional[PatternInterpreter] = None
    _current_note: Optional[Note] = None
    current_index: int = Field(default=0)
    current_notes: List[Note] = Field(default_factory=list)

    def get_next_note(self) -> Note:
        """Get the next note in the sequence."""
        if not self._interpreter:
            pattern_data = self.pattern.data
            if not pattern_data:
                raise ValueError("Pattern data is empty")
            self._interpreter = create_pattern_interpreter(pattern_data, self.scale_info.scale)
        next_note = self._interpreter.get_next_note()
        if not next_note:
            raise ValueError("Failed to get next note from pattern")
        return next_note

    def get_notes(self, count: int = 1) -> List[Note]:
        """Get multiple notes from the sequence."""
        notes = []
        for _ in range(count):
            try:
                note = self.get_next_note()
                notes.append(note)
            except ValueError:
                break
        return notes

    def reset(self) -> None:
        """Reset the sequence to the beginning."""
        if self._interpreter:
            self._interpreter.reset()
        self.current_index = 0
        self.current_notes = []

    def get_chord_notes(self, chord: Union[Chord, Note, ScaleDegree]) -> List[Note]:
        """Get notes from a chord."""
        if isinstance(chord, Chord):
            return chord.get_notes()
        elif isinstance(chord, Note):
            return [chord]
        elif isinstance(chord, ScaleDegree):
            return [chord.to_note()]
        raise ValueError(f"Cannot get chord notes from {type(chord)}")

def generate_sequence_from_scale_based_params(
    chord_progression: Any,
    note_pattern: NotePattern,
    scale_info: ScaleInfo,
    rhythm_pattern: Optional[NotePattern] = None
) -> NoteSequence:
    """Generate a note sequence from scale-based parameters."""
    sequence = NoteSequence()
    sequence.scale_info = scale_info

    # Get the pattern interpreter
    if note_pattern.data:
        sequence.set_pattern(note_pattern)

    return sequence

class OctaveManager(BaseModel):
    """Manages octave ranges for note sequences."""
    min_octave: int = Field(default=-2)
    max_octave: int = Field(default=9)
    current_octave: int = Field(default=4)  # Default to middle octave

    def adjust_octave(self, note_value: int) -> int:
        """Adjust a note value to stay within the allowed octave range."""
        octave = note_value // 12
        if octave < self.min_octave:
            return note_value + ((self.min_octave - octave) * 12)
        if octave > self.max_octave:
            return note_value - ((octave - self.max_octave) * 12)
        return note_value

    def set_current_octave(self, octave: int) -> None:
        """Set the current octave."""
        if octave < self.min_octave or octave > self.max_octave:
            raise ValueError(f"Octave {octave} is outside allowed range ({self.min_octave}-{self.max_octave})")
        self.current_octave = octave

    def get_current_octave(self) -> int:
        """Get the current octave."""
        return self.current_octave

    def transpose_to_octave(self, note_value: int, target_octave: int) -> int:
        """Transpose a note to a specific octave."""
        current_octave = note_value // 12
        return note_value + ((target_octave - current_octave) * 12)

def note_name_to_midi(note_name: str) -> int:
    """Convert a note name to its corresponding MIDI note number."""
    if not isinstance(note_name, str):
        raise TypeError(f"Expected str, got {type(note_name).__name__}")
    
    # Remove any whitespace and convert to uppercase
    note_name = note_name.strip().upper()
    
    # Extract octave if present
    match = re.match(r'^([A-G][#b]?)(-?\d+)?$', note_name)
    if not match:
        raise ValueError(f"Invalid note name format: {note_name}")
        
    note, octave = match.groups()
    octave = octave if octave is not None else "4"  # Default to middle octave
    
    # Get base note value (0-11)
    base_note = NOTE_TO_MIDI.get(note)
    if base_note is None:
        raise ValueError(f"Invalid note name: {note}")
    
    return base_note + (int(octave) * 12)

NOTE_TO_MIDI: Dict[str, int] = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11
}

def _get_pattern_attr(pattern: Optional[Union[Any, List[int]]], attr: str, default: Any = None) -> bool:
    """Safely get an attribute from a pattern object."""
    if pattern is None:
        return False
    try:
        value = getattr(pattern, attr, default)
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return bool(value.strip())
        return bool(value)
    except (AttributeError, TypeError):
        return False

def _safe_numeric_op(value: Union[str, int, float, None], default: Union[int, float] = 0) -> Union[int, float]:
    """Safely perform numeric operations on potentially None or string values."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value) if isinstance(default, float) else int(value)
    except (ValueError, TypeError):
        return default

def _safe_compare(a: Any, b: Any, default: bool = False) -> bool:
    """Safely compare two values that might be None or different types."""
    if a is None or b is None:
        return default
    try:
        return bool(a > b)
    except TypeError:
        return default

def compare_timings(a: Union[str, int, None], b: Union[str, int, None]) -> bool:
    """Compare timing values safely."""
    return bool(_safe_compare(
        _safe_numeric_op(a),
        _safe_numeric_op(b)
    ))

def adjust_timing(timing: Union[str, int, None], adjustment: int) -> int:
    """Adjust timing value safely."""
    base = _safe_numeric_op(timing, 0)
    return int(base + adjustment)

def create_pattern_interpreter(pattern: PatternSequence, scale: ScaleInfo) -> PatternInterpreter:
    # Implementation here
    pass
