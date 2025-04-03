"""Type stubs for patterns module."""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

from note_gen.models.chord import Chord
from note_gen.models.note import Note
from note_gen.models.scale_degree import ScaleDegree
from note_gen.models.patterns import NotePattern as NotePattern
from note_gen.models.patterns import NotePatternData as NotePatternData


DirectionType = str
ApproachType = str

NoteType = Union[Note, ScaleDegree, Chord]
PatternDataType = Union[List[int], Dict[str, Any], "NotePatternData"]

class RhythmNote:
    position: float = 0.0
    duration: float = 1.0
    velocity: float = 100.0
    is_rest: bool = False
    accent: Optional[str] = None
    swing_ratio: Optional[float] = None

    @classmethod
    def validate_velocity(cls, v: float) -> float: ...
    @classmethod
    def validate_duration(cls, v: float) -> float: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def __getitem__(self, key: str) -> Any: ...
    def dict(self, **kwargs: Any) -> Dict[str, Any]: ...

class RhythmPatternData:
    notes: List[RhythmNote] = []
    duration: float = 0.0
    time_signature: str = "4/4"
    swing_enabled: bool = False
    swing_ratio: float = 0.67
    groove_type: Optional[str] = None
    variation_probability: float = 0.0
    humanize_amount: float = 0.0
    accent_pattern: Optional[List[str]] = None
    default_duration: float = 1.0

    @classmethod
    def check_notes(cls, v: List[RhythmNote]) -> List[RhythmNote]: ...
    @classmethod
    def check_duration(cls, v: float) -> float: ...
    @classmethod
    def check_time_signature(cls, v: str) -> str: ...
    @classmethod
    def validate_swing_ratio(cls, v: Optional[float]) -> Optional[float]: ...
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

class RhythmPattern:
    name: str
    data: RhythmPatternData
    description: Optional[str] = ""
    tags: List[str] = []
    complexity: float = 1.0
    style: Optional[str] = None
    default_duration: float = 1.0
    swing_enabled: bool = False
    swing_ratio: float = 0.67
    groove_type: Optional[str] = None
    variation_probability: float = 0.0
    humanize_amount: float = 0.0
    accent_pattern: Optional[List[str]] = None
    id: Optional[str] = Field(None, description="ID of the rhythm pattern")
    is_test: Optional[bool] = Field(default=None, description="Test flag")

    @classmethod
    def check_name(cls, v: Optional[str]) -> str: ...
    @classmethod
    def check_data(
        cls, v: Union[RhythmPatternData, Dict[str, Any]]
    ) -> RhythmPatternData: ...
