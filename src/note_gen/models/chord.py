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
    inversion: Optional[int] = Field(default=None, description="Inversion of the chord")

    def __init__(self, root: Note, notes: List[Note], quality: ChordQualityType = ChordQualityType.MAJOR, inversion: Optional[int] = None):
        logging.debug(f"Initializing Chord with root: {root}, notes: {notes}, quality: {quality}, inversion: {inversion}")
        self.root = Chord.validate_root(root)
        self.notes = Chord.validate_notes(notes)
        self.quality = Chord.validate_quality(quality)  # Ensure correct type is returned
        self.inversion = Chord.validate_inversion(inversion)
        logging.debug(f"Post-init quality: {self.quality}")
        logging.debug(f"Post-init inversion: {self.inversion}")

    @field_validator("notes")
    def validate_notes(cls, v: List[Note]) -> List[Note]:
        if not v:
            raise ValueError("Notes list cannot be empty.")
        if len(v) < 3:
            raise ValueError("A chord must have at least three notes.")
        return v

    @field_validator("root")
    def validate_root(cls, v: Note) -> Note:
        if not isinstance(v, Note):
            raise ValueError('Root must be a Note instance')
        return v

    @classmethod
    def validate_quality(cls, v: Any) -> ChordQualityType:
        if not isinstance(v, ChordQualityType):
            raise ValueError("Quality must be a valid ChordQualityType")
        return v

    @field_validator("inversion")
    def validate_inversion(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not isinstance(v, int):
            raise ValueError("Inversion must be an integer or None")
        return v

    @classmethod
    def from_base(cls, base: ChordBase) -> 'Chord':
        quality = cls.validate_quality(getattr(base, 'quality', ChordQualityType.MAJOR))
        inversion = getattr(base, 'inversion', 0)
        root = cls.validate_root(base.root)  # Validate root first
        instance = cls(root=root, quality=quality, inversion=inversion)  # Create an instance
        instance.notes = instance.generate_chord_notes(root=instance.root, quality=instance.quality, inversion=instance.inversion)  # Call on the instance and assign generated notes to the instance
        return instance

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

        self.root.transpose(semitones)
        for note in self.notes:
            note.transpose(semitones)
        return self

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