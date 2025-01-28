# src/note_gen/models/musical_elements.py
from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum

import logging

# Configure logging to write to a file
logging.basicConfig(filename='logs/debug.log', level=logging.DEBUG, filemode='a')
logger = logging.getLogger(__name__)

from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.note import Note

__all__ = ['Note', 'ChordQualityType', 'Chord']


class ChordQualityType(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    MAJOR_7 = "maj7"
    MINOR_7 = "m7"
    DIMINISHED_7 = "dim7"
    AUGMENTED_7 = "augmented_7"
    SUS2 = "sus2"
    SUS4 = "sus4"
    DOMINANT = "dominant"
    DOMINANT_7 = "dominant_7"
    DOMINANT_9 = "dominant_9"
    DOMINANT_11 = "dominant_11"
    HALF_DIMINISHED_7 = "m7b5"
    MAJOR_9 = "major_9"
    MINOR_9 = "minor_9"
    MAJOR_11 = "major_11"
    MINOR_11 = "minor_11"
    SEVEN_SUS4 = "seven_sus4"
    FLAT_5 = "flat_5"
    FLAT_7 = "flat_7"
    SHARP_5 = "sharp_5"
    SHARP_7 = "sharp_7"

    _ALIASES: Dict[str, str] = {
        "M": "major",
        "maj": "major",
        "m": "minor",
        "min": "minor",
        "dim": "diminished",
        "°": "diminished",
        "aug": "augmented",
        "+": "augmented",
        "7": "dominant_7",
        "ø7": "m7b5",
    }

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQualityType':
        if not quality_str:
            raise ValueError("Quality string cannot be empty")
        quality_str = quality_str.lower()  # Convert to lowercase for consistency
        # Check if the quality_str is in the aliases
        if quality_str in cls._ALIASES:
            quality_str = cls._ALIASES[quality_str]  # Map alias to full name
        try:
            return cls[quality_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid quality string: {quality_str}")

    def get_intervals(self) -> List[int]:
        INTERVALS = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            ChordQualityType.MAJOR_7: [0, 4, 7, 11],
            ChordQualityType.MINOR_7: [0, 3, 7, 10],
            ChordQualityType.DIMINISHED_7: [0, 3, 6, 9],
            ChordQualityType.DOMINANT_7: [0, 4, 7, 10],
            ChordQualityType.HALF_DIMINISHED_7: [0, 3, 6, 10],
        }
        return INTERVALS[self]

    def __str__(self) -> str:
        return self.value


class Chord(BaseModel):
    """Model for a musical chord."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Note = Field(...)
    quality: ChordQualityType = Field(...)
    notes: List[Note] = Field(default_factory=list)
    inversion: int = Field(default=0)

    @field_validator('quality')
    def validate_quality(cls, value: ChordQualityType) -> ChordQualityType:
        if not isinstance(value, ChordQualityType):
            raise ValueError("Invalid chord quality type.")
        return value

    @field_validator('root')
    def validate_root(cls, value: Note) -> Note:
        if not isinstance(value, Note) or value.octave is None or value.note_name is None or value.duration is None or value.velocity is None:
            raise ValueError("Root must be a valid Note instance with a specified octave, note_name, duration, and velocity.")
        return value

    def __init__(self, **data):
        logger.debug(f"Initializing Chord with data: {data}")
        super().__init__(**data)
        if isinstance(data.get('root'), dict):
            data['root'] = Note(**data['root'])  # Convert dictionary to Note instance
        if isinstance(data.get('quality'), str):
            if data['quality'] not in [q.value for q in ChordQualityType]:
                logger.error(f"Invalid quality: '{data['quality']}'. Must be one of: {[q.value for q in ChordQualityType]}")
                raise ValueError(f"Invalid quality: '{data['quality']}'. Must be one of: {[q.value for q in ChordQualityType]}")
            data['quality'] = ChordQualityType(data['quality'])
        if data.get('notes') is None:
            data['notes'] = []  # Initialize to an empty list if not provided
        # Generate notes based on root and quality
        self.notes = self._generate_chord_notes(data['root'], data['quality'])
        if data.get('inversion', 0) > 0:
            self.notes = self._apply_inversion(self.notes, data['inversion'])

    @field_validator('inversion')
    def validate_inversion(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Inversion cannot be negative")
        return v

    def _generate_chord_notes(self, root: Note, quality: ChordQualityType) -> List[Note]:
        logger.debug(f"Starting note generation for quality: {quality}")
        intervals = quality.get_intervals()
        logger.debug(f"Intervals defined: {intervals}")

        notes = [root]
        logger.debug(f"Starting note generation for quality: {quality}")
        for interval in intervals[1:]:
            transposed_note = root.transpose(interval)  # Call transpose on the root note
            logger.debug(f"Transposed note: {transposed_note} for interval: {interval}")
            if quality == ChordQualityType.DIMINISHED:
                if transposed_note.note_name == 'D#':
                    transposed_note.note_name = 'Eb'
                elif transposed_note.note_name == 'F#':
                    transposed_note.note_name = 'Gb'
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

    def to_dict(self) -> str:
        """Return a string representation of the chord name."""
        return f'{self.root.note_name} {self.quality.value}'

        
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