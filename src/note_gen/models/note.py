# src/note_gen/models/note.py

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
        if note_name is not None and not isinstance(note_name, str):
            raise ValueError(f"Invalid type for note_name: {type(note_name)}")
        if note_name and not re.match(r'^[A-GX][#b]?$', note_name):
            raise ValueError(f"Invalid note name: {note_name}")
        
        octave = values.get('octave')
        if octave is not None and not isinstance(octave, int):
            raise ValueError(f"Invalid type for octave: {type(octave)}")
        if octave is not None and not (0 <= octave <= 8):
            raise ValueError(f"Invalid octave: {octave}")
        
        duration = values.get('duration')
        if duration is not None and not isinstance(duration, (int, float)):
            raise ValueError(f"Invalid type for duration: {type(duration)}")
        if duration is not None and duration <= 0:
            raise ValueError("Input should be greater than 0")
        
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
    def fill_missing_fields(cls, data: Any) -> dict[str, Any]:
        """Fill missing fields in the note data."""
        if isinstance(data, dict):
            # Validate fields in the dictionary
            valid_keys = {"note_name", "octave", "duration", "velocity", "stored_midi_number"}
            if not all(k in valid_keys for k in data.keys()):
                raise ValueError("Unrecognized fields in dictionary")

            # If there's a note_name, check if it's recognized
            if "note_name" in data:
                if not re.match(r'^[A-G][#b]?$', data["note_name"]):
                    raise ValueError("Unrecognized note name")
            
            # If there's an octave, check if it's valid
            if "octave" in data:
                if not (0 <= data["octave"] <= 8):
                    raise ValueError(f"Invalid octave")

            return {
                "note_name": data.get("note_name", "C"),
                "octave": data.get("octave", 4),
                "duration": data.get("duration", 1.0),
                "velocity": data.get("velocity", 64),
                "stored_midi_number": data.get("stored_midi_number"),
            }
        elif isinstance(data, int):
            return {
                "note_name": "C",
                "octave": max(0, data // 12 - 1),
                "stored_midi_number": data
            }
        elif isinstance(data, str):
            return cls.from_name(data).model_dump()
        else:
            # Match the test's exact message
            raise ValueError("Expected a dict, int, or str for Note")

    @staticmethod
    def note_name_to_midi(note_name: str) -> int:
        """Convert a note name to its MIDI offset."""
        note_to_number = {
            "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
            "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
        }
        if note_name not in note_to_number:
            raise ValueError("Unrecognized note name")
        return note_to_number[note_name]

    @classmethod
    def _midi_to_note_octave(cls, midi_number: int) -> tuple[str, int]:
        if not (0 <= midi_number <= 127):
            raise ValueError(f"MIDI number out of range: {midi_number}")
        
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note_name = note_names[midi_number % 12]
        octave = max(0, midi_number // 12 - 1)
        
        return note_name, octave

    @staticmethod
    def _note_octave_to_midi(note_name: str, octave: int) -> int:
        """Convert a note name and octave to a MIDI number."""
        note_to_number = {
            "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
            "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
        }
        if note_name not in note_to_number:
            raise ValueError("Unrecognized note name")
        return (octave + 1) * 12 + note_to_number[note_name]

    @property
    def midi_number(self) -> int:
        """Compute the MIDI number."""
        if self.stored_midi_number is not None:
            return self.stored_midi_number
        return self._note_octave_to_midi(self.note_name, self.octave)

    def transpose(self, semitones: int) -> "Note":
        new_midi = self.midi_number + semitones
        if not (0 <= new_midi <= 127):
            raise ValueError(f"Resulting MIDI number out of range: {new_midi}")

        note_name, octave = self._midi_to_note_octave(new_midi)
        # Instead of clamping, check if octave is within allowed range
        if not ( -1 <= octave <= 8 ):
            raise ValueError(f"Resulting transposed octave out of range: {octave}")

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