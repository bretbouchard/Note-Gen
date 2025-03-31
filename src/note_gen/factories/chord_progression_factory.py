from typing import List, Optional, Dict, Any, Sequence, Union, Tuple, TypedDict, ClassVar
from pydantic import BaseModel, Field

from src.note_gen.core.enums import ScaleType, ValidationLevel, ChordQuality
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionItem
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord

class ChordData(TypedDict):
    root: str
    quality: str

class ProgressionPreset(TypedDict):
    name: str
    chords: List[ChordData]

class ChordProgressionFactory(BaseModel):
    """Factory for creating chord progressions with different strategies."""
    
    scale_info: ScaleInfo
    validation_level: ValidationLevel = Field(default=ValidationLevel.NORMAL)

    # Class variables with type annotations
    COMMON_PROGRESSIONS: ClassVar[Dict[str, ProgressionPreset]] = {
        "basic_major": {
            "name": "Basic Major Progression",
            "chords": [
                {"root": "C", "quality": "MAJOR"},
                {"root": "F", "quality": "MAJOR"},
                {"root": "G", "quality": "MAJOR"},
                {"root": "C", "quality": "MAJOR"}
            ]
        }
    }

    GENRE_PATTERNS: ClassVar[Dict[str, List[Tuple[int, ChordQuality]]]] = {
        "pop": [(1, ChordQuality.MAJOR), (6, ChordQuality.MINOR), 
               (4, ChordQuality.MAJOR), (5, ChordQuality.MAJOR)],
        "jazz": [(2, ChordQuality.MINOR), (5, ChordQuality.DOMINANT_SEVENTH), 
                (1, ChordQuality.MAJOR_SEVENTH)],
        "blues": [(1, ChordQuality.DOMINANT_SEVENTH), (4, ChordQuality.DOMINANT_SEVENTH), 
                 (5, ChordQuality.DOMINANT_SEVENTH)]
    }

    @classmethod
    async def from_preset(
        cls,
        preset_name: str,
        key: str,
        scale_type: ScaleType,
        time_signature: tuple[int, int] = (4, 4)
    ) -> ChordProgression:
        """Create a progression from a preset pattern."""
        if preset_name not in cls.COMMON_PROGRESSIONS:
            raise ValueError(f"Unknown preset: {preset_name}")
            
        preset = cls.COMMON_PROGRESSIONS[preset_name]
        items = [
            ChordProgressionItem(
                chord=Chord(**chord_data),
                chord_symbol=f"{chord_data['root']}{chord_data.get('quality', '')}",
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
            total_duration=float(len(items)),
            chords=[Chord(**chord_data) for chord_data in preset["chords"]]
        )

    @classmethod
    async def from_pattern(
        cls,
        pattern: List[Tuple[int, str]],
        key: str,
        scale_type: ScaleType
    ) -> ChordProgression:
        """Create a progression from a pattern of scale degrees and qualities."""
        scale_info = ScaleInfo(key=key, scale_type=scale_type)
        scale_notes = scale_info.get_scale_notes()
        chords = []
        position = 0.0
        
        for degree, quality in pattern:
            # Convert scale degree to root note (degrees are 1-based, list is 0-based)
            root = scale_notes[degree - 1].pitch
            chords.append({
                "root": root,
                "quality": quality
            })
        
        return ChordProgression(
            name="Pattern-Based Progression",
            key=key,
            scale_type=scale_type,
            scale_info=scale_info,
            chords=chords,
            items=[
                ChordProgressionItem(
                    chord=Chord(**chord),
                    chord_symbol=f"{chord['root']}{chord['quality']}",
                    duration=1.0,
                    position=float(i)
                )
                for i, chord in enumerate(chords)
            ]
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
        if genre not in cls.GENRE_PATTERNS:
            raise ValueError(f"Unsupported genre: {genre}")
            
        pattern = cls.GENRE_PATTERNS[genre][:length]
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
