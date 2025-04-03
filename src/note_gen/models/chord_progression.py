"""Chord progression model."""
from typing import List, Optional, Tuple
from pydantic import Field, ConfigDict
from .base import BaseModelWithConfig
from .chord import Chord
from .scale_info import ScaleInfo
from ..core.enums import ScaleType
from .chord_progression_item import ChordProgressionItem  # Import the correct model

class ChordProgression(BaseModelWithConfig):
    """Model for chord progressions."""
    id: Optional[str] = Field(default=None)
    name: str = Field(default="")
    key: str = Field(default="C")
    root_note: Optional[str] = Field(default=None)
    scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    scale_info: Optional[ScaleInfo] = None
    chords: List[Chord] = Field(default_factory=list)
    items: List[ChordProgressionItem] = Field(default_factory=list)
    pattern: List[str] = Field(default_factory=list)
    total_duration: float = Field(default=4.0, ge=0.0)
    time_signature: Tuple[int, int] = Field(default=(4, 4))
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    quality: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    @classmethod
    def generate_progression_from_pattern(
        cls,
        pattern: List[str],
        key: str,
        name: str = "",
        scale_type: ScaleType = ScaleType.MAJOR,
        scale_info: Optional[ScaleInfo] = None
    ) -> "ChordProgression":
        """Generate a chord progression from a pattern."""
        if scale_info is None:
            scale_info = ScaleInfo(key=key, scale_type=scale_type)

        return cls(
            name=name,
            key=key,
            scale_type=scale_type,
            scale_info=scale_info,
            pattern=pattern,
            items=[]
        )

    @classmethod
    def from_pattern(cls, pattern: List[str], scale_info: ScaleInfo) -> "ChordProgression":
        """Create a chord progression from a pattern and scale info."""
        return cls(
            name="",
            key=scale_info.key,
            scale_type=scale_info.scale_type,
            scale_info=scale_info,
            pattern=pattern,
            items=[]
        )

    def add_chord(self, chord: Chord, duration: float = 1.0, position: Optional[float] = None) -> None:
        """Add a chord to the progression."""
        if position is None:
            position = sum(item.duration for item in self.items)

        self.items.append(
            ChordProgressionItem(
                chord_symbol=chord.to_symbol(),
                chord=chord,
                duration=duration,
                position=position
            )
        )
        self.total_duration = max(self.total_duration, position + duration)

    def get_chord_at_position(self, position: float) -> Optional[Chord]:
        """Get the chord at a specific position in the progression."""
        for item in self.items:
            if item.position <= position < (item.position + item.duration):
                return item.chord
        return None


