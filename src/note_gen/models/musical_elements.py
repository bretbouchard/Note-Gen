# src/note_gen/models/musical_elements.py
from typing import List, Optional, Union, Any, Dict, ClassVar
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum
from src.note_gen.models.note import Note


import traceback
import logging
logger = logging.getLogger(__name__)

__all__ = ['Note', 'ChordQualityType', 'Chord']

CHORD_QUALITY_ALIASES = {
    'maj': 'MAJOR',
    'min': 'MINOR',
    'm': 'MINOR',
    'dim': 'DIMINISHED',
    'aug': 'AUGMENTED',
    '7': 'DOMINANT_7',
    'maj7': 'MAJOR7',
    'min7': 'MINOR_7',
    'm7': 'MINOR_7',
    'dim7': 'DIMINISHED7',
    'm7b5': 'M7B5',
    'sus2': 'SUSPENDED_2',
    'sus4': 'SUSPENDED_4',
    '6': 'MAJOR_6',
    'm6': 'MINOR_6',
    'minmaj7': 'MINOR_MAJOR_7',
    'aug7': 'AUGMENTED_7',
    'ø7': 'HALF_DIMINISHED_7',
    'b5': 'FLAT_5',
    '#5': 'SHARP_5',
    '#7': 'SHARP_7'
}

class ChordQualityType(str, Enum):
    MAJOR = 'MAJOR'
    MINOR = 'MINOR'
    DIMINISHED = 'DIMINISHED'
    AUGMENTED = 'AUGMENTED'
    DOMINANT7 = 'DOMINANT7'
    MAJOR7 = 'MAJOR7'  # Keep this as MAJOR7 without underscore
    MINOR7 = 'MINOR7'
    DIMINISHED7 = 'DIMINISHED7'
    M7B5 = 'M7B5'
    SUSPENDED2 = 'SUSPENDED2'
    SUSPENDED4 = 'SUSPENDED4'
    MAJOR6 = 'MAJOR6'
    MINOR6 = 'MINOR6'
    MINOR_MAJOR7 = 'MINOR_MAJOR7'
    AUGMENTED7 = 'AUGMENTED7'
    HALF_DIMINISHED7 = 'HALF_DIMINISHED7'
    FLAT5 = 'FLAT5'
    SHARP5 = 'SHARP5'
    SHARP7 = 'SHARP7'

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQualityType':
        if not quality_str:
            raise ValueError("Quality string cannot be empty")
        quality_str = quality_str.strip().lower()
        
        # Use the global CHORD_QUALITY_ALIASES dictionary
        if quality_str in CHORD_QUALITY_ALIASES:
            quality_str = CHORD_QUALITY_ALIASES[quality_str]
        
        try:
            return cls[quality_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid quality string: {quality_str}")

    def get_intervals(self) -> List[int]:
        """Get the intervals for a given chord quality."""
        intervals_map = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            ChordQualityType.DOMINANT7: [0, 4, 7, 10],  # Changed from DOMINANT_7
            ChordQualityType.MAJOR7: [0, 4, 7, 11],
            ChordQualityType.MINOR7: [0, 3, 7, 10],  # Changed from MINOR_7
            ChordQualityType.DIMINISHED7: [0, 3, 6, 9],
            ChordQualityType.M7B5: [0, 3, 6, 10],
            ChordQualityType.SUSPENDED2: [0, 2, 7],  # Changed from SUSPENDED_2
            ChordQualityType.SUSPENDED4: [0, 5, 7],  # Changed from SUSPENDED_4
            ChordQualityType.MAJOR6: [0, 4, 7, 9],  # Changed from MAJOR_6
            ChordQualityType.MINOR6: [0, 3, 7, 9],  # Changed from MINOR_6
            ChordQualityType.MINOR_MAJOR7: [0, 3, 7, 11],  # Changed from MINOR_MAJOR_7
            ChordQualityType.AUGMENTED7: [0, 4, 8, 10],  # Changed from AUGMENTED_7
            ChordQualityType.HALF_DIMINISHED7: [0, 3, 6, 10],  # Changed from HALF_DIMINISHED_7
            ChordQualityType.FLAT5: [0, 4, 6],  # Changed from FLAT_5
            ChordQualityType.SHARP5: [0, 4, 8],  # Changed from SHARP_5
            ChordQualityType.SHARP7: [0, 4, 7, 11]  # Changed from SHARP_7
        }
    
        if self not in intervals_map:
            raise ValueError(f"No intervals defined for chord quality: {self}")
        
        return intervals_map[self]


class Chord(BaseModel):
    root: Note
    quality: str = Field(default=ChordQualityType.MAJOR.value)
    inversion: int = Field(default=0)
    notes: List[Note] = []

    class Config:
        arbitrary_types_allowed = True

    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)

    def __init__(self, **data: Any) -> None:
        self.logger.debug(f"Initializing Chord with data: {data}")
        if 'quality' in data:
            self.logger.info(f"Quality before conversion: {data['quality']}")
            data['quality'] = ChordQualityType.from_string(data['quality']).value  # Convert to string
        super().__init__(**data)
        self.logger.info(f"Quality after conversion: {self.quality}")
        self.notes = self._generate_chord_notes(self.root, ChordQualityType.from_string(self.quality))
        self.apply_inversion()  # Apply inversion after generating notes

    def apply_inversion(self) -> None:
        if self.inversion < 0:
            raise ValueError("Inversion cannot be negative.")
        if self.inversion > 0:
            self.notes = self.notes[self.inversion:] + self.notes[:self.inversion]  # Rotate notes for inversion

    @field_validator('quality')
    def validate_quality(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Quality must be a valid string.")
        try:
            ChordQualityType.from_string(value)
        except ValueError:
            raise ValueError("Quality must be a valid ChordQualityType.")
        return value

    def _generate_chord_notes(self, root: Note, quality: ChordQualityType) -> List[Note]:
        """Generate the notes for a chord based on its root and quality."""
        logger.debug(f"Starting note generation for quality: {quality}")
        logger.debug(f"Root note: {root.note_name}, Octave: {root.octave}")
        
        intervals = quality.get_intervals()
        notes = []
        
        for interval in intervals:
            new_note = root.transpose(interval)
            notes.append(new_note)
        
        return notes

    def generate_notes(self) -> List[Note]:
        """Generate the notes for this chord based on its root and quality."""
        self.logger.debug(f"Generating notes for chord with root: {self.root}, quality: {self.quality}")
        notes = self._generate_chord_notes(self.root, ChordQualityType.from_string(self.quality))
        if self.inversion > 0:
            notes = notes[self.inversion:] + notes[:self.inversion]  # Rotate notes for inversion
        self.logger.debug(f"Generated notes for chord: {notes}")
        return notes

    def get_notes(self) -> List[Note]:
        """Get the notes in this chord."""
        if not self.notes:
            self.notes = self.generate_notes()
        self.logger.debug(f"Returning notes for chord: {self.notes}")
        return self.notes

    def transpose(self, semitones: int) -> 'Chord':
        new_root = self.root.transpose(semitones)
        new_notes = [note.transpose(semitones) for note in self.notes]
        self.logger.debug(f"Transposed chord: {new_root}, {new_notes}")
        return Chord(root=new_root, quality=self.quality, notes=new_notes, inversion=self.inversion)

    def to_dict(self):
        return {
            "root": self.root.to_dict(),
            "quality": ChordQualityType.from_string(self.quality).name,  # Ensure proper serialization
            "notes": [note.to_dict() for note in self.notes],
            "inversion": self.inversion
        }

        
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
    def from_quality(cls, root: Note, quality: str) -> 'Chord':  # Accept quality as a string
        cls.logger.debug(f"Creating chord from quality: {quality}")  # Log the quality being passed
        if not isinstance(root, Note) or not hasattr(root, 'note_name'):
            raise ValueError("Root must be a valid Note instance with a note_name")
        cls.logger.debug(f"Quality being passed to from_string: {quality}")  # Log the quality value
        cls.logger.debug(f"Creating chord from quality: {root}, {quality}")
        cls.logger.debug(f"Quality being passed to from_string: {quality}")
        cls.logger.debug(f"Quality being passed to from_string: {quality}")
        quality_enum = ChordQualityType.from_string(quality)  # Convert string to enum
        cls.logger.debug(f"Quality being passed to from_string: {quality}")
        return cls(root=root, quality=quality_enum.value)  # Use the enum value


class ChordProgression(BaseModel):
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)

    def __init__(self, **data):
        self.logger.debug(f"Initializing ChordProgression with data: {data}")
        # ... rest of the code remains the same ...