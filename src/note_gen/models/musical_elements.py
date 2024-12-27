# src/note_gen/models/musical_elements.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from pydantic.config import ConfigDict
from src.note_gen.models.enums import AccidentalType


class Note(BaseModel):
    """A musical note."""

    name: str = Field(..., description="Name of the note")
    octave: int = Field(..., description="Octave of the note")
    velocity: int = Field(default=100, description="Velocity of the note")
    duration: float = Field(default=1.0, description="Duration of the note")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def midi_number(self) -> int:
        """Calculate the MIDI number for the note."""
        return (self.octave + 1) * 12 + self.note_to_semitone(self.name)

    def transpose(self, semitones: int) -> "Note":
        """Transpose the note by a given number of semitones."""
        new_octave = self.octave + (self.note_to_semitone(self.name) + semitones) // 12
        new_name = self.semitone_to_note_name(
            (self.note_to_semitone(self.name) + semitones) % 12
        )
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
    def accidental(self) -> Optional[str]:
        if "#" in self.name:
            return "#"
        elif "b" in self.name:
            return "b"
        return None

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
        reverse_mapping = {
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
        return reverse_mapping.get(
            semitone % 12, "Invalid"
        )  # Return 'Invalid' for out-of-range values


class MusicalBase:
    pass


class Chord(MusicalBase, BaseModel):
    """A musical chord."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Note = Field(..., description="Root note of the chord")
    quality: Optional[str] = Field(default=None, description="Quality of the chord")
    notes: List[Note] = Field(
        default_factory=list, description="List of notes in the chord"
    )

    @field_validator("quality")
    def validate_quality(cls, value: Optional[str]) -> None:
        valid_qualities = ["major", "minor", "diminished", "augmented"]
        if value and value not in valid_qualities:
            raise ValueError(f"Invalid chord quality: {value}")

    def generate_chord_notes(self) -> List[Note]:
        """Generate notes for the chord based on its quality and root."""
        intervals = {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "diminished": [0, 3, 6],
            "augmented": [0, 4, 8],
        }
        if self.quality not in intervals:
            return []  # Return empty if quality is invalid
        return [self.root.transpose(interval) for interval in intervals[self.quality]]

    def transpose(self, semitones: int) -> "Chord":
        """Transpose the chord by a given number of semitones."""
        transposed_notes = [note.transpose(semitones) for note in self.notes]
        return Chord(
            root=self.root.transpose(semitones),
            quality=self.quality,
            notes=transposed_notes,
        )

    def __str__(self) -> str:
        return f"Chord(root={self.root}, quality={self.quality})"


# Add other foundational classes as necessary
