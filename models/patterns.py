"""
Module for defining musical patterns.
"""
from typing import Any, List, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field

from models.chord import Chord
from models.note import Note
from models.scale_degree import ScaleDegree

DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]

class RhythmNote(BaseModel):
    """A single note in a rhythm pattern."""
    position: float = Field(default=0.0)
    duration: float = Field(default=1.0)
    velocity: float = Field(default=100.0)
    is_rest: bool = Field(default=False)
    accent: str | None = Field(default=None)
    swing_ratio: float | None = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def validate_velocity(cls, v: float) -> float:
        if not 0 <= v <= 127:
            raise ValueError("Velocity must be between 0 and 127")
        return v

    @classmethod
    def validate_duration(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v

    def get(self, key: str, default: Any | None = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def dict(self, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(**kwargs)

class RhythmPatternData(BaseModel):
    """Data for a rhythm pattern."""
    notes: List[RhythmNote] = Field(default_factory=list)
    duration: float = Field(default=0.0)
    time_signature: str = Field(default="4/4")
    swing_enabled: bool = Field(default=False)
    swing_ratio: float = Field(default=0.67)
    groove_type: str | None = Field(default=None)
    variation_probability: float = Field(default=0.0)
    humanize_amount: float = Field(default=0.0)
    accent_pattern: list[str] | None = Field(default=None)
    default_duration: float = Field(default=1.0)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def check_notes(cls, v) -> list[RhythmNote]:
        if not isinstance(v, list):
            raise ValueError("Notes must be a list")
        return [RhythmNote(**note) if isinstance(note, dict) else note for note in v]

    @classmethod
    def check_duration(cls, v) -> float:
        if v < 0:
            raise ValueError("Duration must be non-negative")
        return v

    @classmethod
    def check_time_signature(cls, v) -> str:
        if not isinstance(v, str) or '/' not in v:
            raise ValueError("Invalid time signature format")
        return v

    @classmethod
    def validate_swing_ratio(cls, v: float | None) -> float | None:
        if v is not None and not 0 <= v <= 1:
            raise ValueError("Swing ratio must be between 0 and 1")
        return v

    @classmethod
    def validate_variation_probability(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Variation probability must be between 0 and 1")
        return v

    @classmethod
    def validate_humanize_amount(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Humanize amount must be between 0 and 1")
        return v

    def _update_duration(self) -> None:
        if self.notes:
            self.duration = max(note.position + note.duration for note in self.notes)

    def apply_swing(self) -> None:
        if not self.swing_enabled:
            return
        for note in self.notes:
            if note.position % 1.0 == 0.5:  # Only apply to off-beats
                note.position += (self.swing_ratio - 0.5)

    def humanize(self) -> None:
        import random
        for note in self.notes:
            note.position += random.uniform(-self.humanize_amount, self.humanize_amount)
            note.velocity *= random.uniform(1 - self.humanize_amount, 1 + self.humanize_amount)

    def apply_groove(self) -> None:
        if not self.groove_type:
            return
        # Implement groove patterns here
        pass

    def apply_accents(self) -> None:
        if not self.accent_pattern:
            return
        for i, note in enumerate(self.notes):
            accent = self.accent_pattern[i % len(self.accent_pattern)]
            if accent == '>':
                note.velocity *= 1.2
            elif accent == '.':
                note.velocity *= 0.8

    def apply_variations(self) -> None:
        import random
        if random.random() < self.variation_probability:
            # Implement variations here
            pass

class RhythmPattern(BaseModel):
    """A pattern of rhythmic notes."""
    name: str = Field()
    data: RhythmPatternData = Field()
    description: Optional[str] = Field(default="")
    tags: list[str] = Field(default_factory=list)
    complexity: float = Field(default=1.0)
    style: str | None = Field(default=None)
    default_duration: float = Field(default=1.0)
    swing_enabled: bool = Field(default=False)
    swing_ratio: float = Field(default=0.67)
    groove_type: str | None = Field(default=None)
    variation_probability: float = Field(default=0.0)
    humanize_amount: float = Field(default=0.0)
    accent_pattern: list[str] | None = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def check_name(cls, v: str | None) -> str:
        if not v:
            raise ValueError("Name cannot be empty")
        return v

    @classmethod
    def check_data(cls, v: RhythmPatternData | dict[str, Any]) -> RhythmPatternData:
        if isinstance(v, dict):
            return RhythmPatternData(**v)
        return v

class NotePatternData(BaseModel):
    """Data class for note patterns."""
    notes: List[int] = Field(default_factory=list)
    intervals: List[int] = Field(default_factory=list)
    restart_on_chord: bool = Field(default=False)
    
    def get_notes(self) -> List[int]:
        """Get the notes in the pattern."""
        return self.notes
        
    def get_intervals(self) -> List[int]:
        """Get the intervals in the pattern."""
        return self.intervals
        
    def should_restart_on_chord(self) -> bool:
        """Check if pattern should restart on chord changes."""
        return self.restart_on_chord
        
    def check_notes(self, notes: List[int]) -> bool:
        """Check if notes are valid for this pattern."""
        return all(0 <= n < len(self.notes) for n in notes)
        
    def check_intervals(self, intervals: List[int]) -> bool:
        """Check if intervals are valid for this pattern."""
        return all(0 <= i < len(self.intervals) for i in intervals)

class NotePattern(BaseModel):
    """A pattern of musical notes."""
    name: str = Field()
    description: str = Field(default="")
    data: NotePatternData | list[int] | None = Field()
    notes: Optional[list[Note | ScaleDegree | Chord]] = Field(default=None)
    intervals: Optional[list[int]] = Field(default=None)
    duration: Optional[float] = Field(default=None)
    position: float | None = Field(default=None)
    velocity: int | None = Field(default=None)
    direction: DirectionType | None = Field(default=None)
    use_chord_tones: bool | None = Field(default=None)
    use_scale_mode: bool | None = Field(default=None)
    arpeggio_mode: bool | None = Field(default=None)
    restart_on_chord: bool | None = Field(default=None)
    octave_range: list[int] | None = Field(default=None)
    default_duration: float | None = Field(default=None)

    @classmethod
    def create(cls, name: str, data: NotePatternData) -> 'NotePattern':
        """Create a new NotePattern."""
        return cls(name=name, data=data)

    def model_dump(self, *, mode: Literal['json', 'python'] | str = 'json', include: Any | None = None,
                exclude: Any | None = None, context: Any | None = None, by_alias: bool = True,
                exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False,
                round_trip: bool = False, warnings: Literal['none', 'warn', 'error'] | bool = 'warn',
                serialize_as_any: bool = False) -> dict[str, Any]:
        """Dump model to dictionary."""
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any
        )
