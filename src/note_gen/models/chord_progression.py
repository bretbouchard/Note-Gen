"""Chord progression model."""
from typing import List, Optional, ClassVar
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseModelWithConfig
from .chord import Chord
from .scale_info import ScaleInfo
from ..core.enums import ScaleType, ChordQuality
from ..core.constants import ROMAN_TO_INT

class ChordProgressionItem(BaseModelWithConfig):
    """Model for a single chord in a progression."""
    chord: Chord
    duration: float = Field(default=1.0, ge=0.0)
    position: float = Field(default=0.0, ge=0.0)
    is_primary: bool = Field(default=False)

    @classmethod
    def create(cls, root: str, quality: ChordQuality, duration: float = 1.0, position: float = 0.0):
        """Factory method to create a ChordProgressionItem."""
        return cls(
            chord=Chord(root=root, quality=quality),
            duration=duration,
            position=position
        )

class ChordProgression(BaseModelWithConfig):
    """Model for chord progressions."""
    name: str = Field(default="")
    key: str = Field(default="C")
    scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    scale_info: Optional[ScaleInfo] = None
    items: List[ChordProgressionItem] = Field(default_factory=list)
    pattern: List[str] = Field(default_factory=list)
    total_duration: float = Field(default=4.0, ge=0.0)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
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
        
        progression = cls(
            name=name,
            key=key,
            scale_type=scale_type,
            scale_info=scale_info,
            pattern=pattern,
            items=[]
        )
        
        # Convert pattern to chords
        position = 0.0
        for degree in pattern:
            # Convert roman numeral to chord
            scale_degree = ROMAN_TO_INT.get(degree.upper())
            if scale_degree is None:
                continue
            
            # Get the chord root based on scale degree
            root = scale_info.get_scale_notes()[scale_degree - 1]
            
            # Create chord based on scale degree
            chord = Chord(root=root, quality=ChordQuality.MAJOR)  # Simplified for now
            
            # Add to progression
            progression.add_chord(chord=chord, position=position)
            position += 1.0
        
        return progression

    @classmethod
    def from_pattern(cls, pattern: List[str], scale_info: ScaleInfo) -> "ChordProgression":
        """Create a chord progression from a pattern and scale info.
        
        Args:
            pattern: List of roman numerals (e.g., ["I", "IV", "V", "vi"])
            scale_info: Scale information for the progression
        
        Returns:
            A new ChordProgression instance
        """
        return cls(
            name="",  # Default name
            key=scale_info.key,
            scale_type=scale_info.scale_type,
            scale_info=scale_info,
            pattern=pattern,
            items=[]  # Items will be generated later
        )

    def add_chord(self, chord: Chord, duration: float = 1.0, position: Optional[float] = None) -> None:
        """Add a chord to the progression."""
        if position is None:
            position = sum(item.duration for item in self.items)
        
        self.items.append(
            ChordProgressionItem(
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


