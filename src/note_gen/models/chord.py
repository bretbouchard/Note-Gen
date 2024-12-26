from __future__ import annotations
import logging
from typing import TypeAlias, Literal, List, Optional, TYPE_CHECKING, Any, Union
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


class Chord(BaseModel):
    root: Note
    notes: List[Note]
    quality: ChordQualityType = Field(default=ChordQualityType.MAJOR)
    inversion: int = Field(default=0, description="Inversion of the chord")

    def __init__(self, root: Note, notes: List[Note], quality: ChordQualityType = ChordQualityType.MAJOR, inversion: Optional[int] = None):
        logging.debug(f"Initializing Chord with root: {root}, notes: {notes}, quality: {quality}, inversion: {inversion}")
        self.root = root
        self.notes = notes
        self.quality = quality
        self.inversion = inversion
        logging.debug(f"Post-init quality: {self.quality}")
        self.validate_notes(notes)
        self.validate_root(root)
        self.validate_quality(quality)

    @classmethod
    def validate_notes(cls, notes: List[Note]) -> None:
        if not notes:
            logging.error("Notes list cannot be empty.")
            raise ValueError("Notes list cannot be empty.")
        if len(notes) < 3:
            logging.error("A chord must have at least three notes.")
            raise ValueError("A chord must have at least three notes.")
        logging.debug(f"Notes validation passed for notes: {notes}")

    @classmethod
    def validate_root(cls, root: Note) -> Note:
        if not isinstance(root, Note):
            raise ValueError('Root must be a Note instance')
        return root

    @classmethod
    def validate_quality(cls, value: Any) -> ChordQualityType:
        if not isinstance(value, ChordQualityType):
            raise ValueError('Quality must be a ChordQualityType instance')
        return value

    @classmethod
    def from_base(cls, base: ChordBase) -> 'Chord':
        notes = cls.generate_chord_notes(base.root, base.quality, base.inversion)
        return cls(root=base.root, notes=notes, quality=base.quality, inversion=base.inversion)

    def generate_chord_notes(self, root: Note, quality: ChordQualityType, inversion: Optional[int] = None) -> List[Note]:
        """Generate notes for the chord based on its quality and root."""
        if quality is None:
            raise ValueError("Chord quality must be specified.")
        if not isinstance(root, Note):
            raise ValueError("Root must be a Note instance")

        # Generate chord notes based on quality
        if quality == ChordQualityType.MAJOR:
            return [
                root,
                Note(name="E", octave=root.octave),  # Major third
                Note(name="G", octave=root.octave),  # Perfect fifth
            ]
        elif quality == ChordQualityType.MINOR:
            return [
                root,
                Note(name="D", octave=root.octave),  # Minor third
                Note(name="G", octave=root.octave),  # Perfect fifth
            ]
        elif quality == ChordQualityType.DIMINISHED:
            return [
                root,
                Note(name="D", octave=root.octave),  # Minor third
                Note(name="F", octave=root.octave),  # Diminished fifth
            ]
        # Add additional quality cases as needed
        return []  # Default case if no quality matches

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