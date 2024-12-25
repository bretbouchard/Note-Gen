"""Data structures for musical note patterns."""

from __future__ import annotations

from typing import Any, Literal, Optional, Union, List, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale_degree import ScaleDegree


# Type aliases
DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]
NoteType = Union["Note", "ScaleDegree", "Chord"]
PatternDataType = Union[List[int], Dict[str, Any], "NotePatternData"]
# Integrate PatternDataType for rhythm and note patterns to ensure clarity and maintainability.
# This will help differentiate between the two types and facilitate future expansions.
# Integrate PatternDataType for rhythm and note patterns to ensure clarity and maintainability.
# This will help differentiate between the two types and facilitate future expansions.


class NotePatternData(BaseModel):
    """Data structure for note patterns."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    notes: List[NoteType] = Field(
        default_factory=list, description="List of notes in the pattern"
    )
    intervals: Optional[List[int]] = Field(
        default=None, description="List of intervals between notes"
    )
    position: float = Field(default=0.0, description="Position of the pattern")
    velocity: Optional[int] = Field(default=None, description="Velocity of the pattern")
    direction: Optional[DirectionType] = Field(
        default=None, description="Direction of the pattern"
    )
    use_chord_tones: bool = Field(
        default=False, description="Whether to use chord tones"
    )
    use_scale_mode: bool = Field(default=False, description="Whether to use scale mode")
    arpeggio_mode: bool = Field(
        default=False, description="Whether to use arpeggio mode"
    )
    restart_on_chord: bool = Field(
        default=False, description="Whether to restart on chord"
    )
    octave_range: Optional[List[int]] = Field(
        default=None, description="Range of octaves for the pattern"
    )

    def __init__(
        self,
        *,
        notes: List[NoteType],
        intervals: Optional[List[int]] = None,
        position: float = 0.0,
        velocity: Optional[int] = None,
        direction: Optional[DirectionType] = None,
        use_chord_tones: bool = False,
        use_scale_mode: bool = False,
        arpeggio_mode: bool = False,
        restart_on_chord: bool = False,
        octave_range: Optional[List[int]] = None,
    ) -> None:
        super().__init__(
            notes=notes,
            intervals=intervals,
            position=position,
            velocity=velocity,
            direction=direction,
            use_chord_tones=use_chord_tones,
            use_scale_mode=use_scale_mode,
            arpeggio_mode=arpeggio_mode,
            restart_on_chord=restart_on_chord,
            octave_range=octave_range,
        )

    @field_validator("notes")
    @classmethod
    def check_notes(cls, v: List[NoteType]) -> List[NoteType]:
        if not all(isinstance(note, (Note, ScaleDegree, Chord)) for note in v):
            raise ValueError(
                "All items in notes must be instances of Note, ScaleDegree, or Chord."
            )
        return v


class NotePattern(BaseModel):
    """A musical pattern with transformation capabilities."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Name of the pattern")
    description: str = Field(default="", description="Description of the pattern")
    data: Optional[Union[NotePatternData, List[int]]] = Field(
        ..., description="Pattern data"
    )
    notes: Optional[List[NoteType]] = Field(
        default=None, description="List of notes in the pattern"
    )
    intervals: Optional[List[int]] = Field(
        default=None, description="List of intervals between notes"
    )
    duration: Optional[float] = Field(
        default=None, description="Duration of the pattern"
    )
    position: Optional[float] = Field(
        default=None, description="Position of the pattern"
    )
    velocity: Optional[int] = Field(default=None, description="Velocity of the pattern")
    direction: Optional[DirectionType] = Field(
        default=None, description="Direction of the pattern"
    )
    use_chord_tones: Optional[bool] = Field(
        default=None, description="Whether to use chord tones"
    )
    use_scale_mode: Optional[bool] = Field(
        default=None, description="Whether to use scale mode"
    )
    arpeggio_mode: Optional[bool] = Field(
        default=None, description="Whether to use arpeggio mode"
    )
    restart_on_chord: Optional[bool] = Field(
        default=None, description="Whether to restart on chord"
    )
    octave_range: Optional[List[int]] = Field(
        default=None, description="Range of octaves to use"
    )
    default_duration: Optional[float] = Field(
        default=None, description="Default duration for note patterns"
    )

    @classmethod
    def create(cls, name: str, data: NotePatternData) -> NotePattern:
        """Create a new NotePattern instance."""
        return cls(name=name, data=data)

    def get_notes(self) -> List[NoteType]:
        """Get the list of notes in the pattern."""
        return self.notes or []

    def get_intervals(self) -> List[int]:
        """Get the list of intervals in the pattern."""
        return self.intervals or []

    def get_duration(self) -> Optional[float]:
        """Get the duration of the pattern."""
        return self.duration

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override dict method to include additional fields if necessary."""
        return super().dict(*args, **kwargs)

    def initialize_models(self) -> None:
        """Initialize models for the pattern."""
        # Implementation for initializing models
        pass

    def __str__(self) -> str:
        return f"NotePattern(name={self.name}, description={self.description})"


def get_pattern_notes(pattern: List[int], notes: List[NoteType]) -> List[NoteType]:
    """Get notes from a pattern. Returns a list of notes or raises an error if pattern is invalid."""
    if not check_pattern_notes(pattern, notes):
        raise ValueError("Invalid pattern or notes")
    return [notes[i] for i in pattern if 0 <= i < len(notes)]


def check_pattern_notes(pattern: List[int], notes: List[NoteType]) -> bool:
    """Check if pattern notes are valid. Returns True if all notes are valid, otherwise False."""
    return all(isinstance(i, int) for i in pattern) and all(
        0 <= i < len(notes) for i in pattern
    )


def check_pattern_intervals(pattern: List[int], intervals: List[int]) -> bool:
    """Check if pattern intervals are valid. Returns True if all intervals are valid, otherwise False."""
    return all(isinstance(i, int) for i in pattern + intervals)


def setup_models() -> None:
    NotePatternData.model_rebuild()


def initialize_models() -> None:
    setup_models()
    NotePatternData.model_rebuild()


# Method to get a chord at a specific index. Not yet implemented. This will allow access to chords like 'vii7' or 'v' in the scale.
# Implement this method to enhance functionality.
# def get_chord_at(index: int) -> Chord:
#     pass

initialize_models()  # Call this at the end to ensure all models are defined before rebuilding
