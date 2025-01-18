# src/note_gen/models/musical_elements.py

from typing import List, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
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
            'dominant': ChordQualityType.DOMINANT_7,
            'dominant7': ChordQualityType.DOMINANT_7,
            'major7': ChordQualityType.MAJOR_7,
            'minor7': ChordQualityType.MINOR_7,
            'diminished7': ChordQualityType.DIMINISHED_7,
            'half_diminished7': ChordQualityType.HALF_DIMINISHED_7,
            'augmented7': ChordQualityType.AUGMENTED_7,
            'major9': ChordQualityType.MAJOR_9,
            'minor9': ChordQualityType.MINOR_9,
            'dominant9': ChordQualityType.DOMINANT_9,
            'major11': ChordQualityType.MAJOR_11,
            'minor11': ChordQualityType.MINOR_11,
            'dominant11': ChordQualityType.DOMINANT_11,
            'sus2': ChordQualityType.SUS2,
            'sus4': ChordQualityType.SUS4,
            '7sus4': ChordQualityType.SEVEN_SUS4,
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

    def __init__(self, root: Note, quality: ChordQualityType = ChordQualityType.MAJOR, notes: List[Note] = [], inversion: int = 0) -> None:
        logger.debug(f'Initializing Chord with root: {root}, quality: {quality}, notes: {notes}, inversion: {inversion}')  # Log initialization
        # Convert string quality to ChordQualityType if needed
        if isinstance(quality, str):
            quality = ChordQualityType(quality)
        super().__init__(root=root, quality=quality, notes=notes or [], inversion=inversion)
        if not self.notes:  # If notes are not provided, generate them based on quality
            self.notes = self.generate_notes()

    @field_validator('quality', mode='before')
    @classmethod
    def validate_quality(cls, v: Any) -> ChordQualityType:
        """Validate the chord quality."""
        logger.debug(f'Validating quality: {v}')  # Log the quality being validated
        
        if isinstance(v, ChordQualityType):
            return v
            
        if isinstance(v, str):
            try:
                # First try to get the enum directly
                return ChordQualityType(v)
            except ValueError:
                try:
                    # If that fails, try the _missing_ method for aliases
                    quality = ChordQualityType._missing_(v)
                    if quality is not None:
                        return quality
                except Exception:
                    pass
                
                # If all else fails, try lowercase
                try:
                    return ChordQualityType(v.lower())
                except ValueError:
                    logger.warning(f"Invalid chord quality '{v}', defaulting to major")
                    return ChordQualityType.MAJOR
        
        logger.warning(f"Invalid chord quality type: {type(v)}, defaulting to major")
        return ChordQualityType.MAJOR

    @field_validator('root', mode='before')
    @classmethod
    def validate_root(cls, v: Any) -> Note:
        """Validate the root note."""
        logger.debug(f'Validating root: {v}')
        
        if isinstance(v, Note):
            return v
            
        if isinstance(v, dict):
            try:
                return Note(**v)
            except Exception as e:
                logger.error(f"Error creating Note from dict: {e}")
                return Note(note_name='C')
                
        if isinstance(v, str):
            try:
                return Note(note_name=v)
            except Exception as e:
                logger.error(f"Error creating Note from string: {e}")
                return Note(note_name='C')
        
        logger.error(f"Invalid root note type: {type(v)}")
        return Note(note_name='C')

    @field_validator('inversion')
    @classmethod
    def validate_inversion(cls, v: int) -> int:
        """Validate the inversion."""
        if not isinstance(v, int):
            raise ValueError("Inversion must be an integer")
        if v < 0:
            raise ValueError("Inversion cannot be negative")
        return v

    def generate_notes(self) -> List[Note]:
        """Generate the notes for this chord based on its root and quality."""
        notes = []
        root_note = self.root

        # Get intervals based on chord quality
        intervals = self.quality.get_intervals()

        # Generate notes
        for interval in intervals:
            note = Note(
                note_name=root_note.get_note_at_interval(interval),
                octave=root_note.octave,
                duration=1.0,
                velocity=64
            )
            notes.append(note)

        # Apply inversion if needed
        if self.inversion > 0:
            for _ in range(self.inversion):
                # Move the first note up an octave
                first_note = notes.pop(0)
                first_note.octave += 1
                notes.append(first_note)

        return notes

    def get_notes(self) -> List[Note]:
        """Get the notes in this chord."""
        if not self.notes:
            self.notes = self.generate_notes()
        return self.notes

    def transpose(self, semitones: int) -> "Chord":
        """Transpose the chord by a given number of semitones."""
        self.root = self.root.transpose(semitones)
        self.notes = [note.transpose(semitones) for note in self.notes]
        return self

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

    @classmethod
    def from_quality(cls, root: Note, quality: str) -> "Chord":
        """Create a chord from a root note and quality."""
        if not isinstance(root, Note):
            raise ValueError("Root must be a valid Note instance.")
        if quality is None:
            raise ValueError("Quality must be a valid ChordQualityType.")
        chord_quality = ChordQuality.from_str(quality)
        return cls(root=root, quality=chord_quality.quality_type)

    def generate_chord_notes(self) -> List[Note]:
        """Generate the notes of the chord based on quality and inversion."""
        if not isinstance(self.root, Note):
            raise ValueError("Root must be a valid Note instance.")

        intervals = self.quality.get_intervals()
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