"""Pattern generator module."""
from typing import Dict, Any, List
from note_gen.core.enums import PatternType, PatternDirection, ValidationLevel
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.note_sequence import NoteSequence
from note_gen.validation.pattern_validation import PatternValidator
from note_gen.core.constants import PATTERN_PRESETS, PROGRESSION_PRESETS

async def generate_sequence_from_presets(
    note_pattern_name: str,
    rhythm_pattern_name: str,
    progression_name: str,
    scale_info: Dict[str, Any]
) -> NoteSequence:
    """
    Generate a note sequence from preset patterns.

    Args:
        note_pattern_name: Name of the note pattern preset
        rhythm_pattern_name: Name of the rhythm pattern preset
        progression_name: Name of the chord progression preset
        scale_info: Dictionary containing scale information

    Returns:
        Generated note sequence

    Raises:
        ValueError: If any preset names are invalid or if generation fails
    """
    # Validate preset names
    if note_pattern_name not in PATTERN_PRESETS.get("note_patterns", {}):
        raise ValueError(f"Invalid note pattern name: {note_pattern_name}")
    if rhythm_pattern_name not in PATTERN_PRESETS.get("rhythm_patterns", {}):
        raise ValueError(f"Invalid rhythm pattern name: {rhythm_pattern_name}")
    if progression_name not in PROGRESSION_PRESETS:
        raise ValueError(f"Invalid progression name: {progression_name}")

    # Create scale info object
    scale = ScaleInfo(**scale_info)

    # Get preset configurations
    note_pattern_config = PATTERN_PRESETS["note_patterns"][note_pattern_name]
    rhythm_pattern_config = PATTERN_PRESETS["rhythm_patterns"][rhythm_pattern_name]
    progression = PROGRESSION_PRESETS[progression_name]

    # Initialize pattern generator
    generator = PatternGenerator()

    # Generate patterns
    # We don't use the note_pattern directly, but it's generated for consistency
    _ = generator.generate_pattern(
        pattern_type=PatternType.MELODIC,
        config={
            "root_note": scale.key,
            "scale_type": scale.scale_type,
            **(note_pattern_config if isinstance(note_pattern_config, dict) else {})
        }
    )

    rhythm_pattern = generator.generate_pattern(
        pattern_type=PatternType.RHYTHMIC,
        config=rhythm_pattern_config if isinstance(rhythm_pattern_config, dict) else {}
    )

    # Combine patterns into a sequence
    notes = []
    current_position = 0.0

    # We don't use the chord directly, but iterate through the progression
    for _ in progression:
        for rhythm_note in rhythm_pattern.pattern:
            if rhythm_note.note:
                note = rhythm_note.note.clone()
                note.position = current_position + rhythm_note.position
                note.duration = rhythm_note.duration
                notes.append(note)

        current_position += rhythm_pattern.total_duration

    # Create and return the sequence
    return NoteSequence(
        notes=notes,
        duration=current_position,
        scale_info=scale,
        progression_name=progression_name,
        note_pattern_name=note_pattern_name,
        rhythm_pattern_name=rhythm_pattern_name
    )

class PatternGenerator:
    """Generator for musical patterns."""

    def generate_pattern(
        self,
        pattern_type: PatternType,
        config: Dict[str, Any],
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> RhythmPattern:
        """
        Generate a musical pattern based on the provided configuration.

        Args:
            pattern_type: Type of pattern to generate (MELODIC or RHYTHMIC)
            config: Configuration dictionary containing pattern parameters
            validation_level: Level of validation to apply

        Returns:
            Generated pattern

        Raises:
            ValueError: If the configuration is invalid
        """
        if pattern_type == PatternType.MELODIC:
            return self._generate_melodic_pattern(config, validation_level)
        elif pattern_type == PatternType.RHYTHMIC:
            return self._generate_rhythm_pattern(config, validation_level)
        else:
            raise ValueError(f"Unsupported pattern type: {pattern_type}")

    def _generate_melodic_pattern(
        self,
        config: Dict[str, Any],
        validation_level: ValidationLevel
    ) -> RhythmPattern:
        """Generate a melodic pattern."""
        # Extract configuration
        root_note = config.get('root_note')
        scale_type = config.get('scale_type')
        intervals = config.get('intervals', [])
        direction = config.get('direction', PatternDirection.UP)
        octave_range = config.get('octave_range', (4, 4))

        if not root_note or not scale_type:
            raise ValueError("Root note and scale type are required for melodic patterns")

        # Create scale info
        scale_info = ScaleInfo(key=root_note, scale_type=scale_type)
        scale_notes = scale_info.get_scale_notes(octave_range[0])

        # Generate notes based on intervals
        pattern_notes: List[RhythmNote] = []
        current_position = 0.0

        for interval in intervals:
            if not (0 <= interval < len(scale_notes)):
                raise ValueError(f"Invalid interval: {interval}")

            note_idx = interval if direction == PatternDirection.UP else (len(scale_notes) - 1 - interval)
            scale_note = scale_notes[note_idx]

            rhythm_note = RhythmNote(
                note=scale_note,
                position=current_position,
                duration=1.0  # Default duration
            )
            pattern_notes.append(rhythm_note)
            current_position += 1.0

        # Create and validate the pattern
        pattern = RhythmPattern(
            pattern=pattern_notes,
            total_duration=float(len(pattern_notes))
        )

        validation_result = PatternValidator.validate(pattern, validation_level)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid pattern: {validation_result.violations}")

        return pattern

    def _generate_rhythm_pattern(
        self,
        config: Dict[str, Any],
        validation_level: ValidationLevel
    ) -> RhythmPattern:
        """Generate a rhythm pattern."""
        # Extract configuration
        durations = config.get('durations', [])
        time_signature = config.get('time_signature', (4, 4))

        if not durations:
            raise ValueError("Durations are required for rhythm patterns")

        # Generate rhythm notes
        pattern_notes: List[RhythmNote] = []
        current_position = 0.0

        for duration in durations:
            if duration <= 0:
                raise ValueError(f"Invalid duration: {duration}")

            rhythm_note = RhythmNote(
                position=current_position,
                duration=duration
            )
            pattern_notes.append(rhythm_note)
            current_position += duration

        # Validate total duration against time signature
        total_duration = sum(note.duration for note in pattern_notes)
        expected_duration = time_signature[0] * (4.0 / time_signature[1])
        if total_duration > expected_duration:
            raise ValueError(
                f"Total duration ({total_duration}) exceeds time signature duration ({expected_duration})"
            )

        # Create and validate the pattern
        pattern = RhythmPattern(
            pattern=pattern_notes,
            time_signature=time_signature,
            total_duration=total_duration
        )

        validation_result = PatternValidator.validate(pattern, validation_level)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid pattern: {validation_result.violations}")

        return pattern
