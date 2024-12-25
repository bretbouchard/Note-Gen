from __future__ import annotations
import logging
from typing import TypeAlias, Literal, List, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.note_gen.models.musical_elements import Note
from src.note_gen.models.base_types import MusicalBase
from src.note_gen.models.chord_base import ChordBase
from src.note_gen.models.enums import ChordQualityType

if TYPE_CHECKING:
    pass

# Define Literal types for warnings and modes
Modes: TypeAlias = Literal["json", "python"]
Warnings: TypeAlias = Literal["none", "warn", "error"]

# Configure logging to output to console
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Chord(MusicalBase, BaseModel):
    """A musical chord."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Note = Field(..., description="Root note of the chord")
    quality: Optional[ChordQualityType] = Field(
        default=ChordQualityType.MAJOR, description="Quality of the chord"
    )
    notes: List[Note] = Field(
        default_factory=list, description="List of notes in the chord"
    )
    bass: Optional[Note] = Field(default=None, description="Bass note of the chord")
    duration: Optional[float] = Field(default=None, description="Duration of the chord")
    velocity: Optional[int] = Field(default=None, description="Velocity of the chord")
    inversion: Optional[int] = Field(default=0, description="Inversion of the chord")

    @field_validator("quality")
    def validate_quality(cls, value: Optional[ChordQualityType]) -> None:
        valid_qualities = [
            ChordQualityType.MAJOR,
            ChordQualityType.MINOR,
            ChordQualityType.DIMINISHED,
            ChordQualityType.AUGMENTED,
        ]
        if quality is None:
            raise ValueError("Quality must be specified")
        if value and value not in valid_qualities:
            raise ValueError(f"Invalid chord quality: {value}")

    @field_validator("root")
    def validate_root(cls, v):
        if not isinstance(v, Note):
            raise ValueError("Root must be a Note instance")
        return v

    @field_validator("notes")
    def validate_notes(cls, v):
        if not v:
            raise ValueError("Chord notes cannot be empty")
        if not all(isinstance(note, Note) for note in v):
            raise ValueError("All notes must be Note instances.")
        return v

    def __init__(
        self,
        *,
        root: Note,
        quality: Optional[ChordQualityType] = ChordQualityType.MAJOR,
        notes: List[Note] = None,
        bass: Optional[Note] = None,
        duration: Optional[float] = None,
        velocity: Optional[int] = None,
        inversion: Optional[int] = 0,
    ) -> None:
        logging.debug(
            f"Initializing Chord with root: {root}, quality: {quality}, notes: {notes}"
        )
        if quality is None:
            raise ValueError("Quality must be specified")
        if not isinstance(root, Note):
            raise ValueError("Root must be a Note instance")
        if quality not in ChordQualityType:
            raise ValueError(f"Invalid chord quality: {quality}")
        if notes is None or not notes:
            raise ValueError("Chord notes cannot be empty")
        if not all(isinstance(note, Note) for note in notes):
            raise ValueError("All notes must be Note instances.")
        super().__init__(
            root=root,
            quality=quality,
            notes=notes,
            bass=bass,
            duration=duration,
            velocity=velocity,
            inversion=inversion,
        )
        self.quality = quality
        self.inversion = inversion

    def generate_chord_notes(self) -> List[Note]:
        """Generate notes for the chord based on its quality and root."""
        if self.quality is None:
            raise ValueError("Chord quality must be specified.")
        if not isinstance(self.root, Note):
            raise ValueError("Root must be a Note instance")
        if not self.notes:
            raise ValueError("Chord notes cannot be empty")
        if not all(isinstance(note, Note) for note in self.notes):
            raise ValueError("All notes must be Note instances.")

        if self.quality == ChordQualityType.MAJOR:
            return [
                self.root,
                Note(name="E", octave=self.root.octave),  # Major third
                Note(name="G", octave=self.root.octave),  # Perfect fifth
            ]
        elif self.quality == ChordQualityType.MINOR:
            return [
                self.root,
                Note(name="D", octave=self.root.octave),  # Minor third
                Note(name="G", octave=self.root.octave),  # Perfect fifth
            ]
        elif self.quality == ChordQualityType.DIMINISHED:
            return [
                self.root,
                Note(name="D#", octave=self.root.octave),  # Diminished third
                Note(name="F#", octave=self.root.octave),  # Diminished fifth
            ]
        elif self.quality == ChordQualityType.AUGMENTED:
            return [
                self.root,
                Note(name="E", octave=self.root.octave),  # Major third
                Note(name="B", octave=self.root.octave),  # Augmented fifth
            ]
        else:
            raise ValueError(f"Invalid chord quality: {self.quality}")

    def transpose(self, semitones: int) -> "Chord":
        """Transpose the chord by a given number of semitones."""
        if not isinstance(self.root, Note):
            raise ValueError("Root note cannot be None")
        if not self.quality:
            raise ValueError("Quality must be a string instance")

        new_root = self.root.transpose(semitones)
        new_notes = [Note(name=note.name, octave=note.octave) for note in self.notes]
        return Chord(
            root=new_root,
            quality=self.quality,
            notes=new_notes,
            inversion=self.inversion,
        )

    def __str__(self) -> str:
        return f"Chord(root={self.root}, quality={self.quality})"

    def from_base(cls, base: ChordBase) -> "Chord":
        """Create a chord from a ChordBase instance."""
        if not isinstance(base, ChordBase):
            raise ValueError("Invalid base: must be a ChordBase instance")

        if not isinstance(base.root, Note):
            raise ValueError("Base root must be a Note object")

        root_note = Note.from_midi(base.root.midi_number)
        notes = [
            Note.from_midi(base.root.midi_number + interval)
            for interval in base.intervals
        ]

        quality = base.quality if hasattr(base, "quality") else "major"

        return cls(root=root_note, quality=quality, notes=notes, inversion=0)

    def _apply_inversion(self, notes: List[Note], inversion: int) -> List[Note]:
        """Apply inversion to the chord notes."""
        if not notes:
            return notes

        effective_inversion = inversion % len(notes)
        if effective_inversion == 0:
            return notes.copy()

        inverted_notes = notes.copy()
        for _ in range(effective_inversion):
            first_note = inverted_notes.pop(0)
            inverted_notes.append(first_note)

        return inverted_notes


Chord.model_rebuild()

# Example instantiation for testing