"""Factory for creating musical patterns."""
from typing import List, Tuple
from ..models.patterns import (
    NotePattern,
    RhythmPattern,
    RhythmNote  # Make sure we're using the correct RhythmNote
)
from ..models.note import Note
from ..core.enums import ScaleType

class PatternFactory:
    """Factory for creating musical patterns."""

    def create_note_pattern(
        self,
        root_note: str,
        scale_type: ScaleType,
        intervals: List[int]
    ) -> NotePattern:
        """
        Create a note pattern from the given parameters.
        
        Args:
            root_note: The root note (e.g. "C4")
            scale_type: The scale type to use
            intervals: List of intervals from the root note
            
        Returns:
            NotePattern: The created note pattern
        """
        return self._create_note_pattern(root_note, scale_type, intervals)

    def create_rhythm_pattern(
        self,
        durations: List[float],
        time_signature: Tuple[int, int] = (4, 4)
    ) -> RhythmPattern:
        """
        Create a rhythm pattern from the given parameters.
        
        Args:
            durations: List of note durations in beats
            time_signature: Time signature as (numerator, denominator)
            
        Returns:
            RhythmPattern: The created rhythm pattern
        """
        return self._create_rhythm_pattern(durations, time_signature)

    def _create_note_pattern(
        self,
        root_note: str,
        scale_type: ScaleType,
        intervals: List[int]
    ) -> NotePattern:
        """Internal method to create a note pattern."""
        # Add octave if not present
        if not any(c.isdigit() for c in root_note):
            root_note = f"{root_note}4"  # Default to octave 4
        
        root = Note.from_name(root_note)
        if root is None:
            raise ValueError(f"Invalid root note: {root_note}")
        
        notes = []
        for interval in intervals:
            midi_num = root.to_midi_number() + interval
            note = Note.from_midi_number(midi_num)
            if note is not None:
                notes.append(note)  # Append Note object directly
        
        return NotePattern(
            pattern=notes,
            data={"root_note": root_note, "scale_type": scale_type}
        )

    def _create_rhythm_pattern(
        self,
        durations: List[float],
        time_signature: Tuple[int, int]
    ) -> RhythmPattern:
        """Internal method to create a rhythm pattern."""
        rhythm_notes = []
        position = 0.0
        
        for duration in durations:
            # Create RhythmNote with only the required fields
            rhythm_note = RhythmNote(
                position=position,
                duration=duration
            )
            rhythm_notes.append(rhythm_note)
            position += duration
        
        total_duration = sum(durations)
        
        return RhythmPattern(
            pattern=rhythm_notes,
            time_signature=time_signature,
            total_duration=total_duration
        )
