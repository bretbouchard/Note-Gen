"""Service for pattern-related operations."""
import re
from typing import Dict, Any, Union, List
from src.note_gen.core.enums import ScaleType, ValidationLevel, PatternDirection
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.scale import Scale
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.validation.base_validation import ValidationResult

# Define a Pattern type that can be either NotePattern or RhythmPattern
PatternType = Union[NotePattern, RhythmPattern]

class PatternService:
    """Service for handling pattern operations."""
    
    async def generate_musical_pattern(
        self,
        root_note: str,
        scale_type: ScaleType,
        pattern_config: Dict[str, Any]
    ) -> NotePattern:
        """Generate a musical pattern based on given parameters."""
        if not re.match(r'^[A-G][#b]?$', root_note):
            raise ValueError(f"Invalid root note format: {root_note}")

        # Extract configuration
        intervals = pattern_config.get("intervals", [0, 2, 4])
        direction = PatternDirection(pattern_config.get("direction", "up"))
        octave_range = pattern_config.get("octave_range", (4, 5))
        
        # Create scale with root note and octave
        scale = Scale(
            root=f"{root_note}{octave_range[0]}",  # Add octave to root note
            scale_type=scale_type,
            octave_range=octave_range
        ).generate_notes()
        
        # Generate notes based on intervals
        pattern_notes: List[Note] = []
        scale_notes = scale.notes
        
        for interval in intervals:
            if direction == PatternDirection.UP:
                note_idx = interval % len(scale_notes)
            else:
                note_idx = (len(scale_notes) - 1 - interval) % len(scale_notes)
                
            note = scale_notes[note_idx].model_copy()  # Using model_copy instead of copy
            note.duration = 1.0  # Set default duration
            pattern_notes.append(note)

        # Create pattern data - remove duplicated fields from pattern_config
        pattern_config_clean = {
            k: v for k, v in pattern_config.items() 
            if k not in ['intervals', 'direction', 'octave_range']
        }
        
        pattern_data = NotePatternData(
            key=root_note,
            root_note=root_note,
            scale_type=scale_type,
            direction=direction,
            octave_range=octave_range,
            intervals=intervals,
            **pattern_config_clean
        )

        # Create scale info for the pattern
        scale_info = ScaleInfo(
            key=root_note,
            scale_type=scale_type
        )

        # Create and return the pattern
        pattern = NotePattern(
            name=f"{root_note} {scale_type.value} Pattern",
            pattern=pattern_notes,
            data=pattern_data,
            scale_info=scale_info
        )

        return pattern

    async def validate_pattern(self, pattern: PatternType) -> ValidationResult:
        """Validate a pattern."""
        return ValidationResult(
            is_valid=True,
            violations=[]
        )
