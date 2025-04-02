"""Factory for creating note sequences with different strategies."""
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4

from ..models.note_sequence import NoteSequence
from ..models.patterns import NotePattern
from ..models.rhythm import RhythmPattern
from ..models.chord_progression import ChordProgression
from ..models.scale_info import ScaleInfo
from ..core.enums import ScaleType, ValidationLevel
from ..generators.note_sequence_generator import NoteSequenceGenerator
from ..validation.validation_manager import ValidationManager

class NoteSequenceFactory:
    """Factory for creating note sequences using different strategies."""

    @classmethod
    async def create_from_patterns(
        cls,
        chord_progression: ChordProgression,
        note_pattern: NotePattern,
        rhythm_pattern: RhythmPattern,
        scale_info: Optional[ScaleInfo] = None,
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> NoteSequence:
        """Create a note sequence from patterns."""
        generator = NoteSequenceGenerator(
            chord_progression=chord_progression,
            note_pattern=note_pattern,
            rhythm_pattern=rhythm_pattern,
            validation_level=validation_level
        )

        sequence = await generator.generate(scale_info=scale_info)
        # Ensure chord progression is set on the sequence
        sequence.chord_progression = chord_progression.model_dump() if chord_progression else None
        sequence.progression_name = chord_progression.name
        return sequence

    @classmethod
    async def create_from_preset(
        cls,
        preset_name: str,
        key: str,
        scale_type: ScaleType,
        time_signature: Tuple[int, int] = (4, 4),
        tempo: int = 120
    ) -> NoteSequence:
        """Create a note sequence from a preset configuration."""
        from ..factories.pattern_factory import PatternFactory
        from ..factories.chord_progression_factory import ChordProgressionFactory

        # Create components using their respective factories
        pattern_factory = PatternFactory()
        note_pattern = pattern_factory.create_note_pattern(
            root_note=key,
            scale_type=scale_type,
            intervals=[0, 2, 4]  # Basic triad pattern
        )

        rhythm_pattern = pattern_factory.create_rhythm_pattern(
            durations=[1.0, 1.0, 1.0, 1.0],  # Basic quarter note pattern
            time_signature=time_signature
        )

        chord_progression = await ChordProgressionFactory.from_preset(
            preset_name=preset_name,
            key=key,
            scale_type=scale_type,
            time_signature=time_signature
        )

        scale_info = ScaleInfo(key=key, scale_type=scale_type)

        return await cls.create_from_patterns(
            chord_progression=chord_progression,
            note_pattern=note_pattern,
            rhythm_pattern=rhythm_pattern,
            scale_info=scale_info
        )

    @classmethod
    async def create_empty(
        cls,
        time_signature: Tuple[int, int] = (4, 4),
        tempo: int = 120,
        name: str = ""
    ) -> NoteSequence:
        """Create an empty note sequence."""
        return NoteSequence(
            id=str(uuid4())[:8],
            name=name or "Empty Sequence",
            notes=[],
            duration=0.0,
            tempo=tempo,
            time_signature=time_signature
        )

    @classmethod
    async def create_from_config(
        cls,
        config: Dict[str, Any],
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> NoteSequence:
        """Create a note sequence from a configuration dictionary."""
        # Validate config
        if not ValidationManager.validate_config(config, "note_sequence"):
            raise ValueError("Invalid note sequence configuration")

        # Extract components from config
        chord_progression = ChordProgression(**config["chord_progression"])
        note_pattern = NotePattern(**config["note_pattern"])
        rhythm_pattern = RhythmPattern(**config["rhythm_pattern"])

        scale_info = None
        if "scale_info" in config:
            scale_info = ScaleInfo(**config["scale_info"])

        sequence = await cls.create_from_patterns(
            chord_progression=chord_progression,
            note_pattern=note_pattern,
            rhythm_pattern=rhythm_pattern,
            scale_info=scale_info,
            validation_level=validation_level
        )

        # Set additional properties from config
        sequence.name = f"Generated Sequence {note_pattern.name}"
        sequence.note_pattern_name = note_pattern.name
        sequence.rhythm_pattern_name = rhythm_pattern.name

        return sequence
