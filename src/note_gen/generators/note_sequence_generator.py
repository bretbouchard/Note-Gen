"""
Note sequence generator with enhanced validation and pattern support.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionItem
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.patterns import NotePattern, RhythmPattern
from src.note_gen.core.enums import ValidationLevel, VoiceLeadingRule, ChordQuality
from src.note_gen.validation.validation_manager import ValidationManager, ValidationResult

import logging

logger = logging.getLogger(__name__)

class NoteSequenceGenerator(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )
    """Generator for creating note sequences from chord progressions and patterns."""
    
    chord_progression: ChordProgression = Field(...)
    note_pattern: NotePattern = Field(...)
    rhythm_pattern: RhythmPattern = Field(...)
    validation_level: ValidationLevel = Field(default=ValidationLevel.NORMAL)
    voice_leading_rules: List[VoiceLeadingRule] = Field(default_factory=list)

    async def generate_sequence_async(
        self,
        scale_info: ScaleInfo,
        transpose: Optional[int] = None
    ) -> List[Note]:
        """Generate note sequence asynchronously with validation."""
        try:
            # Validate inputs
            if not self.chord_progression.chords:
                raise ValueError("Chord progression cannot be empty")

            # Generate basic sequence
            sequence = self._generate_basic_sequence()

            # Apply rhythm pattern
            sequence = self._apply_rhythm_pattern(sequence)

            # Apply note pattern
            sequence = self._apply_note_pattern(sequence, scale_info)

            # Transpose if needed
            if transpose:
                sequence = self._transpose_sequence(sequence, transpose)

            # Validate the generated sequence
            validation_result = self._validate_sequence(sequence)
            if not validation_result.is_valid and self.validation_level == ValidationLevel.STRICT:
                raise ValueError(f"Sequence validation failed: {validation_result.errors}")

            return sequence

        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
            raise

    def _generate_basic_sequence(self) -> List[Note]:
        """Generate basic sequence from chord progression."""
        sequence = []
        for chord_item in self.chord_progression.chords:
            # Create root note
            root_note = Note(
                pitch=chord_item.root,
                octave=4,
                duration=1.0,
                velocity=64
            )
            chord_notes = [root_note]
            
            # Add chord notes based on intervals
            root_midi = root_note.to_midi_number()
            for interval in ChordQuality.get_intervals(chord_item.quality):
                new_midi = root_midi + interval
                new_note = Note.from_midi_number(
                    midi_number=new_midi,
                    duration=1.0,
                    velocity=64
                )
                chord_notes.append(new_note)
            
            sequence.extend(chord_notes)
        return sequence

    def _apply_rhythm_pattern(self, sequence: List[Note]) -> List[Note]:
        """Apply rhythm pattern to the sequence."""
        if not self.rhythm_pattern.pattern:  # Changed from notes to pattern
            return sequence

        rhythmic_sequence = []
        pattern_durations = [note.duration for note in self.rhythm_pattern.pattern]
        pattern_positions = [note.position for note in self.rhythm_pattern.pattern]
        pattern_accents = [note.accent for note in self.rhythm_pattern.pattern]
        pattern_length = len(pattern_durations)
        
        current_position = 0.0
        for i, note in enumerate(sequence):
            pattern_idx = i % pattern_length
            duration = pattern_durations[pattern_idx]
            position = pattern_positions[pattern_idx]
            accent = pattern_accents[pattern_idx]
            
            # Update note properties
            note.duration = duration
            note.position = current_position + position
            if accent:
                note.velocity = min(note.velocity + 16, 127)  # Increase velocity for accented notes
            
            rhythmic_sequence.append(note)
            current_position += duration

        return rhythmic_sequence

    def _apply_note_pattern(self, sequence: List[Note], scale_info: ScaleInfo) -> List[Note]:
        """Apply note pattern to the sequence."""
        if not self.note_pattern.pattern:
            return sequence

        # Create scale notes as Note objects from the scale note strings
        scale_notes = []
        scale_note_strings = scale_info.get_scale_notes()  # Assuming this returns List[Note]
        for scale_note in scale_note_strings:
            scale_notes.append(Note(
                pitch=scale_note.pitch,  # Use the pitch string from the Note object
                octave=4
            ))
        
        pattern_sequence = []
        pattern_length = len(self.note_pattern.pattern)

        for i, note in enumerate(sequence):
            pattern_idx = i % pattern_length
            pattern_note = self.note_pattern.pattern[pattern_idx]
            
            # Find the index of the current note in the scale using the pitch string
            scale_idx = next(i for i, n in enumerate(scale_notes) if n.pitch == note.pitch)
            
            # Calculate interval from pattern note to current note
            interval = pattern_note.to_midi_number() - note.to_midi_number()
            
            new_idx = (scale_idx + interval) % len(scale_notes)
            scale_note = scale_notes[new_idx]
            
            # Use the pitch string from the scale note
            new_note = Note(
                pitch=scale_note.pitch,
                octave=note.octave,
                duration=note.duration,
                velocity=note.velocity
            )
            pattern_sequence.append(new_note)

        return pattern_sequence

    def _transpose_sequence(self, sequence: List[Note], semitones: int) -> List[Note]:
        """Transpose the sequence by given number of semitones."""
        return [note.transpose(semitones) for note in sequence]

    def _validate_sequence(self, sequence: List[Note]) -> ValidationResult:
        """Validate the generated sequence."""
        validation_params = {
            'sequence': sequence,
            'chord_progression': self.chord_progression,
            'voice_leading_rules': self.voice_leading_rules
        }
        
        return ValidationManager.validate_sequence(**validation_params)

    def to_dict(self) -> Dict[str, Any]:
        """Convert generator settings to dictionary."""
        return {
            "chord_progression": self.chord_progression.model_dump(),
            "note_pattern": self.note_pattern.model_dump(),
            "rhythm_pattern": self.rhythm_pattern.model_dump(),
            "validation_level": self.validation_level.value,
            "voice_leading_rules": [rule.value for rule in self.voice_leading_rules]
        }
