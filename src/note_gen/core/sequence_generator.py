"""Generator classes for creating musical sequences."""
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4
import logging
from pydantic import ConfigDict, BaseModel, Field, field_validator

# Import models
from src.note_gen.models.patterns import Pattern, NotePattern
from src.note_gen.models.rhythm import RhythmPattern, RhythmNote
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.sequence import NoteSequence

# Import enums and other utilities
from src.note_gen.core.enums import PatternDirection, ValidationLevel, ScaleType
from src.note_gen.validation.pattern_pipeline import PatternValidationPipeline
from src.note_gen.validation.validation_manager import ValidationManager

logger = logging.getLogger(__name__)

class Generator:
    """Base generator class with common functionality."""
    
    def __init__(self):
        self.validator = PatternValidationPipeline()
        
    def _generate_id(self) -> str:
        """Generate a unique pattern ID."""
        return str(uuid4())[:8]
        
    def validate_pattern(self, pattern: Pattern, level: ValidationLevel) -> bool:
        """Validate a generated pattern."""
        return ValidationManager.validate_model(
            model_class=pattern.__class__,
            data=pattern.model_dump(),
            level=level
        ).is_valid

class NoteGenerator(Generator):
    """Generator for note patterns."""

    def generate_pattern(
        self,
        root_note: str,
        scale_type: ScaleType,
        pattern_config: Dict[str, Any],
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> Optional[NotePattern]:
        """Generate a validated note pattern."""
        try:
            pattern = NotePattern(
                id=self._generate_id(),
                name=f"Generated Note Pattern {self._generate_id()}",
                pattern=[],  # Will be populated based on config
                data={
                    "root_note": root_note,
                    "scale_type": scale_type,
                    "intervals": pattern_config.get('intervals', [0, 2, 4]),
                    "direction": pattern_config.get('direction', PatternDirection.UP),
                    "octave_range": pattern_config.get('octave_range', (4, 5))
                }
            )
            
            if self.validate_pattern(pattern, validation_level):
                return pattern
            return None
            
        except Exception as e:
            logger.error(f"Note pattern generation failed: {e}")
            return None

class RhythmGenerator(Generator):
    """Generator for rhythm patterns."""

    def generate_pattern(
        self,
        durations: List[float],
        time_signature: Tuple[int, int] = (4, 4),
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> Optional[RhythmPattern]:
        """Generate a validated rhythm pattern."""
        try:
            pattern = RhythmPattern(
                id=self._generate_id(),
                name=f"Generated Rhythm Pattern {self._generate_id()}",
                durations=durations,
                time_signature=time_signature
            )
            
            if self.validate_pattern(pattern, validation_level):
                return pattern
            return None
            
        except Exception as e:
            logger.error(f"Rhythm pattern generation failed: {e}")
            return None

class PatternGenerator(Generator):
    """Base pattern generator class."""
    
    def __init__(self):
        super().__init__()
        self.note_generator = NoteGenerator()
        self.rhythm_generator = RhythmGenerator()

    async def generate_pattern(
        self,
        pattern_type: str,
        config: Dict[str, Any],
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> Optional[Pattern]:
        """Generate a pattern based on type and config."""
        if pattern_type == "note":
            return self.note_generator.generate_pattern(**config, validation_level=validation_level)
        elif pattern_type == "rhythm":
            return self.rhythm_generator.generate_pattern(**config, validation_level=validation_level)
        return None

class NoteSequenceGenerator(BaseModel):
    """Generator for creating note sequences."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
        validate_assignment=True
    )
    
    chord_progression: ChordProgression
    note_pattern: NotePattern
    rhythm_pattern: RhythmPattern
    durations: List[float] = Field(default_factory=list)

    @field_validator('rhythm_pattern')
    @classmethod
    def validate_rhythm_pattern(cls, v):
        if isinstance(v, RhythmPattern):
            return v
        elif isinstance(v, dict):
            return RhythmPattern(**v)
        raise ValueError("Invalid rhythm pattern")

    def generate_sequence(self) -> NoteSequence:
        """Generate a note sequence from the patterns."""
        sequence = NoteSequence(
            id=str(uuid4())[:8],
            name=f"Generated Sequence {self.note_pattern.name}",
            notes=[],
            duration=self.rhythm_pattern.total_duration,
            tempo=120,
            time_signature=self.rhythm_pattern.time_signature
        )
        
        return sequence

async def generate_sequence_from_presets(
    progression_name: str,
    scale_info: ScaleInfo,
    time_signature: Tuple[int, int],
    tempo: int,
    key: str
) -> Pattern:
    """Generate a sequence from preset parameters."""
    note_gen = NoteGenerator()
    rhythm_gen = RhythmGenerator()
    
    # Generate both patterns
    note_pattern = note_gen.generate_pattern(
        root_note=key,
        scale_type=scale_info.scale_type,
        pattern_config={"intervals": [0, 2, 4]}  # Basic triad pattern
    )
    
    rhythm_pattern = rhythm_gen.generate_pattern(
        durations=[1.0, 1.0, 1.0, 1.0],  # Basic quarter note pattern
        time_signature=time_signature
    )
    
    if not note_pattern or not rhythm_pattern:
        raise ValueError("Failed to generate valid patterns")
        
    # Combine patterns into final sequence
    return Pattern(
        id=note_gen._generate_id(),
        name=f"Generated Sequence {note_gen._generate_id()}",
        duration=4.0,  # Default to one bar
        time_signature=time_signature,
        note_pattern=note_pattern,
        rhythm_pattern=rhythm_pattern
    )
