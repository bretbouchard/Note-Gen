from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Any, Optional
import re


class Note(BaseModel):
    """A musical note with optional MIDI number auto-population."""

    note_name: str = Field(
        default="C",
        description="The pitch class (e.g., 'C', 'C#', 'Db')."
    )
    octave: int = Field(
        default=4,
        ge=0,
        le=8,
        description="Octave range 0–8."
    )
    duration: float = Field(
        default=1.0,
        gt=0,
        description="Duration must be positive and non-zero."
    )
    velocity: int = Field(
        default=64,
        ge=0,
        le=127,
        description="MIDI velocity, 0–127."
    )
    stored_midi_number: Optional[int] = Field(
        default=None,
        description="Stored MIDI number, overrides note_name and octave."
    )

    @model_validator(mode='before')
    def validate_and_fill(cls, values: dict[str, Any]) -> dict[str, Any]:
        note_name = values.get('note_name')
        if note_name and not re.match(r'^[A-G][#b]?$', note_name):
            raise ValueError(f"Invalid note name: {note_name}")
        return values

    @staticmethod
    def normalize_note_name(name: str) -> str:
        """Normalize the note name to uppercase and valid accidentals."""
        match = re.match(r"^[A-Ga-g][#b]?$", name)
        if not match:
            raise ValueError(f"Invalid note name: {name}")
        return name.capitalize()

    @classmethod
    def from_name(cls, name: str, duration: float = 1.0, velocity: int = 64) -> "Note":
        """Create a Note from a name like 'C4', 'C#3', etc."""
        match = re.match(r"^([A-Ga-g#b]+)(\d+)$", name)
        if not match:
            raise ValueError(f"Invalid note name format: {name}")
        note_name, octave = match.groups()
        return cls(
            note_name=cls.normalize_note_name(note_name),
            octave=int(octave),
            duration=duration,
            velocity=velocity
        )

    @classmethod
    def from_full_name(cls, full_name: str) -> "Note":
        """Create a Note from a full name like 'C4'."""
        match = re.match(r"^([A-Ga-g#b]+)(\d+)$", full_name)
        if not match:
            raise ValueError(f"Invalid note name format: {full_name}")
        note_name, octave = match.groups()
        return cls(note_name=cls.normalize_note_name(note_name), octave=int(octave))

    @classmethod
    def from_midi(cls, midi_number: int, velocity: int = 64, duration: float = 1.0) -> "Note":
        """Create a Note from a MIDI number (0–127)."""
        if not (0 <= midi_number <= 127):
            raise ValueError(f"MIDI number out of range: {midi_number}")
        note_name, octave = cls._midi_to_note_octave(midi_number)
        return cls(
            note_name=note_name,
            octave=octave,
            duration=duration,
            velocity=velocity,
            stored_midi_number=midi_number
        )

    @classmethod
    def fill_missing_fields(cls, data: dict) -> dict:
        """Fill missing fields in the note data."""
        if not isinstance(data, dict):
            raise ValueError("Input should be a valid dictionary.")
        # Fill in default values for missing fields
        return {
            "note_name": data.get("note_name", "C"),
            "octave": data.get("octave", 4),
            "duration": data.get("duration", 1.0),
            "velocity": data.get("velocity", 64),
            "stored_midi_number": data.get("stored_midi_number", None),
        }

    @staticmethod
    def _note_octave_to_midi(note_name: str, octave: int) -> int:
        """Convert a note name and octave to a MIDI number."""
        note_to_number = {
            "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
            "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
        }
        if note_name not in note_to_number:
            raise ValueError(f"Invalid note name: {note_name}")
        return (octave + 1) * 12 + note_to_number[note_name]

    @staticmethod
    def _midi_to_note_octave(midi_num: int) -> tuple[str, int]:
        """Convert MIDI number to note name and octave."""
        number_to_note = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (midi_num // 12) - 1
        note = number_to_note[midi_num % 12]
        return note, octave

    @property
    def midi_number(self) -> int:
        """Compute the MIDI number."""
        if self.stored_midi_number is None:
            return 0  # Default value if None
        return self.stored_midi_number

    def transpose(self, semitones: int) -> "Note":
        """Transpose the note by a number of semitones."""
        new_midi = self.midi_number + semitones
        if not (0 <= new_midi <= 127):
            raise ValueError(f"Resulting MIDI number out of range: {new_midi}")

        note_name, octave = self._midi_to_note_octave(new_midi)
        return Note(
            note_name=note_name,
            octave=octave,
            duration=self.duration,
            velocity=self.velocity,
            stored_midi_number=new_midi
        )

    def full_note_name(self) -> str:
        """Return the full note name."""
        return f"{self.note_name}{self.octave}"

    def __str__(self) -> str:
        return self.full_note_name()