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
    "dominant": "dominant7",           # Map to the enum value, not the enum name
    "dom": "dominant7", 
    'maj': 'MAJOR',
    'min': 'MINOR',
    'm': 'MINOR',
    'dim': 'DIMINISHED',
    'aug': 'AUGMENTED',
    '7': 'DOMINANT7',
    'maj7': 'MAJOR7',
    'min7': 'MINOR7',
    'm7': 'MINOR7',
    'dim7': 'DIMINISHED7',
    'm7b5': 'M7B5',
    'sus2': 'SUSPENDED2',
    'sus4': 'SUSPENDED4',
    '6': 'MAJOR7',
    'm6': 'MINOR7',
    'minmaj7': 'MINOR_MAJOR7',
    'aug7': 'AUGMENTED7',
    'ø7': 'HALF_DIMINISHED7',
    'b5': 'FLAT5',
    '#5': 'SHARP5',
    '#7': 'SHARP7'
}

class ChordQualityType(str, Enum):
    MAJOR = 'MAJOR'
    MINOR = 'MINOR'
    DIMINISHED = 'DIMINISHED'
    AUGMENTED = 'AUGMENTED'
    DOMINANT7 = "DOMINANT7"
    MAJOR7 = 'MAJOR7'
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
    INVALID_QUALITY = "INVALID_QUALITY"

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
            if quality_str not in cls._member_map_:
                return cls.INVALID_QUALITY  # Assign INVALID_QUALITY for invalid strings

    def get_intervals(self, quality: 'ChordQualityType') -> List[int]:
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
    
        if self == ChordQualityType.INVALID_QUALITY:
            raise ValueError("No intervals defined for chord quality: INVALID_QUALITY.")
        if quality not in intervals_map:
            raise ValueError(f"No intervals defined for chord quality: {quality}")
        
        return intervals_map[quality]

class Chord(BaseModel):
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)

    root: Note
    quality: ChordQualityType
    notes: List[Note] = Field(default_factory=list)
    inversion: int = 0
    complexity: Optional[float] = None

    def __init__(self, root: Note, quality: ChordQualityType, notes: Optional[List[Note]] = None, inversion: int = 0, complexity: Optional[float] = None):
        if not isinstance(root, Note):
            raise ValueError("Root must be a valid Note instance.")
        if complexity is not None and (complexity < 0 or complexity > 1):
            raise ValueError("Complexity must be between 0 and 1")
        super().__init__(root=root, quality=quality, notes=notes or [], inversion=inversion, complexity=complexity)

    def generate_notes(self) -> List[Note]:
        """Generate notes for the chord based on its root and quality."""
        intervals = self.quality.get_intervals(self.quality) 
        notes = []
        for interval in intervals:
            note = self.root.transpose(interval)  # Assuming transpose method exists in Note class
            notes.append(note)
        return notes

    def apply_inversion(self) -> None:
        if self.inversion < 0:
            raise ValueError("Inversion cannot be negative.")
        if self.inversion >= len(self.notes):
            raise ValueError("Inversion is greater than the number of notes.")
        self.notes = self.notes[self.inversion:] + self.notes[:self.inversion]  

    def _generate_chord_notes(self, root: Note, quality: ChordQualityType) -> List[Note]:
        """Generate the notes for a chord based on its root and quality."""
        self.logger.debug(f"Starting note generation for quality: {quality}")
        self.logger.debug(f"Root note: {root.note_name}, Octave: {root.octave}")
        
        if quality == ChordQualityType.INVALID_QUALITY:
            raise ValueError("Invalid chord quality.")  
        
        intervals = quality.get_intervals(quality)  
        self.logger.debug(f"Intervals for {quality}: {intervals}")  
        notes = []
        
        for interval in intervals:
            self.logger.debug(f"Processing interval: {interval}")  
            new_note = root.transpose(interval)
            notes.append(new_note)
            self.logger.debug(f"Generated note: {new_note.note_name} for interval: {interval}")  # Log each generated note
            self.logger.debug(f"Generated note details: {new_note.note_name}, octave: {new_note.octave}")  # Log additional note details
        
        return notes

    def get_notes(self) -> List[Note]:
        """Get the notes in this chord."""
        if not self.notes:
            self.notes = self.generate_notes()
            self.logger.debug(f"Generated notes: {self.notes}")  # Log the generated notes
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
            "quality": self.quality.name,  
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
    def from_quality(cls, root: Note, quality: Union[str, ChordQualityType]) -> 'Chord':
        if isinstance(quality, str):
            input_quality = quality
            cls.logger.debug(f"Input quality string: {input_quality}")
            quality = {
                'maj7': ChordQualityType.MAJOR7,
                'major7': ChordQualityType.MAJOR7,
                'MAJOR7': ChordQualityType.MAJOR7,
                'MAJ7': ChordQualityType.MAJOR7,
                'min7': ChordQualityType.MINOR7,
                'minor7': ChordQualityType.MINOR7,
                'MINOR7': ChordQualityType.MINOR7,
                'MIN7': ChordQualityType.MINOR7,
                'dim': ChordQualityType.DIMINISHED,
                'diminished': ChordQualityType.DIMINISHED,
                'aug': ChordQualityType.AUGMENTED,
                'maj': ChordQualityType.MAJOR,
                'major': ChordQualityType.MAJOR,
                'MIN': ChordQualityType.MINOR,
                'MINOR': ChordQualityType.MINOR,
                'dom7': ChordQualityType.DOMINANT7,
                'major': ChordQualityType.MAJOR,
                'minor': ChordQualityType.MINOR,
                'INVALID': ChordQualityType.INVALID_QUALITY
            }.get(quality.lower())

            if quality is None:
                cls.logger.debug("Quality is None, defaulting to MAJOR")
            else:
                cls.logger.debug(f"Mapped quality string '{input_quality}' to '{quality}'")
            cls.logger.debug(f"Mapped quality: {quality}")
        cls.logger.debug(f"Input quality string: {input_quality}")
        cls.logger.debug(f"Mapped quality: {quality}")
        if not isinstance(root, Note) or not hasattr(root, 'note_name'):
            raise ValueError("Root must be a valid Note instance with a note_name")
        cls.logger.debug(f"Quality being passed to from_string: {quality}")  
        return cls(root=root, quality=quality)  


class ChordProgression(BaseModel):
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)
