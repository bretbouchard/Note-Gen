# src/note_gen/models/note.py

from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Any, Optional, ClassVar
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

    # Maps note names to their semitone values
    NOTE_TO_SEMITONE: ClassVar[dict[str, int]] = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11
    }

    # Maps semitone values to their note names (using sharps)
    SEMITONE_TO_NOTE: ClassVar[dict[int, str]] = {
        0: 'C', 1: 'C#', 2: 'D',
        3: 'D#', 4: 'E', 5: 'F',
        6: 'F#', 7: 'G', 8: 'G#',
        9: 'A', 10: 'A#', 11: 'B'
    }

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

    @property
    def midi_number(self) -> int:
        """Get the MIDI number for this note."""
        if self.stored_midi_number is not None:
            return self.stored_midi_number
        return self._note_octave_to_midi(self.note_name, self.octave)

    @classmethod
    def _midi_to_note_octave(cls, midi_number: int) -> tuple[str, int]:
        """Convert a MIDI number to a note name and octave."""
        if not (0 <= midi_number <= 127):
            raise ValueError("MIDI number out of range")
        semitone_to_note = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_number // 12) - 1
        note_index = midi_number % 12
        # Handle edge cases for octave 0
        if octave < 0:
            octave = 0
        # For MIDI number 127, we should allow octave 10
        if octave > 10:
            raise ValueError("MIDI number out of range")
        return semitone_to_note[note_index], octave

    @staticmethod
    def _note_octave_to_midi(note_name: str, octave: int) -> int:
        """Convert a note name and octave to a MIDI number."""
        if not (0 <= octave <= 8):
            raise ValueError("Octave must be between 0 and 8")
        note_to_semitone = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                           'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
        if note_name not in note_to_semitone:
            raise ValueError("Unrecognized note name")
        midi_number = (octave + 1) * 12 + note_to_semitone[note_name]
        if not (0 <= midi_number <= 127):
            raise ValueError("MIDI number out of range")
        return midi_number

    def get_note_at_interval(self, interval: int) -> str:
        """Get the note name at the specified interval from this note."""
        base_semitone = self.NOTE_TO_SEMITONE[self.note_name]
        new_semitone = (base_semitone + interval) % 12
        return self.SEMITONE_TO_NOTE[new_semitone]

    def transpose(self, semitones: int) -> 'Note':
        """Transpose the note by a number of semitones."""
        try:
            new_midi = self.midi_number + semitones
            if not (0 <= new_midi <= 127):
                raise ValueError("MIDI number out of range")
            note_name, octave = self._midi_to_note_octave(new_midi)
            if octave > 8:
                raise ValueError("MIDI number out of range")
            return Note(note_name=note_name, octave=octave, duration=self.duration, velocity=self.velocity)
        except (ValueError, ValidationError):
            raise ValueError("MIDI number out of range")

    def full_note_name(self) -> str:
        """Return the full note name."""
        return f"{self.note_name}{self.octave}"

    def __init__(self, **data):
        super().__init__(**data)

    def __str__(self) -> str:
        return self.full_note_name()