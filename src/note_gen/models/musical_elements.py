# src/note_gen/models/musical_elements.py
from typing import List, Optional, Dict, Any, ClassVar, Tuple, Union
from pydantic import BaseModel, ConfigDict, field_validator
import logging
import re
from enum import Enum

from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.roman_numeral import RomanNumeral

class Note(BaseModel):
    note_name: str
    octave: int
    duration: float = 1.0
    velocity: int = 100
    stored_midi_number: Optional[int] = None

    NOTE_TO_SEMITONE: ClassVar[Dict[str, int]] = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11
    }

    SEMITONE_TO_NOTE: ClassVar[Dict[int, str]] = {
        0: 'C', 1: 'C#', 2: 'D',
        3: 'D#', 4: 'E', 5: 'F',
        6: 'F#', 7: 'G', 8: 'G#',
        9: 'A', 10: 'A#', 11: 'B'
    }

    def to_midi_number(self) -> int:
        """Convert the note to its MIDI number representation.
        
        Returns:
            int: The MIDI number for this note (0-127)
            
        Raises:
            ValueError: If the resulting MIDI number would be out of range (0-127)
        """
        if self.stored_midi_number is not None:
            return self.stored_midi_number
            
        # Get the semitone value for the note name
        try:
            semitone = self.NOTE_TO_SEMITONE[self.note_name]
        except KeyError:
            raise ValueError(f"Invalid note name: {self.note_name}")
            
        # Calculate MIDI number: (octave + 1) * 12 + semitone
        midi_number = (self.octave + 1) * 12 + semitone
        
        # Validate MIDI number range
        if midi_number < 0 or midi_number > 127:
            raise ValueError(f"Resulting MIDI number {midi_number} is out of valid range (0-127)")
            
        return midi_number

    @classmethod
    def from_midi_number(cls, midi_number: int, duration: float = 1.0, velocity: int = 100) -> 'Note':
        """Create a Note from a MIDI number.
        
        Args:
            midi_number: The MIDI number (0-127)
            duration: Note duration in beats
            velocity: Note velocity (0-127)
            
        Returns:
            Note: A new Note instance
            
        Raises:
            ValueError: If midi_number is out of range
        """
        if not 0 <= midi_number <= 127:
            raise ValueError(f"MIDI number {midi_number} is out of valid range (0-127)")
            
        octave = (midi_number // 12) - 1
        semitone = midi_number % 12
        note_name = cls.SEMITONE_TO_NOTE[semitone]
        
        return cls(
            note_name=note_name,
            octave=octave,
            duration=duration,
            velocity=velocity,
            stored_midi_number=midi_number
        )

class ScaleType(str, Enum):
    MAJOR = 'MAJOR'
    NATURAL_MINOR = 'NATURAL_MINOR'
    HARMONIC_MINOR = 'HARMONIC_MINOR'
    MELODIC_MINOR = 'MELODIC_MINOR'
    PENTATONIC_MAJOR = 'PENTATONIC_MAJOR'
    PENTATONIC_MINOR = 'PENTATONIC_MINOR'
    BLUES = 'BLUES'
    WHOLE_TONE = 'WHOLE_TONE'
    CHROMATIC = 'CHROMATIC'
    DORIAN = 'DORIAN'
    PHRYGIAN = 'PHRYGIAN'
    LYDIAN = 'LYDIAN'
    MIXOLYDIAN = 'MIXOLYDIAN'
    LOCRIAN = 'LOCRIAN'

    def get_intervals(self) -> List[int]:
        """Get the intervals for this scale type."""
        intervals_map = {
            ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11],
            ScaleType.NATURAL_MINOR: [0, 2, 3, 5, 7, 8, 10],
            ScaleType.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
            ScaleType.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11],
            ScaleType.PENTATONIC_MAJOR: [0, 2, 4, 7, 9],
            ScaleType.PENTATONIC_MINOR: [0, 3, 5, 7, 10],
            ScaleType.BLUES: [0, 3, 5, 6, 7, 10],
            ScaleType.WHOLE_TONE: [0, 2, 4, 6, 8, 10],
            ScaleType.CHROMATIC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
            ScaleType.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
            ScaleType.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
            ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
            ScaleType.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
        }
        
        if self not in intervals_map:
            raise ValueError(f"No intervals defined for scale type: {self}")
        
        return intervals_map[self]

    @property
    def degree_count(self) -> int:
        """Get the number of degrees in this scale type."""
        return len(self.get_intervals())

    @property
    def is_diatonic(self) -> bool:
        """Check if this scale type is diatonic (has 7 intervals)."""
        return len(self.get_intervals()) == 7

    def validate_degree(self, degree: int) -> bool:
        """Validate if a scale degree is valid for this scale type."""
        return 1 <= degree <= len(self.get_intervals())

    def get_scale_degrees(self) -> List[int]:
        """Get all valid scale degrees for this scale type."""
        return list(range(1, len(self.get_intervals()) + 1))


class Scale(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    root: Note
    scale_type: ScaleType
    notes: List[Note] = []

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook to generate notes if not provided."""
        if not self.notes:
            self.notes = self._generate_scale_notes()

    def _generate_scale_notes(self) -> List[Note]:
        """Generate the notes for this scale based on root note and scale type."""
        intervals = self.scale_type.get_intervals()
        scale_notes = []
        base_midi = self.root.to_midi_number()
        
        for interval in intervals:
            new_midi = base_midi + interval
            if new_midi < 0 or new_midi > 127:
                raise ValueError(f"Generated note would be out of MIDI range: {new_midi}")
                
            new_note = Note.from_midi_number(
                midi_number=new_midi,
                duration=self.root.duration,
                velocity=self.root.velocity
            )
            scale_notes.append(new_note)
            
        # Add the octave note
        octave_midi = base_midi + 12
        if octave_midi <= 127:
            octave_note = Note.from_midi_number(
                midi_number=octave_midi,
                duration=self.root.duration,
                velocity=self.root.velocity
            )
            scale_notes.append(octave_note)
            
        return scale_notes

    def get_scale_degree(self, degree: int) -> Note:
        """Get the note at a specific scale degree."""
        if not self.validate_degree(degree):
            raise ValueError(f"Scale degree must be between 1 and {len(self.notes)}")
            
        return self.notes[degree - 1]

    def validate_degree(self, degree: int) -> bool:
        """Validate if a scale degree is valid for this scale."""
        return 1 <= degree <= len(self.notes)

    @property
    def degree_count(self) -> int:
        """Get the number of degrees in this scale."""
        return len(self.notes)

    @property
    def is_diatonic(self) -> bool:
        """Check if this scale is diatonic (has 7 notes)."""
        return len(self.scale_type.get_intervals()) == 7

    def get_scale_degrees(self) -> List[int]:
        """Get all valid scale degrees for this scale."""
        return list(range(1, len(self.notes) + 1))

    def __str__(self) -> str:
        note_names = [note.note_name for note in self.notes]
        return f"{self.root.note_name} {self.scale_type.value} Scale: {', '.join(note_names)}"

class ChordProgression(BaseModel):
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)

class ChordQualityType(str, Enum):
    MAJOR = 'MAJOR'
    MINOR = 'MINOR'
    DIMINISHED = 'DIMINISHED'
    AUGMENTED = 'AUGMENTED'
    DOMINANT = 'DOMINANT'
    DOMINANT7 = 'DOMINANT7'
    MAJOR7 = 'MAJOR7'
    MINOR7 = 'MINOR7'
    DIMINISHED7 = 'DIMINISHED7'
    HALF_DIMINISHED7 = 'HALF_DIMINISHED7'
    MAJOR9 = 'MAJOR9'
    MINOR9 = 'MINOR9'
    DOMINANT9 = 'DOMINANT9'
    AUGMENTED7 = 'AUGMENTED7'
    MAJOR11 = 'MAJOR11'
    MINOR11 = 'MINOR11'
    DOMINANT11 = 'DOMINANT11'
    SUS2 = 'SUS2'
    SUS4 = 'SUS4'
    SEVEN_SUS4 = 'SEVEN_SUS4'
    FLAT5 = 'FLAT5'
    FLAT7 = 'FLAT7'
    SHARP5 = 'SHARP5'
    SHARP7 = 'SHARP7'
    INVALID = 'INVALID'
    INVALID_QUALITY = 'INVALID_QUALITY'

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQualityType':
        """Convert a string to a ChordQualityType."""
        logger.debug(f"Processing quality string: {quality_str}")
        
        # Handle case-sensitive aliases first
        quality_map = {
            # Case-sensitive aliases
            'm': cls.MINOR,
            'M': cls.MAJOR,
            'dim': cls.DIMINISHED,
            'aug': cls.AUGMENTED,
            '7': cls.DOMINANT7,
            'ø7': cls.HALF_DIMINISHED7,
            '°': cls.DIMINISHED,
            '+': cls.AUGMENTED,
            # Uppercase aliases
            'MAJ': cls.MAJOR,
            'MAJOR': cls.MAJOR,
            'MIN': cls.MINOR,
            'MINOR': cls.MINOR,
            'DIM': cls.DIMINISHED,
            'AUG': cls.AUGMENTED,
            'DOM': cls.DOMINANT,
            'DOM7': cls.DOMINANT7,
            'MAJ7': cls.MAJOR7,
            'MIN7': cls.MINOR7,
            'DIM7': cls.DIMINISHED7,
            'SUS2': cls.SUS2,
            'SUS4': cls.SUS4,
            '7SUS4': cls.SEVEN_SUS4,
            # Mixed case aliases
            'maj': cls.MAJOR,
            'min': cls.MINOR,
            'maj7': cls.MAJOR7,
            'min7': cls.MINOR7,
            'm7': cls.MINOR7,
            'dim7': cls.DIMINISHED7,
            'aug7': cls.AUGMENTED7,
            'sus2': cls.SUS2,
            'sus4': cls.SUS4,
            '7sus4': cls.SEVEN_SUS4,
            'b5': cls.FLAT5,
            '#5': cls.SHARP5,
            'b7': cls.FLAT7,
            '#7': cls.SHARP7,
        }

        # Try direct mapping first
        if quality_str in quality_map:
            return quality_map[quality_str]
            
        # Try as enum value
        try:
            return cls(quality_str)
        except ValueError:
            # Try uppercase version
            upper_str = quality_str.upper()
            if upper_str in quality_map:
                return quality_map[upper_str]
            elif upper_str in cls.__members__:
                return cls[upper_str]
            
            raise ValueError(f"Invalid chord quality string: {quality_str}")

    def get_intervals(self) -> List[int]:
        """Get the intervals for this chord quality."""
        intervals_map = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            ChordQualityType.DOMINANT7: [0, 4, 7, 10],
            ChordQualityType.MAJOR7: [0, 4, 7, 11],
            ChordQualityType.MINOR7: [0, 3, 7, 10],
            ChordQualityType.DIMINISHED7: [0, 3, 6, 9],
            ChordQualityType.HALF_DIMINISHED7: [0, 3, 6, 10],
            ChordQualityType.MAJOR9: [0, 4, 7, 11, 14],
            ChordQualityType.MINOR9: [0, 3, 7, 10, 14],
            ChordQualityType.DOMINANT9: [0, 4, 7, 10, 14],
            ChordQualityType.AUGMENTED7: [0, 4, 8, 10],
            ChordQualityType.MAJOR11: [0, 4, 7, 11, 14, 17],
            ChordQualityType.MINOR11: [0, 3, 7, 10, 14, 17],
            ChordQualityType.DOMINANT11: [0, 4, 7, 10, 14, 17],
            ChordQualityType.SUS2: [0, 2, 7],
            ChordQualityType.SUS4: [0, 5, 7],
            ChordQualityType.SEVEN_SUS4: [0, 5, 7, 10],
            ChordQualityType.FLAT5: [0, 4, 6],
            ChordQualityType.FLAT7: [0, 4, 7, 10],
            ChordQualityType.SHARP5: [0, 4, 8],
            ChordQualityType.SHARP7: [0, 4, 7, 11],
        }
        
        if self == ChordQualityType.INVALID_QUALITY or self == ChordQualityType.INVALID:
            raise ValueError(f"No intervals defined for chord quality: {self}")
        if self not in intervals_map:
            raise ValueError(f"No intervals defined for chord quality: {self}")
        
        return intervals_map[self]

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
    '#7': 'SHARP7',
}
