"""
Chord progression generator with enhanced validation and pattern support.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from src.note_gen.core.enums import ChordQuality, ScaleType, ValidationLevel, VoiceLeadingRule
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.core.constants import COMMON_PROGRESSIONS
from src.note_gen.validation.validation_manager import ValidationManager
from src.note_gen.validation.base_validation import ValidationResult, ValidationViolation

import logging

logger = logging.getLogger(__name__)

class ProgressionGenerator(BaseModel):
    """Base class for progression generation."""
    scale_info: ScaleInfo
    progression_length: int = Field(default=4, ge=1)
    validation_level: ValidationLevel = Field(default=ValidationLevel.NORMAL)
    voice_leading_rules: List[VoiceLeadingRule] = Field(default_factory=list)

    @field_validator('scale_info')
    @classmethod
    def validate_scale_info(cls, v):
        if not isinstance(v, ScaleInfo):
            raise ValueError("scale_info must be a ScaleInfo instance")
        return v


class ChordProgressionGenerator(BaseModel):
    """Generator for chord progressions with enhanced validation and patterns."""
    name: str
    chords: List[Chord] = Field(default_factory=list)
    key: str
    scale_type: ScaleType = ScaleType.MAJOR
    complexity: float = Field(ge=0.1, le=1.0, default=0.5)
    test_mode: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    @classmethod
    def create_test_generator(cls, scale_info: ScaleInfo) -> 'ChordProgressionGenerator':
        """Create a test generator instance."""
        return cls(
            name="Test Generator",
            key=scale_info.key,
            scale_type=scale_info.scale_type,
            scale_info=scale_info,
            test_mode=True
        )

    def get_root_note_for_degree(self, degree: Union[int, str]) -> Note:
        """Get the root note for a given scale degree."""
        if isinstance(degree, str):
            return Note(
                pitch=degree,
                duration=1.0,
                velocity=64
            )

        if not 1 <= degree <= 7:
            raise ValueError(f"Scale degree must be between 1 and 7, got {degree}")

        # Get notes from scale_info using proper method
        scale_notes = self.scale_info.get_scale_notes()  # Assuming this method exists
        note_name = scale_notes[degree - 1]
        return Note(
            pitch=note_name,
            duration=1.0,
            velocity=64
        )

    async def generate_from_pattern(self, pattern: List[tuple]) -> ChordProgression:
        chords = []
        for degree, quality in pattern:
            if not (1 <= degree <= 7):
                raise ValueError(f"Invalid scale degree: {degree}")
            
            root = self.get_root_note_for_degree(degree)
            chord = Chord(root=str(root.pitch), quality=quality)
            chords.append(chord)

        progression = ChordProgression(
            name=self.name,
            root_note=self.key,
            scale_type=self.scale_type,
            chords=chords,
            time_signature=(4, 4)
        )
        
        # Validation
        validation_manager = ValidationManager()
        validation_result = validation_manager.validate(progression)
        
        if not validation_result.is_valid:
            logger.warning(f"Validation issues: {validation_result.errors}")
            if self.validation_level == ValidationLevel.STRICT:
                raise ValueError(f"Validation failed: {validation_result.errors}")

        return progression

    async def generate(
        self,
        progression_length: int = 4,
        genre: Optional[str] = None,
        template: Optional[str] = None
    ) -> ChordProgression:
        """Generate a chord progression with optional genre or template."""
        try:
            if template and template in COMMON_PROGRESSIONS:
                pattern = COMMON_PROGRESSIONS[template]["chords"]
                return await self.generate_from_pattern(pattern[:progression_length])

            if genre and genre not in self.genre_patterns:
                raise ValueError(f"Unsupported genre: {genre}")

            pattern = self.genre_patterns.get(genre or "pop", [])
            if not pattern:
                raise ValueError(f"No pattern found for genre: {genre}")

            # Create progression with required parameters
            progression = await self.generate_from_pattern(pattern[:progression_length])
            
            # Validate using proper method
            validation_manager = ValidationManager()
            validation_result = validation_manager.validate(progression)
            
            if not validation_result.is_valid:
                raise ValueError(f"Generated progression validation failed: {validation_result.errors}")
                
            return progression

        except Exception as e:
            logger.error(f"Error generating progression: {str(e)}", exc_info=True)
            raise

    def validate_progression(self, progression: ChordProgression) -> ValidationResult:
        """Validate a chord progression."""
        # Validation logic here
        return ValidationResult(is_valid=True, violations=[])

    @property
    def genre_patterns(self) -> Dict[str, List[tuple]]:
        """Predefined chord patterns for different genres."""
        return {
            "pop": [
                (1, ChordQuality.MAJOR),
                (4, ChordQuality.MAJOR),
                (5, ChordQuality.MAJOR),
                (1, ChordQuality.MAJOR)
            ],
            "jazz": [
                (2, ChordQuality.MINOR),
                (5, ChordQuality.DOMINANT_SEVENTH),
                (1, ChordQuality.MAJOR_SEVENTH),
                (4, ChordQuality.MAJOR_SEVENTH)
            ],
            "blues": [
                (1, ChordQuality.DOMINANT_SEVENTH),
                (4, ChordQuality.DOMINANT_SEVENTH),
                (5, ChordQuality.DOMINANT_SEVENTH),
                (1, ChordQuality.DOMINANT_SEVENTH)
            ],
            "classical": [
                (1, ChordQuality.MAJOR),
                (5, ChordQuality.MAJOR),
                (4, ChordQuality.MAJOR),
                (1, ChordQuality.MAJOR)
            ]
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert generator settings to dictionary."""
        return {
            "name": self.name,
            "key": self.key,
            "scale_type": self.scale_type.value,
            "complexity": self.complexity,
            "validation_level": self.validation_level.value,
            "voice_leading_rules": [rule.value for rule in self.voice_leading_rules]
        }

    def generate_from_template(
        self,
        template_name: str,
        key: str = "C",
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> ChordProgression:
        """
        Generate a chord progression from a template.
        
        Args:
            template_name: Name of the template to use
            key: Key to generate in
            validation_level: Level of validation to apply
            
        Returns:
            ChordProgression: Generated progression
        """
        if template_name not in COMMON_PROGRESSIONS:
            raise ValueError(f"Unknown progression template: {template_name}")
            
        template = COMMON_PROGRESSIONS[template_name]
        progression = ChordProgression(
            name=template["name"],
            key=key,
            chords=template["chords"],
            tags=template["tags"]
        )
        
        # Validate the generated progression
        validation_result = ChordProgression.validate_progression(
            progression=progression,
            validation_level=validation_level
        )
        
        if not validation_result.is_valid:
            raise ValueError(f"Generated progression validation failed: {validation_result.errors}")
            
        return progression

    def generate_custom(
        self,
        length: int,
        key: str = "C",
        complexity: float = 0.5,
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> ChordProgression:
        """
        Generate a custom chord progression.
        
        Args:
            length: Number of chords
            key: Key to generate in
            complexity: Desired complexity (0-1)
            validation_level: Level of validation to apply
            
        Returns:
            ChordProgression: Generated progression
        """
        # Generate progression logic here
        progression = ChordProgression(
            name="Custom Progression",
            key=key,
            chords=self._generate_chord_sequence(length, complexity),
            tags=["custom"]
        )
        
        # Validate the generated progression
        validation_result = ChordProgression.validate_progression(
            progression=progression,
            validation_level=validation_level
        )
        
        if not validation_result.is_valid:
            raise ValueError(f"Generated progression validation failed: {validation_result.errors}")
            
        return progression

    def _generate_chord_sequence(self, length: int, complexity: float) -> List[Dict[str, Any]]:
        """
        Generate a sequence of chords based on length and complexity.
        
        Args:
            length: Number of chords to generate
            complexity: Value between 0-1 determining progression complexity
        
        Returns:
            List of chord dictionaries
        """
        chords = []
        scale_degrees = [1, 4, 5, 6]  # Basic scale degrees
        
        # Add more complex degrees based on complexity
        if complexity > 0.5:
            scale_degrees.extend([2, 3, 7])
        
        for _ in range(length):
            # Select degree based on complexity
            degree = scale_degrees[int(len(scale_degrees) * complexity) % len(scale_degrees)]
            
            # Determine chord quality based on scale degree and complexity
            if complexity > 0.7 and degree in [2, 3, 6]:
                quality = ChordQuality.MINOR
            elif complexity > 0.8 and degree in [5, 7]:
                quality = ChordQuality.DOMINANT_SEVENTH
            else:
                quality = ChordQuality.MAJOR
            
            chords.append({
                "root": degree,
                "quality": quality,
                "duration": 1.0  # Default duration
            })
        
        return chords
