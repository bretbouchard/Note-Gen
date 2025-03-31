from typing import List, Optional, Dict, Any, Sequence, Union, Tuple
from pydantic import BaseModel, Field

from src.note_gen.core.enums import ScaleType, ValidationLevel, ChordQuality
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionItem
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.core.constants import COMMON_PROGRESSIONS

# Add GENRE_PATTERNS constant
GENRE_PATTERNS: Dict[str, List[Tuple[int, ChordQuality]]] = {
    "pop": [(1, ChordQuality.MAJOR), (6, ChordQuality.MINOR), 
           (4, ChordQuality.MAJOR), (5, ChordQuality.MAJOR)],
    "jazz": [(2, ChordQuality.MINOR), (5, ChordQuality.DOMINANT_SEVENTH), 
            (1, ChordQuality.MAJOR_SEVENTH)],
    "blues": [(1, ChordQuality.DOMINANT_SEVENTH), (4, ChordQuality.DOMINANT_SEVENTH), 
             (5, ChordQuality.DOMINANT_SEVENTH)]
}

class ChordProgressionFactory(BaseModel):
    """Factory for creating chord progressions with different strategies."""
    
    scale_info: ScaleInfo
    validation_level: ValidationLevel = Field(default=ValidationLevel.NORMAL)

    @classmethod
    async def from_preset(
        cls,
        preset_name: str,
        key: str,
        scale_type: ScaleType,
        time_signature: tuple[int, int] = (4, 4)
    ) -> ChordProgression:
        """Create a progression from a preset pattern."""
        if preset_name not in COMMON_PROGRESSIONS:
            raise ValueError(f"Unknown preset: {preset_name}")
            
        preset = COMMON_PROGRESSIONS[preset_name]
        items = [
            ChordProgressionItem(
                chord=Chord(**chord_data),
                duration=1.0,
                position=float(i)
            )
            for i, chord_data in enumerate(preset["chords"])
        ]
        
        return ChordProgression(
            name=preset_name,
            key=key,
            scale_type=scale_type,
            items=items,
            total_duration=float(len(items))
        )

    @classmethod
    async def from_pattern(
        cls,
        pattern: Sequence[tuple[int, Union[str, ChordQuality]]],
        key: str,
        scale_type: ScaleType,
        name: Optional[str] = None
    ) -> ChordProgression:
        """Create a progression from a degree-quality pattern."""
        items: List[ChordProgressionItem] = []
        position = 0.0
        
        for degree, quality in pattern:
            chord = Chord(
                root=key,
                quality=ChordQuality(quality) if isinstance(quality, str) else quality
            )
            item = ChordProgressionItem(
                chord=chord,
                duration=1.0,
                position=position
            )
            items.append(item)
            position += 1.0

        return ChordProgression(
            name=name or "Pattern-Based Progression",
            key=key,
            scale_type=scale_type,
            items=items,
            total_duration=position
        )

    @classmethod
    async def from_genre(
        cls,
        genre: str,
        key: str,
        scale_type: ScaleType,
        length: int = 4
    ) -> ChordProgression:
        """Create a progression based on genre patterns."""
        if genre not in GENRE_PATTERNS:
            raise ValueError(f"Unsupported genre: {genre}")
            
        pattern = GENRE_PATTERNS[genre][:length]
        return await cls.from_pattern(
            pattern=pattern,
            key=key,
            scale_type=scale_type,
            name=f"{genre.title()} Progression"
        )

    @classmethod
    async def custom(
        cls,
        chord_data: List[Dict[str, Any]],
        key: str,
        scale_type: ScaleType,
        name: str = "Custom Progression"
    ) -> ChordProgression:
        """Create a progression from custom chord data."""
        items = []
        position = 0.0

        for data in chord_data:
            chord_item = ChordProgressionItem(
                chord=Chord(
                    root=data.get("root", key),
                    quality=data["quality"]
                ),
                duration=data.get("duration", 1.0),
                position=position
            )
            items.append(chord_item)
            position += chord_item.duration

        return ChordProgression(
            name=name,
            key=key,
            scale_type=scale_type,
            items=items,
            total_duration=position
        )
