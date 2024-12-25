from __future__ import annotations
import logging
from typing import ClassVar, Dict, Any, TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict, Field, validator
from src.note_gen.models.base_types import MusicalBase


if TYPE_CHECKING:
    from src.note_gen.models.scale import Scale  # Forward reference for type hinting

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Note(MusicalBase, BaseModel):
    """A musical note representation."""

    NOTES: ClassVar[Dict[str, int]] = {
        "C": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
        "Cb": -1,
        "B#": 12,
        "Dbb": 1,
        "Ebb": 2,
        "Fb": 4,
        "Gbb": 5,
        "Abb": 8,
        "Bbb": 10,
        "C4": 0,
        "C#4": 1,
        "Db4": 1,
        "D4": 2,
        "D#4": 3,
        "Eb4": 3,
        "E4": 4,
        "F4": 5,
        "F#4": 6,
        "Gb4": 6,
        "G4": 7,
        "G#4": 8,
        "A4": 9,
        "A#4": 10,
        "B4": 11,
    }

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Name of the note")
    octave: int = Field(..., description="Octave of the note")
    velocity: int = Field(default=100, description="Velocity of the note")
    duration: float = Field(default=1.0, description="Duration of the note")

    @validator("name")
    def validate_name(cls, value: str) -> str:
        if not value:
            raise ValueError("Note name cannot be empty.")
        if value not in cls.NOTES:
            raise ValueError(f"Invalid note name: {value}")
        return value

    @property
    def midi_number(self) -> int:
        """Calculate the MIDI number for the note."""
        return (self.octave + 1) * 12 + self.NOTES[self.name]

    def transpose(self, semitones: int) -> "Note":
        """Transpose the note by a given number of semitones."""
        new_octave = self.octave + (self.NOTES[self.name] + semitones) // 12
        new_name = self.semitone_to_note_name((self.NOTES[self.name] + semitones) % 12)
        return Note(
            name=new_name,
            octave=new_octave,
            velocity=self.velocity,
            duration=self.duration,
        )

    def shift_octave(self, octaves: int) -> "Note":
        """Shift the note by a given number of octaves."""
        return Note(
            name=self.name,
            octave=self.octave + octaves,
            velocity=self.velocity,
            duration=self.duration,
        )

    @property
    def note_name(self) -> str:
        return self.name  # Assuming name represents the note name

    @property
    def accidental(self) -> Optional[str]:
        if "#" in self.name:
            return "#"
        elif "b" in self.name:
            return "b"
        return None

    def get_note_name(self) -> str:
        return self.name

    @staticmethod
    def note_to_semitone(name: str) -> int:
        """Convert note name to semitone value."""
        note_mapping = {
            "C": 0,
            "C#": 1,
            "Db": 1,
            "D": 2,
            "D#": 3,
            "Eb": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "Gb": 6,
            "G": 7,
            "G#": 8,
            "Ab": 8,
            "A": 9,
            "A#": 10,
            "Bb": 10,
            "B": 11,
            "Cb": -1,
            "B#": 12,
            "Dbb": 1,
            "Ebb": 2,
            "Fb": 4,
            "Gbb": 5,
            "Abb": 8,
            "Bbb": 10,
        }
        return note_mapping.get(name, -1)  # Returns -1 for invalid notes

    @staticmethod
    def semitone_to_note_name(semitone: int) -> str:
        """Convert semitone value back to note name."""
        # Implement reverse mapping if necessary
        pass

    def __str__(self) -> str:
        accidental_str = f" {self.accidental}" if self.accidental else ""
        return f"Note(name='{self.name}{accidental_str}', octave={self.octave})"

    def calculate_midi_number(self) -> int:
        """Calculate MIDI number based on note name, accidental, and octave."""
        # Get the base value for the note from NOTES dictionary
        base_value = self.NOTES.get(self.name, 0)

        # Add accidental modification
        accidental_value = 0
        if self.accidental == "#":
            accidental_value = 1
        elif self.accidental == "b":
            accidental_value = -1

        # Calculate the complete MIDI number
        midi_number = ((self.octave + 1) * 12) + base_value + accidental_value

        return midi_number

    @classmethod
    def from_name(cls, note_name: str) -> "Note":
        """Create a note from a string name (e.g., 'C#4').

        Args:
            note_name (str): String representation of the note

        Returns:
            Note: Created note object

        Raises:
            ValueError: If the note name is invalid
        """
        logger.debug(f"Attempting to create Note from string: {note_name}")
        try:
            # Extract note components
            name = note_name[0].upper()
            accidental = ""
            octave = 4  # Default octave

            # Extract accidental if present
            pos = 1
            while pos < len(note_name) and note_name[pos] in ["#", "b"]:
                accidental += note_name[pos]
                pos += 1

            # Extract octave if present
            if pos < len(note_name):
                octave = int(note_name[pos:])

            note = cls(name=name + accidental, octave=octave)
            logger.debug(f"Created Note: {note}")
            return note
        except ValueError as e:
            logger.error(f"Invalid note name: {note_name}")
            raise ValueError(f"Invalid note name: {note_name}") from e

    @classmethod
    def from_str(cls, note_str: str) -> "Note":
        """Create a Note from a string representation.

        Args:
            note_str (str): String representation of the note

        Returns:
            Note: Created note object

        Raises:
            ValueError: If the note string is invalid
        """
        if not note_str:
            logger.error("Empty note string")
            raise ValueError("Empty note string")

        logger.debug(f"Creating Note from string: {note_str}")
        try:
            # Extract components
            name = note_str[0].upper()
            pos = 1
            accidental = ""
            while pos < len(note_str) and note_str[pos] in ["#", "b"]:
                accidental += note_str[pos]
                pos += 1

            # Get octave if present
            octave = 4
            if pos < len(note_str):
                octave = int(note_str[pos:])

            note = cls(name=name + accidental, octave=octave)
            logger.debug(f"Created Note: {note}")
            return note
        except ValueError as e:
            logger.error(f"Invalid note string: {note_str}")
            raise ValueError(f"Invalid note string: {note_str}") from e

    @classmethod
    def from_midi(cls, midi_number: int) -> "Note":
        """Create a Note instance from a MIDI number.

        Args:
            midi_number (int): MIDI number

        Returns:
            Note: Created note object
        """
        octave = min(
            midi_number // 12, 8
        )  # Calculate octave from MIDI number, capping at 8
        note_name = cls.get_note_name(
            midi_number % 12
        )  # Get note name from MIDI number
        return cls(name=note_name, octave=octave)

    def is_enharmonic(self, other: "Note") -> bool:
        """Check if two notes are enharmonically equivalent.

        Args:
            other (Note): Other note to compare with

        Returns:
            bool: Whether the notes are enharmonically equivalent
        """
        return self.midi_number == other.midi_number

    def enharmonic(self) -> "Note":
        """Get enharmonic equivalent of note.

        Returns:
            Note: Enharmonic equivalent note object
        """
        midi_num = self.midi_number
        current_note = (
            self.NOTES[self.name] + self.ACCIDENTALS.get(self.accidental, 0)
        ) % 12

        # Return natural notes as is
        if not self.accidental:
            return self
        # Logic for enharmonic equivalent can be added here
        for name, base_num in self.NOTES.items():
            if (base_num - 1) % 12 == current_note:
                return Note(
                    name=name, accidental="b", octave=self.octave, midi_number=midi_num
                )
            elif (base_num + 1) % 12 == current_note:
                return Note(
                    name=name, accidental="#", octave=self.octave, midi_number=midi_num
                )

        # No enharmonic found
        return self

    def __eq__(self, other: object) -> bool:
        """Compare notes by MIDI number.

        Args:
            other (object): Other note to compare with

        Returns:
            bool: Whether the notes are equal
        """
        if not isinstance(other, Note):
            return NotImplemented
        return self.midi_number == other.midi_number

    def __add__(self, interval: int) -> "Note":
        """Add an interval (in semitones) to the current note.

        Args:
            interval (int): The interval to add.

        Returns:
            Note: A new Note object representing the transposed note.
        """
        # Calculate the new MIDI number
        new_midi_number = self.midi_number + interval
        # Create a new Note from the new MIDI number
        return Note.from_midi(new_midi_number)

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of note
        """
        d = super().model_dump(*args, **kwargs)
        return d

    @staticmethod
    def get_note_name(midi_number: int) -> str:
        """Get the note name from a MIDI number without octave."""
        # Map MIDI note numbers (0-11) to note names
        note_names = {
            0: "C",
            1: "C#",
            2: "D",
            3: "D#",
            4: "E",
            5: "F",
            6: "F#",
            7: "G",
            8: "G#",
            9: "A",
            10: "A#",
            11: "B",
        }
        # Get the note name by taking the modulo 12 of the MIDI number
        return note_names.get(midi_number % 12, "Unknown Note")

    def note_name_octave(self) -> str:
        """Note name with octave (e.g., C4)

        Returns:
            str: Note name with octave
        """
        return f"{self.name}{self.octave}"

    def scale(self, scale_type: str) -> Scale:
        from .scale import Scale  # Local import to avoid circular import
        from .scale_info import ScaleInfo  # Import ScaleInfo

        return Scale(
            scale=ScaleInfo(scale_type=scale_type, root=self),
            numeral="I",
            numeral_str="I",
            scale_degree=1,
            quality=scale_type,
            is_major=True,
            is_diminished=False,
            is_augmented=False,
            is_half_diminished=False,
            has_seventh=False,
            has_ninth=False,
            has_eleventh=False,
            inversion=0,
        )
