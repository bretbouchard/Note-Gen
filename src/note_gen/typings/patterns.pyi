"""Type stubs for patterns module."""
from typing import List, Any, Optional, Union, Literal, ClassVar

from pydantic import BaseModel, ConfigDict

from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.scale_degree import ScaleDegree

DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]

class RhythmNote(BaseModel):
    position: float = 0.0
    duration: float = 1.0
    velocity: float = 100.0
    is_rest: bool = False
    accent: str | None = None
    swing_ratio: float | None = None
    model_config: ClassVar[ConfigDict]

    @classmethod
    def validate_velocity(cls, v: float) -> float: ...
    @classmethod
    def validate_duration(cls, v: float) -> float: ...
    def get(self, key: str, default: Any | None = None) -> Any: ...
    def __getitem__(self, key: str) -> Any: ...
    def dict(self, **kwargs: Any) -> dict[str, Any]: ...

class RhythmPatternData(BaseModel):
    notes: List[RhythmNote] = []
    duration: float = 0.0
    time_signature: str = "4/4"
    swing_enabled: bool = False
    swing_ratio: float = 0.67
    groove_type: str | None = None
    variation_probability: float = 0.0
    humanize_amount: float = 0.0
    accent_pattern: list[str] | None = None
    default_duration: float = 1.0
    model_config: ClassVar[ConfigDict]

    @classmethod
    def check_notes(cls, v: list[RhythmNote]) -> list[RhythmNote]: ...
    @classmethod
    def check_duration(cls, v: float) -> float: ...
    @classmethod
    def check_time_signature(cls, v: str) -> str: ...
    @classmethod
    def validate_swing_ratio(cls, v: float | None) -> float | None: ...
    @classmethod
    def validate_variation_probability(cls, v: float) -> float: ...
    @classmethod
    def validate_humanize_amount(cls, v: float) -> float: ...
    def _update_duration(self) -> None: ...
    def apply_swing(self) -> None: ...
    def humanize(self) -> None: ...
    def apply_groove(self) -> None: ...
    def apply_accents(self) -> None: ...
    def apply_variations(self) -> None: ...

    @property
    def time_signature_numerator(self) -> int: ...

    @property
    def time_signature_denominator(self) -> int: ...

    @property
    def total_duration(self) -> float: ...

class RhythmPattern(BaseModel):
    name: str
    data: RhythmPatternData
    description: Optional[str] = ""
    tags: list[str] = []
    complexity: float = 1.0
    style: str | None = None
    default_duration: float = 1.0
    swing_enabled: bool = False
    swing_ratio: float = 0.67
    groove_type: str | None = None
    variation_probability: float = 0.0
    humanize_amount: float = 0.0
    accent_pattern: list[str] | None = None
    model_config: ClassVar[ConfigDict]

    def __init__(self, pattern: str | list[str], name: str | None = None, description: str | None = None) -> None: ...
    @classmethod
    def check_name(cls, v: str | None) -> str: ...
    @classmethod
    def check_data(cls, v: RhythmPatternData | dict[str, Any]) -> RhythmPatternData: ...
    @classmethod
    def from_pattern(cls, pattern: str | list[str], name: str | None = None, description: str | None = None) -> RhythmPattern: ...
    @classmethod
    def validate_pattern(cls, pattern: str | list[str]) -> str | list[str]: ...

class NotePatternData(BaseModel):
    model_config: ClassVar[ConfigDict]
    notes: List[Union[Note, ScaleDegree, Chord]] = []
    intervals: list[int] | None = None
    duration: float = 1.0
    position: float = 0.0
    velocity: int | None = None
    direction: DirectionType = "forward"
    use_chord_tones: bool = False
    use_scale_mode: bool = False
    arpeggio_mode: bool = False
    restart_on_chord: bool = False
    octave_range: list[int] | None = None
    default_duration: float = 1.0

    def get_notes(self) -> List[Union[Note, ScaleDegree, Chord]]: ...
    def get_intervals(self) -> list[int] | None: ...
    def should_restart_on_chord(self) -> bool: ...
    @classmethod
    def check_notes(cls, v: List[Union[Note, ScaleDegree, Chord]]) -> List[Union[Note, ScaleDegree, Chord]]: ...
    @classmethod
    def check_intervals(cls, v: list[int] | None) -> list[int] | None: ...
    def check_restart_on_chord(self, v: bool) -> bool: ...

class NotePattern(BaseModel):
    model_config: ClassVar[ConfigDict]
    name: str
    description: str = ""
    data: NotePatternData | list[int] | None
    notes: Optional[list[Note | ScaleDegree | Chord]] = None
    intervals: Optional[list[int]] = None
    duration: Optional[float] = None
    position: float | None = None
    velocity: int | None = None
    direction: DirectionType | None = None
    use_chord_tones: bool | None = None
    use_scale_mode: bool | None = None
    arpeggio_mode: bool | None = None
    restart_on_chord: bool | None = None
    octave_range: list[int] | None = None
    default_duration: float | None = None

    def __init__(self, pattern: str | list[str], name: str | None = None, description: str | None = None) -> None: ...
    @classmethod
    def create(cls, name: str, data: NotePatternData) -> NotePattern: ...
    def model_dump(self, *, mode: Literal['json', 'python'] | str = 'json', include: Any | None = None,
                exclude: Any | None = None, context: Any | None = None, by_alias: bool = True,
                exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False,
                round_trip: bool = False, warnings: Literal['none', 'warn', 'error'] | bool = 'warn',
                serialize_as_any: bool = False) -> dict[str, Any]: ...
