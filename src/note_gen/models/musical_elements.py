# src/note_gen/models/musical_elements.py

from typing import List, Optional, Union , Any
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

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Note
    quality: ChordQualityType
    notes: List[Note] = []
    inversion: int = 0

    def __init__(self, root: Note, quality: Union[str, ChordQualityType], notes: Optional[List[Note]] = None, inversion: int = 0):
        logger.debug(f"Initializing Chord with root: {root}, quality: {quality}")
        if isinstance(quality, str):
            if quality not in [q.value for q in ChordQualityType]:
                logger.error(f"Invalid quality: '{quality}'. Must be one of: {[q.value for q in ChordQualityType]}")
                raise ValueError(f"Invalid quality: '{quality}'. Must be one of: {[q.value for q in ChordQualityType]}")
            quality = ChordQualityType(quality)
        if notes is None:
            notes = []  # Initialize to an empty list if not provided

        super().__init__(root=root, quality=quality, notes=notes, inversion=inversion)

        # Generate notes based on root and quality
        self.notes = self._generate_chord_notes(root, quality)

        if inversion > 0:
            self.notes = self._apply_inversion(self.notes, inversion)


    @field_validator('quality', mode='before')
    @classmethod
    def validate_quality(cls, v: Any) -> ChordQualityType:
        """Validate the chord quality."""
        logger.debug(f'Validating quality: {v}')  # Log the quality being validated
        
        if isinstance(v, ChordQualityType):
            return v
            
        if isinstance(v, str):
            if v not in [q.value for q in ChordQualityType]:
                logger.error(f"Invalid quality: '{v}'. Must be one of: {[q.value for q in ChordQualityType]}")
                raise ValueError(f"Invalid quality: '{v}'. Must be one of: {[q.value for q in ChordQualityType]}")
            quality = ChordQualityType(v)
            return quality
        
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
    def validate_inversion(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Inversion cannot be negative")
        return v

    def _generate_chord_notes(self, root: Note, quality: ChordQualityType) -> List[Note]:
        logger.debug(f"Generating notes for chord with root: {root}, quality: {quality}")
        # Ensure root is a Note object
        if not isinstance(root, Note):
            if isinstance(root, dict):
                root = Note(**root)  # Convert dictionary to Note object
            elif isinstance(root, str):
                root = Note(note_name=root)
            else:
                logger.error(f"Invalid root note type: {type(root)}")
                root = Note(note_name='C')
        intervals = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            ChordQualityType.MAJOR_7: [0, 4, 7, 11],
            ChordQualityType.MINOR_7: [0, 3, 7, 10],
            ChordQualityType.DIMINISHED_7: [0, 3, 6, 9],
            ChordQualityType.AUGMENTED_7: [0, 4, 8, 11],
            ChordQualityType.SUS2: [0, 2, 7],
            ChordQualityType.SUS4: [0, 5, 7],
        }
        if quality not in intervals:
            logger.error(f"Invalid quality: '{quality}'. Must be one of: {[q.value for q in ChordQualityType]}")
            raise ValueError(f"Invalid quality: '{quality}'. Must be one of: {[q.value for q in ChordQualityType]}")

        notes = [root]
        logger.debug(f"Starting note generation for quality: {quality}")
        for interval in intervals[quality][1:]:
            transposed_note = root.transpose(interval)  # Call transpose on the root note
            logger.debug(f"Transposed note: {transposed_note} for interval: {interval}")
            if quality == ChordQualityType.DIMINISHED:
                transposed_note = root.transpose(interval)
                if transposed_note.note_name == 'D#':
                    transposed_note.note_name = 'Eb'  # Change D# to Eb
                if transposed_note.note_name == 'F#':
                    transposed_note.note_name = 'Gb'  # Change F# to Gb
                notes.append(transposed_note)
            else:
                notes.append(transposed_note)
        logger.debug(f"Generated notes: {notes}")
        return notes

    def _apply_inversion(self, notes: List[Note], inversion: int) -> List[Note]:
        if inversion == 0 or not notes:
            return notes
        
        inversion = min(inversion, len(notes) - 1)
        inverted_notes = notes[inversion:] + [
            Note.from_midi(note.midi_number + 12, duration=note.duration, velocity=note.velocity)
            for note in notes[:inversion]
        ]
        logger.debug(f"Applied inversion: {inverted_notes}")
        return inverted_notes


    def generate_notes(self) -> List[Note]:
        """Generate the notes for this chord based on its root and quality."""
        logger.debug(f"Generating notes for chord with root: {self.root}, quality: {self.quality}")
        notes = self._generate_chord_notes(self.root, self.quality)
        if self.inversion > 0:
            notes = self._apply_inversion(notes, self.inversion)
        logger.debug(f"Generated notes for chord: {notes}")
        return notes

    def get_notes(self) -> List[Note]:
        """Get the notes in this chord."""
        if not self.notes:
            self.notes = self.generate_notes()
        logger.debug(f"Returning notes for chord: {self.notes}")
        return self.notes

    def transpose(self, semitones: int) -> 'Chord':
        new_root = self.root.transpose(semitones)
        new_notes = [note.transpose(semitones) for note in self.notes]
        logger.debug(f"Transposed chord: {new_root}, {new_notes}")
        return Chord(root=new_root, quality=self.quality, notes=new_notes, inversion=self.inversion)

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
    def from_quality(cls, root: Note, quality: ChordQualityType) -> 'Chord':
        if not isinstance(root, Note) or not hasattr(root, 'note_name'):
            raise ValueError("Root must be a valid Note instance with a note_name")
        logger.debug(f"Creating chord from quality: {root}, {quality}")
        return cls(root=root, quality=quality)