# src/note_gen/models/musical_elements.py

from typing import List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator
import logging

# Configure logging to write to a file
logging.basicConfig(filename='logs/debug.log', level=logging.DEBUG, filemode='a')
logger = logging.getLogger(__name__)

from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.note import Note

__all__ = ['Note', 'ChordQuality', 'Chord']


class ChordQuality(BaseModel):
    """Model for chord quality."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    quality_type: ChordQualityType = Field(default=ChordQualityType.MAJOR)
    has_seventh: bool = Field(default=False)
    has_ninth: bool = Field(default=False)
    has_eleventh: bool = Field(default=False)
    is_diminished: bool = Field(default=False)
    is_augmented: bool = Field(default=False)

    @classmethod
    def from_str(cls, quality_str: str) -> "ChordQuality":
        """Create a ChordQuality from a string."""
        quality_map = {
            'major': ChordQualityType.MAJOR,
            'minor': ChordQualityType.MINOR,
            'diminished': ChordQualityType.DIMINISHED,
            'augmented': ChordQualityType.AUGMENTED,
            'dominant': ChordQualityType.DOMINANT,
            'dominant7': ChordQualityType.DOMINANT_7,
            'major7': ChordQualityType.MAJOR_7,
            'minor7': ChordQualityType.MINOR_7,
            'diminished7': ChordQualityType.DIMINISHED_7,
            'half_diminished7': ChordQualityType.HALF_DIMINISHED_7,
            'major_seventh': ChordQualityType.MAJOR_SEVENTH,
            'minor_seventh': ChordQualityType.MINOR_SEVENTH,
            'diminished_seventh': ChordQualityType.DIMINISHED_SEVENTH,
        }
        quality_type = quality_map.get(quality_str.lower(), ChordQualityType.MAJOR)
        return cls(quality_type=quality_type)


class Chord(BaseModel):
    """Model for a musical chord."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Note
    quality: ChordQualityType = Field(default=ChordQualityType.MAJOR, description="Quality of the chord (e.g., Major, Minor).")
    notes: List[Note] = Field(default_factory=list, description="List of notes in the chord. Auto-generated if not provided.")
    inversion: int = Field(default=0, ge=0, description="Chord inversion. 0 means root position.")

    @model_validator(mode='before')
    def validate_chord(cls, values: dict[str, Any]) -> dict[str, Any]:
        root = values.get('root')
        if root is not None and root.octave < 0:
            raise ValueError("Root note octave must be greater than or equal to 0.")
        return values

    QUALITY_INTERVALS: Dict[ChordQualityType, List[int]] = {
        ChordQualityType.MAJOR: [0, 4, 7],
        ChordQualityType.MINOR: [0, 3, 7],
        ChordQualityType.DIMINISHED: [0, 3, 6],
        ChordQualityType.AUGMENTED: [0, 4, 8],
        ChordQualityType.DOMINANT: [0, 4, 7, 10],
        ChordQualityType.MAJOR_7: [0, 4, 7, 11],
        ChordQualityType.MINOR_7: [0, 3, 7, 10],
    }

    @model_validator(mode='after')
    def generate_notes_if_none(self) -> "Chord":
        """Generate notes if the `notes` attribute is empty."""
        if not self.notes:
            self.notes = self.generate_chord_notes()
        return self
    
    def transpose(self, semitones: int) -> "Chord":
        """Transpose the chord by a given number of semitones."""
        transposed_root = self.root.transpose(semitones)
        return Chord(root=transposed_root, quality=self.quality, notes=[
            note.transpose(semitones) for note in self.notes
        ])

    def generate_chord_notes(self) -> List[Note]:
        """Generate the notes of the chord based on quality and inversion."""
        if not isinstance(self.root, Note):
            raise ValueError("Root must be a valid Note instance.")

        intervals = self.QUALITY_INTERVALS.get(self.quality, [0, 4, 7])
        base_midi = self.root.midi_number
        notes = [Note.from_midi(base_midi + interval) for interval in intervals]

        # Log the generated notes
        logger.debug(f"Generated notes for chord: {[note.note_name for note in notes]}")

        # Apply inversion if specified
        for _ in range(self.inversion):
            first_note = notes.pop(0)
            transposed_note = first_note.transpose(12)  # Move up an octave
            notes.append(transposed_note)

        return notes

    @classmethod
    def from_quality(cls, root: Note, quality: str) -> "Chord":
        """Create a chord from a root note and quality."""
        if not isinstance(root, Note):
            raise ValueError("Root must be a valid Note instance.")
        if quality is None:
            raise ValueError("Quality must be a valid ChordQualityType.")
        chord_quality = ChordQuality.from_str(quality)
        return cls(root=root, quality=chord_quality.quality_type)

    def __str__(self) -> str:
        """String representation of the chord."""
        return (
            f"Chord("
            f"root={self.root}, "
            f"quality={self.quality}, "
            f"notes={[str(note) for note in self.notes]}, "
            f"inversion={self.inversion}"
            f")"
        )

    def __repr__(self) -> str:
        return (f"Chord(root={self.root}, quality={self.quality}, "
                f"notes={self.notes}, inversion={self.inversion})")