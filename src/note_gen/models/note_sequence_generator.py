from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, validator

from src.note_gen.models.note import Note
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.scale_info import ScaleInfo  # Import ScaleInfo

def generate_sequence_from_presets(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
) -> NoteSequence:
    """
    Top-level function to generate a note sequence from presets.
    Replace this stub with your real logic as needed.
    """
    # For example, you might look up the chord progression, note pattern,
    # and rhythm pattern from a database or in-memory dictionaries,
    # then build a NoteSequence. Currently just returns an empty sequence.
    return NoteSequence(notes=[])

class NoteSequenceGenerator(BaseModel):
    """Generator for creating note sequences from chord progressions and rhythm patterns."""
    
    chord_progression: ChordProgression
    rhythm_pattern: Optional[RhythmPattern] = None
    
    def generate(self) -> List[Note]:
        """Generate a sequence of notes based on the chord progression and rhythm pattern."""
        if not self.rhythm_pattern:
            return self._generate_basic_sequence()
        return self._generate_rhythmic_sequence()
    
    def _generate_basic_sequence(self) -> List[Note]:
        """Generate a basic sequence without rhythm pattern."""
        sequence = []
        for chord in self.chord_progression.chords:
            # Generate all notes in the chord (not just the root)
            chord_notes = chord.generate_chord_notes()
            sequence.extend(chord_notes)
        return sequence
    
    def _generate_rhythmic_sequence(self) -> List[Note]:
        """Generate a sequence using the rhythm pattern."""
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
            
        return sequence
    
    def generate_sequence(self) -> NoteSequence:
        """Generate a note sequence from the chord progression and rhythm pattern."""
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
        
        return sequence
    
    def get_root_note_from_chord(self, chord: Chord) -> Optional[Note]:
        """Get the root note from a chord."""
        if hasattr(chord, 'root') and isinstance(chord.root, Note):
            return chord.root
        return None
    
    def set_rhythm_pattern(self, pattern: RhythmPattern) -> None:
        """Set a new rhythm pattern."""
        self.rhythm_pattern = pattern
    
    def set_chord_progression(self, progression: ChordProgression) -> None:
        """Set a new chord progression."""
        self.chord_progression = progression

    def generate_sequence_from_presets(
        self,
        progression_name: str,
        note_pattern_name: str,
        rhythm_pattern_name: str,
        scale_info: ScaleInfo,
    ) -> NoteSequence:
        """
        Class method version for generating sequences from presets.
        Typically, you might do lookups for each preset, build chord progression,
        note pattern, and rhythm pattern objects, then create a NoteSequence.

        For now, this just returns an empty sequence as a stub.
        """
        return NoteSequence(notes=[])