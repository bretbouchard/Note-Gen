from typing import List, Tuple, Dict, Any
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionItem
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.core.enums import ScaleType, ChordQuality

class ChordProgressionFactory:
    """Factory for creating chord progressions."""
    
    COMMON_PROGRESSIONS = {
        "pop": {
            "pattern": [
                (1, "MAJOR"),    # C
                (5, "MAJOR"),    # G
                (6, "MINOR"),    # Am
                (4, "MAJOR")     # F
            ],
            "duration": 1.0,     # duration per chord
            "description": "Common I-V-vi-IV pop progression"
        },
        "basic_major": {
            "pattern": [
                (1, "MAJOR"),    # I
                (4, "MAJOR"),    # IV
                (5, "MAJOR"),    # V
                (1, "MAJOR")     # I
            ],
            "duration": 1.0,
            "description": "Basic I-IV-V-I progression"
        }
    }

    GENRE_PATTERNS = {
        "rock": {
            "patterns": [
                [(1, "MAJOR"), (4, "MAJOR"), (5, "MAJOR"), (5, "MAJOR")],  # I-IV-V-V
                [(1, "MAJOR"), (6, "MINOR"), (4, "MAJOR"), (5, "MAJOR")],  # I-vi-IV-V
                [(1, "MAJOR"), (5, "MAJOR"), (6, "MINOR"), (4, "MAJOR")]   # I-V-vi-IV
            ],
            "description": "Common rock progressions"
        }
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
        pattern = preset["pattern"]
        
        return await cls.from_pattern(
            pattern=pattern,
            key=key,
            scale_type=scale_type,
            time_signature=time_signature
        )

    @classmethod
    async def from_pattern(
        cls,
        pattern: List[Tuple[int, str]],
        key: str,
        scale_type: ScaleType,
        time_signature: tuple[int, int] = (4, 4)  # Add time_signature parameter with default value
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
            time_signature=time_signature,
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
        length: int = 4,
        time_signature: tuple[int, int] = (4, 4)
    ) -> ChordProgression:
        """Create a progression based on genre patterns."""
        if genre not in cls.GENRE_PATTERNS:
            raise ValueError(f"Unsupported genre: {genre}")

        pattern = cls.GENRE_PATTERNS[genre]["patterns"][0]
        
        return await cls.from_pattern(
            pattern=pattern,
            key=key,
            scale_type=scale_type,
            time_signature=time_signature
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
