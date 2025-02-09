from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, validator
import logging

from src.note_gen.models.note import Note
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ScaleType

logger = logging.getLogger(__name__)

async def generate_sequence_from_presets(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
    chord_progression: Dict[str, Any],
    note_pattern: Dict[str, Any],
    rhythm_pattern: Dict[str, Any]
) -> NoteSequence:
    """
    Generate a note sequence from presets.
    """
    try:
        logger.info(f"Generating sequence with scale_info: {scale_info.model_dump_json()}")
        # For Simple Triad pattern, generate notes based on the scale root
        root_note = scale_info.root
        
        # Calculate notes for the Simple Triad pattern (root, second, third)
        second_semitones = 2  # Whole step
        third_semitones = 4 if scale_info.scale_type == ScaleType.MAJOR else 3  # Major third (4) or minor third (3)
        
        root_midi = root_note.midi_number
        second_midi = root_midi + second_semitones
        third_midi = root_midi + third_semitones
        
        root = Note.from_midi(root_midi, velocity=64, duration=1)
        second = Note.from_midi(second_midi, velocity=64, duration=1)
        third = Note.from_midi(third_midi, velocity=64, duration=1)
        
        # Create a sequence with these notes
        sequence = NoteSequence(notes=[root, second, third])
        logger.info(f"Generated sequence: {sequence.model_dump_json()}")
        
        return sequence
    except Exception as e:
        logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
        raise

class NoteSequenceGenerator(BaseModel):
    """Generator for creating note sequences from chord progressions and rhythm patterns."""
    
    chord_progression: ChordProgression
    rhythm_pattern: Optional[RhythmPattern] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Initialized NoteSequenceGenerator with chord_progression: {self.chord_progression.model_dump_json()} and rhythm_pattern: {self.rhythm_pattern.model_dump_json() if self.rhythm_pattern else None}")
    
    def generate(self) -> NoteSequence:
        """Generate a sequence of notes based on the chord progression and rhythm pattern."""
        try:
            logger.info("Generating sequence")
            sequence = []
            for chord in self.chord_progression.chords:
                # Use chord.notes instead of chord.generate_notes()
                sequence.extend(chord.notes)
            logger.info(f"Generated sequence: {NoteSequence(notes=sequence).model_dump_json()}")
            return NoteSequence(notes=sequence)
        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
            raise
    
    def _generate_basic_sequence(self) -> List[Note]:
        """Generate a basic sequence without rhythm pattern."""
        try:
            logger.info("Generating basic sequence")
            sequence = []
            for chord in self.chord_progression.chords:
                # Generate all notes in the chord (not just the root)
                chord_notes = chord.generate_notes()
                sequence.extend(chord_notes)
            logger.info(f"Generated basic sequence: {sequence}")
            return sequence
        except Exception as e:
            logger.error(f"Error generating basic sequence: {str(e)}", exc_info=True)
            raise
    
    def _generate_rhythmic_sequence(self) -> List[Note]:
        """Generate a sequence using the rhythm pattern."""
        try:
            logger.info("Generating rhythmic sequence")
            if not self.rhythm_pattern:
                raise ValueError("Rhythm pattern is required for rhythmic sequence generation")
            
            sequence = []
            durations = self.rhythm_pattern.get_durations()
            chord_idx = 0
            
            for duration in durations:
                if chord_idx >= len(self.chord_progression.chords):
                    chord_idx = 0  # Loop back to start of progression
                    
                chord = self.chord_progression.chords[chord_idx]
                note = Note(
                    note_name=chord.root.note_name,
                    octave=chord.root.octave,
                    duration=duration,
                    velocity=chord.root.velocity
                )
                sequence.append(note)
                chord_idx += 1
                
            logger.info(f"Generated rhythmic sequence: {sequence}")
            return sequence
        except Exception as e:
            logger.error(f"Error generating rhythmic sequence: {str(e)}", exc_info=True)
            raise
    
    def generate_sequence(self) -> NoteSequence:
        """Generate a note sequence from the chord progression and rhythm pattern."""
        try:
            logger.info("Generating sequence")
            if not self.rhythm_pattern:
                raise ValueError("Rhythm pattern is required for sequence generation")
            
            sequence = NoteSequence(notes=[], events=[])
            for chord in self.chord_progression.chords:
                root_note = self.get_root_note_from_chord(chord)
                if not root_note:
                    continue
                
                # Create note events based on the rhythm pattern
                for rhythm_note in self.rhythm_pattern.data.notes:
                    note_event = NoteEvent(
                        note=root_note,
                        position=rhythm_note.position,
                        duration=rhythm_note.duration,
                        velocity=rhythm_note.velocity,
                        is_rest=rhythm_note.is_rest
                    )
                    sequence.events.append(note_event)
                    sequence.notes.append(root_note)
            
            # Update sequence duration
            if sequence.events:
                sequence.duration = max(event.end_position for event in sequence.events)
            
            logger.info(f"Generated sequence: {sequence.model_dump_json()}")
            return sequence
        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
            raise
    
    def get_root_note_from_chord(self, chord: Chord) -> Optional[Note]:
        """Get the root note from a chord."""
        try:
            logger.info(f"Getting root note from chord: {chord.model_dump_json()}")
            if hasattr(chord, 'root') and isinstance(chord.root, Note):
                return chord.root
            logger.info("No root note found")
            return None
        except Exception as e:
            logger.error(f"Error getting root note from chord: {str(e)}", exc_info=True)
            raise
    
    def set_rhythm_pattern(self, pattern: RhythmPattern) -> None:
        """Set a new rhythm pattern."""
        try:
            logger.info(f"Setting rhythm pattern: {pattern.model_dump_json()}")
            self.rhythm_pattern = pattern
        except Exception as e:
            logger.error(f"Error setting rhythm pattern: {str(e)}", exc_info=True)
            raise
    
    def set_chord_progression(self, progression: ChordProgression) -> None:
        """Set a new chord progression."""
        try:
            logger.info(f"Setting chord progression: {progression.model_dump_json()}")
            self.chord_progression = progression
        except Exception as e:
            logger.error(f"Error setting chord progression: {str(e)}", exc_info=True)
            raise

    async def generate_sequence_from_presets(
        self,
        progression_name: str,
        note_pattern_name: str,
        rhythm_pattern_name: str,
        scale_info: ScaleInfo,
        chord_progression: ChordProgression,
        note_pattern: dict,
        rhythm_pattern: dict,
    ) -> NoteSequence:
        """
        Generate a note sequence from presets.
        """
        try:
            logger.info(f"Generating sequence with scale_info: {scale_info.model_dump_json()}")
            # For now, generate a simple sequence using the chord progression's first chord
            if not chord_progression.chords:
                raise ValueError("Chord progression has no chords")
            
            first_chord = chord_progression.chords[0]
            sequence = NoteSequence(notes=first_chord.notes)
            logger.info(f"Generated sequence: {sequence.model_dump_json()}")
            
            return sequence
        except Exception as e:
            logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
            raise