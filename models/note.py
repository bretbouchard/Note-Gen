"""Module for handling musical notes."""
from __future__ import annotations

from typing import ClassVar, Dict, Union, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field

class Note(BaseModel):
    """A musical note with pitch and octave."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Note name (A-G)")
    accidental: str = Field(default="", description="Accidental (# or b)")
    octave: int = Field(default=4, description="Octave number")
    duration: float = Field(default=1.0, description="Note duration")
    velocity: int = Field(default=64, description="Note velocity")

    # Class constants
    NOTES: ClassVar[Dict[str, int]] = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
    }
    ACCIDENTALS: ClassVar[Dict[str, int]] = {
        '': 0, '#': 1, 'b': -1, '##': 2, 'bb': -2
    }

    @classmethod
    def from_name(cls, note_name: str) -> Note:
        """Create a note from a string name (e.g., 'C#4')."""
        # Extract note components
        name = note_name[0].upper()
        accidental = ""
        octave = 4  # Default octave

        # Extract accidental if present
        pos = 1
        while pos < len(note_name) and note_name[pos] in ['#', 'b']:
            accidental += note_name[pos]
            pos += 1

        # Extract octave if present
        if pos < len(note_name):
            try:
                octave = int(note_name[pos:])
            except ValueError:
                raise ValueError(f"Invalid octave in note name: {note_name}")

        return cls(name=name, accidental=accidental, octave=octave)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate note name."""
        if v.upper() not in cls.NOTES:
            raise ValueError(f"Invalid note name: {v}")
        return v.upper()

    @field_validator('accidental')
    @classmethod
    def validate_accidental(cls, v: str) -> str:
        """Validate accidental."""
        if v not in cls.ACCIDENTALS:
            raise ValueError(f"Invalid accidental: {v}")
        return v

    @field_validator('octave')
    @classmethod
    def validate_octave(cls, v: int) -> int:
        """Validate octave."""
        if not -2 <= v <= 8:
            raise ValueError("Octave must be between -2 and 8")
        return v

    @computed_field
    def note_name(self) -> str:
        """Get the full note name including accidental."""
        return f"{self.name}{self.accidental}"

    @computed_field
    def midi_note(self) -> int:
        """Get the MIDI note number."""
        return self.to_midi()

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: float) -> float:
        """Validate note duration."""
        if v <= 0:
            raise ValueError("Note duration must be greater than zero")
        return v

    @field_validator('velocity')
    @classmethod
    def validate_velocity(cls, v: int) -> int:
        """Validate note velocity."""
        if not 0 <= v <= 127:
            raise ValueError("Note velocity must be between 0 and 127")
        return v

    @classmethod
    def from_str(cls, note_str: str) -> Note:
        """Create a Note from a string representation."""
        if not note_str:
            raise ValueError("Empty note string")

        # Extract components
        name = note_str[0].upper()
        pos = 1
        accidental = ""
        while pos < len(note_str) and note_str[pos] in ['#', 'b']:
            accidental += note_str[pos]
            pos += 1
        
        # Get octave if present
        octave = 4
        if pos < len(note_str):
            try:
                octave = int(note_str[pos:])
            except ValueError:
                raise ValueError(f"Invalid octave in note string: {note_str}")

        return cls(name=name, accidental=accidental, octave=octave)

    @classmethod
    def from_midi(cls, midi_num: int) -> Note:
        """Create a Note from a MIDI number."""
        if not 0 <= midi_num <= 127:
            raise ValueError(f"MIDI number must be between 0 and 127, got {midi_num}")

        octave = (midi_num // 12) - 1
        note_num = midi_num % 12

        # Find closest natural note
        for name, base_num in cls.NOTES.items():
            if base_num == note_num:
                return cls(name=name, octave=octave, midi_number=midi_num)
            elif base_num > note_num:
                prev_name = list(cls.NOTES.keys())[list(cls.NOTES.values()).index(base_num) - 1]
                return cls(name=prev_name, accidental="#", octave=octave, midi_number=midi_num)

        # Handle special case for B#
        return cls(name='B', accidental="#", octave=octave, midi_number=midi_num)

    def to_midi(self) -> int:
        """Convert note to MIDI number."""
        base = self.NOTES[self.name]
        acc = self.ACCIDENTALS[self.accidental]
        midi_num = (self.octave + 1) * 12 + base + acc
        if not 0 <= midi_num <= 127:
            raise ValueError(f"Invalid MIDI number: {midi_num}")
        return midi_num

    def transpose(self, interval: int) -> Note:
        """Transpose note by given interval."""
        new_midi = self.to_midi() + interval
        if not 0 <= new_midi <= 127:
            raise ValueError(f"Transposition would result in invalid MIDI number: {new_midi}")
        return Note.from_midi(new_midi)

    def enharmonic(self) -> Note:
        """Get enharmonic equivalent of note."""
        midi_num = self.to_midi()
        current_note = (self.NOTES[self.name] + self.ACCIDENTALS[self.accidental]) % 12

        # Return natural notes as is
        if not self.accidental:
            return self

        # Always use flats for specific notes in minor scales
        if self.name == 'A' and self.accidental == '#':
            return Note(name='B', accidental='b', octave=self.octave, midi_number=midi_num)
        if self.name == 'B' and self.accidental == 'b':
            return Note(name='A', accidental='#', octave=self.octave, midi_number=midi_num)

        # Special case for C# -> Db
        if self.name == 'C' and self.accidental == '#':
            return Note(name='D', accidental='b', octave=self.octave, midi_number=midi_num)

        # Special case for Db -> C#
        if self.name == 'D' and self.accidental == 'b':
            return Note(name='C', accidental='#', octave=self.octave, midi_number=midi_num)

        # Try other enharmonics
        for name, base_num in self.NOTES.items():
            if (base_num - 1) % 12 == current_note:
                return Note(name=name, accidental="b", octave=self.octave, midi_number=midi_num)
            elif (base_num + 1) % 12 == current_note:
                return Note(name=name, accidental="#", octave=self.octave, midi_number=midi_num)

        # No enharmonic found
        return self

    def is_enharmonic(self, other: Note) -> bool:
        """Check if two notes are enharmonically equivalent."""
        return self.to_midi() == other.to_midi()

    def __str__(self) -> str:
        """String representation of note."""
        return f"{self.name}{self.accidental}{self.octave}"

    def __eq__(self, other: object) -> bool:
        """Compare notes by MIDI number."""
        if not isinstance(other, Note):
            return NotImplemented
        return self.to_midi() == other.to_midi()

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Union[int, float, str, None]]:
        """Convert to dictionary representation."""
        d = super().dict(*args, **kwargs)
        return d
