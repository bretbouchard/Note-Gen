"""Module for note model."""
import re
from typing import Dict, Optional, ClassVar
from pydantic import BaseModel, ConfigDict, Field

class Note(BaseModel):
    """Model for musical notes."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    midi_number: int = Field(..., description="MIDI note number (0-127)")
    velocity: int = Field(64, description="Note velocity (0-127)")
    duration: float = Field(0.0, description="Note duration in beats")
    accidental: Optional[str] = Field(None, description="Note accidental (#, b, or None)")

    NOTE_NAMES: ClassVar[Dict[str, int]] = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11
    }

    NUMBER_TO_NOTE: Dict[int, str] = {
        0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E',
        5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A',
        10: 'A#', 11: 'B'
    }

    @property
    def base_name(self) -> str:
        """Get the base note name without octave."""
        note_number = self.midi_number % 12
        return self.NUMBER_TO_NOTE[note_number]

    @property
    def octave(self) -> int:
        """Get the octave of the note."""
        return (self.midi_number // 12) - 1

    @property
    def note_name(self) -> str:
        """Get the base note name."""
        return self.base_name

    @property
    def name(self) -> str:
        """Get the full note name including octave."""
        return f'{self.note_name}{self.octave}'

    @classmethod
    def from_name(cls, name: str, velocity: int = 64, duration: float = 0.0) -> "Note":
        """Create a note from a note name and optional velocity and duration."""
        
        match = re.match(r"([A-G][#b]?)(\d+)", name)
        if not match:
            raise ValueError(f"Invalid note name format: {name}")
    
        note_name, octave_str = match.groups()
        octave = int(octave_str)  # Octave is now required

        if octave < 0 or octave > 8:
            raise ValueError(f"Invalid octave: {octave}. Valid range is 0 to 8.")
    
        print(f"Note Name: {note_name}, Octave String: {octave_str}, Octave: {octave}")
        print(f"Parsed Note Name: {note_name}")
        print(f"Parsed Octave String: {octave_str}")
        print(f"Parsed Octave Value: {octave}")
    
        if note_name not in cls.NOTE_NAMES:
            raise ValueError(f"Invalid note name: {note_name}")
    
        if duration < 0:
            raise ValueError(f"Invalid duration: {duration}. Duration cannot be negative.")

        # Calculate MIDI number, ensuring octave is correctly factored in
        midi_number = cls.NOTE_NAMES[note_name] + (octave + 1) * 12  # +1 to align with MIDI standard
        if not (0 <= midi_number <= 127):
            raise ValueError(f"MIDI number {midi_number} out of range [0-127]")
    
        return cls(
            midi_number=midi_number,
            velocity=velocity,
            duration=duration,
            accidental='#' if '#' in note_name else 'b' if 'b' in note_name else None
        )

    @classmethod
    def from_midi(cls, midi_number: int, velocity: int = 64, duration: float = 0.0) -> "Note":
        """Create a note from a MIDI number."""
        if not (0 <= midi_number <= 127):
            raise ValueError(f"MIDI number must be between 0 and 127, got {midi_number}")
        return cls(midi_number=midi_number, velocity=velocity, duration=duration)

    def transpose(self, interval: int) -> "Note":
        """Transpose the note by a number of semitones."""
        new_midi = self.midi_number + interval
        if not (0 <= new_midi <= 127):
            raise ValueError(f"Transposition would result in invalid MIDI number: {new_midi}")
        return Note.from_midi(new_midi, self.velocity, self.duration)

    def __str__(self) -> str:
        """String representation of the note."""
        return self.name