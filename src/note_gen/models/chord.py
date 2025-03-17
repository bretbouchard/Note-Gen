from typing import Annotated, List, Dict, Any, Union, Optional, ClassVar, Type, Tuple, Literal, Callable
from pydantic import BaseModel, ConfigDict, model_validator, field_validator, Field, validator
import logging
from enum import Enum
import random
import warnings
import json

from src.note_gen.models.note import Note

# Set up logging configuration
logger = logging.getLogger(__name__)

class ChordQuality(Enum):
    AUGMENTED = "AUGMENTED"
    DIMINISHED = "DIMINISHED"
    DIMINISHED_SEVENTH = "DIMINISHED_SEVENTH"
    DOMINANT_SEVENTH = "DOMINANT_SEVENTH"
    DOMINANT = "DOMINANT"
    DOMINANT9 = "DOMINANT9"
    DOMINANT11 = "DOMINANT11"
    FLAT5 = "FLAT5"
    FLAT7 = "FLAT7"
    FULL_DIMINISHED = "FULL_DIMINISHED"
    HALF_DIMINISHED = "HALF_DIMINISHED"
    MAJOR = "MAJOR"
    MAJOR11 = "MAJOR11"
    MAJOR9 = "MAJOR9"
    MAJOR_SEVENTH = "MAJOR_SEVENTH"
    MINOR = "MINOR"
    MINOR9 = "MINOR9"
    MINOR11 = "MINOR11"
    MINOR_SEVENTH = "MINOR_SEVENTH"
    SEVEN_SUS4 = "SEVEN_SUS4"
    SHARP5 = "SHARP5"
    SHARP7 = "SHARP7"
    SUS2 = "SUS2"
    SUS4 = "SUS4"
    SUSPENDED = "SUSPENDED"

    @classmethod
    def from_string(cls, quality_str: str) -> 'ChordQuality':
        """
        Convert a string representation to a ChordQuality enum.
        
        This handles various ways to represent chord qualities including shorthand notations.
        """
        # If we get None or empty string, default to MAJOR
        if not quality_str:
            logger.debug('Empty quality string, defaulting to MAJOR')
            return cls.MAJOR
            
        # First try direct match with the enum value
        try:
            return cls(quality_str.upper())
        except ValueError:
            # If that fails, let's try additional approaches
            pass
            
        # Special handling for single character symbols
        if quality_str == "M":
            return cls.MAJOR
        if quality_str == "m":
            return cls.MINOR
        if quality_str == "+":
            return cls.AUGMENTED
        if quality_str == "°" or quality_str == "o":
            return cls.DIMINISHED
        if quality_str == "7":
            return cls.DOMINANT_SEVENTH
        if quality_str == "ø7" or quality_str == "m7b5":
            return cls.HALF_DIMINISHED
            
        # Special mapping for uppercase values (for test cases)
        uppercase_mapping = {
            'MINOR7': cls.MINOR_SEVENTH,
            'MINOR_SEVENTH': cls.MINOR_SEVENTH,
            'DOMINANT7': cls.DOMINANT_SEVENTH,
            'DOMINANT_SEVENTH': cls.DOMINANT_SEVENTH,
            'MAJOR7': cls.MAJOR_SEVENTH,
            'MAJOR_SEVENTH': cls.MAJOR_SEVENTH,
            'MINOR7': cls.MINOR_SEVENTH,
            'MAJOR7': cls.MAJOR_SEVENTH,
            'DIMINISHED7': cls.FULL_DIMINISHED,
            'HALF_DIMINISHED7': cls.HALF_DIMINISHED,
        }
        
        if quality_str.upper() in uppercase_mapping:
            logger.debug('Matched uppercase quality: %s', quality_str)
            return uppercase_mapping[quality_str.upper()]
            
        # Convert to lowercase for standard mapping
        quality_str_lower = quality_str.lower()
        mapping = {
            'major': cls.MAJOR,
            'maj': cls.MAJOR,
            'maj7': cls.MAJOR_SEVENTH,
            'major7': cls.MAJOR_SEVENTH,
            'major_seventh': cls.MAJOR_SEVENTH,
            'minor': cls.MINOR,
            'min': cls.MINOR,
            'm7': cls.MINOR_SEVENTH,  # Added explicit mapping for 'm7'
            'min7': cls.MINOR_SEVENTH,
            'minor7': cls.MINOR_SEVENTH,
            'minor_seventh': cls.MINOR_SEVENTH,
            'diminished': cls.DIMINISHED,
            'dim': cls.DIMINISHED,
            'dim7': cls.FULL_DIMINISHED,
            'diminished7': cls.FULL_DIMINISHED,
            'full_diminished': cls.FULL_DIMINISHED,
            'aug': cls.AUGMENTED,
            'augmented': cls.AUGMENTED,
            'dominant': cls.DOMINANT,
            'dominant7': cls.DOMINANT_SEVENTH,  # Correct musical representation
            'dom7': cls.DOMINANT_SEVENTH,
            'flat5': cls.FLAT5,
            'flat7': cls.FLAT7,
            'sharp5': cls.SHARP5,
            'sharp7': cls.SHARP7,
            'suspended': cls.SUSPENDED,
            'sus': cls.SUSPENDED,
            'sus2': cls.SUS2,
            'sus4': cls.SUS4,
            'seven_sus4': cls.SEVEN_SUS4,
            'half_diminished7': cls.HALF_DIMINISHED,
        }
        
        if quality_str_lower in mapping:
            logger.debug('Matched lowercase quality: %s to %s', quality_str_lower, mapping[quality_str_lower])
            return mapping[quality_str_lower]
            
        logger.error('Invalid chord quality string: %s', quality_str)
        raise ValueError(f'Invalid chord quality: {quality_str}')

    def get_intervals(self) -> List[int]:
        """Get the intervals for this chord quality."""
        intervals_map = {
            ChordQuality.MAJOR: [0, 4, 7],
            ChordQuality.MINOR: [0, 3, 7],
            ChordQuality.DIMINISHED: [0, 3, 6],
            ChordQuality.DIMINISHED_SEVENTH: [0, 3, 6, 9],
            ChordQuality.AUGMENTED: [0, 4, 8],
            ChordQuality.DOMINANT: [0, 4, 7],
            ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
            ChordQuality.HALF_DIMINISHED: [0, 3, 6, 10],
            ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
            ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
            ChordQuality.FULL_DIMINISHED: [0, 3, 6, 9],
            ChordQuality.MAJOR9: [0, 4, 7, 11, 14],
            ChordQuality.MINOR9: [0, 3, 7, 10, 14],
            ChordQuality.DOMINANT9: [0, 4, 7, 10, 14],
            ChordQuality.MAJOR11: [0, 4, 7, 11, 14, 17],
            ChordQuality.MINOR11: [0, 3, 7, 10, 14, 17],
            ChordQuality.DOMINANT11: [0, 4, 7, 10, 14, 17],
            ChordQuality.SUS2: [0, 2, 7],
            ChordQuality.SUS4: [0, 5, 7],
            ChordQuality.SEVEN_SUS4: [0, 5, 7, 10],
            ChordQuality.FLAT5: [0, 4, 6],
            ChordQuality.FLAT7: [0, 4, 7, 9],
            ChordQuality.SHARP5: [0, 4, 8],
            ChordQuality.SHARP7: [0, 4, 7, 11],
            ChordQuality.SUSPENDED: [0, 5, 7],
        }
        if self not in intervals_map:
            raise ValueError(f"Invalid chord quality: {self}")
        return intervals_map[self]

    def __str__(self) -> str:
        return self.value

class Chord(BaseModel):
    """
    Represents a musical chord with a root note, quality, and optional notes.
    """
    root: Union['Note', str, dict[str, Any]] = Field(..., description="Root note of the chord")
    quality: 'ChordQuality' = Field(..., description="Quality of the chord")
    inversion: int = Field(default=0, ge=0, description="Inversion of the chord")
    duration: Optional[float] = Field(None, gt=0, description="Duration in beats")
    notes: Optional[List['Note']] = Field(None, description="List of notes in the chord")

    # Add class-level quality constants for backward compatibility
    MAJOR: ClassVar[ChordQuality] = ChordQuality.MAJOR
    MINOR: ClassVar[ChordQuality] = ChordQuality.MINOR
    DIMINISHED: ClassVar[ChordQuality] = ChordQuality.DIMINISHED
    AUGMENTED: ClassVar[ChordQuality] = ChordQuality.AUGMENTED
    DOMINANT: ClassVar[ChordQuality] = ChordQuality.DOMINANT
    MINOR_SEVENTH: ClassVar[ChordQuality] = ChordQuality.MINOR_SEVENTH
    MAJOR_SEVENTH: ClassVar[ChordQuality] = ChordQuality.MAJOR_SEVENTH
    DOMINANT_SEVENTH: ClassVar[ChordQuality] = ChordQuality.DOMINANT_SEVENTH
    FULL_DIMINISHED: ClassVar[ChordQuality] = ChordQuality.FULL_DIMINISHED
    HALF_DIMINISHED: ClassVar[ChordQuality] = ChordQuality.HALF_DIMINISHED
    SUSPENDED_SECOND: ClassVar[ChordQuality] = ChordQuality.SUS2
    SUSPENDED_FOURTH: ClassVar[ChordQuality] = ChordQuality.SUS4
    
    # Alias for the quality class for backward compatibility
    quality_enum: ClassVar = ChordQuality

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='forbid',
        json_encoders={
            Note: lambda v: v.json(),
        }
    )

    @model_validator(mode='before')
    @classmethod
    def validate_root(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if 'root' in data and isinstance(data['root'], str):
                data['root'] = Note(note_name=data['root'], octave=4)
        return data

    @field_validator('root')
    @classmethod
    def validate_root_type(cls, value: Union['Note', str, dict[str, Any]]) -> 'Note':
        if isinstance(value, str):
            return Note(note_name=value, octave=4)
        elif isinstance(value, dict):
            return Note(**value)
        return value

    @field_validator('quality')
    @classmethod
    def validate_quality(cls, v: ChordQuality) -> ChordQuality:
        if not isinstance(v, ChordQuality):
            raise ValueError("Invalid chord quality")
        return v

    def _get_note_name(self, note: Note | str | dict[str, Any]) -> str:
        if isinstance(note, str):
            return note
        elif isinstance(note, dict):
            return str(note.get('note_name', ''))
        return note.note_name

    def _transpose_note(self, note: Note | str | dict[str, Any], interval: int) -> Note:
        if isinstance(note, str):
            note = Note.parse_note_name(note)
        elif isinstance(note, dict):
            note = Note(**note)
        if not isinstance(note, Note):
            raise TypeError(f"Expected Note object, got {type(note)}")
        return note.transpose(interval)

    def _get_note_attributes(self, note: Note | str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(note, str):
            return {'note_name': note, 'octave': 0}
        elif isinstance(note, dict):
            return note
        return note.model_dump()

    def __init__(self, root: Union['Note', str, dict[str, Any]], quality: Union[ChordQuality, str], **kwargs: Any) -> None:
        # Convert root if it's a dict
        if isinstance(root, dict):
            root = Note(**root)
        # Convert root if it's a string
        elif isinstance(root, str):
            root = Note(note_name=root, octave=4)
        
        # Convert quality if it's a string
        if isinstance(quality, str):
            quality = ChordQuality.from_string(quality)
        
        super().__init__(root=root, quality=quality, **kwargs)
        logger.debug('Initialized Chord with root: %s, quality: %s', self.root.note_name if isinstance(self.root, Note) else self.root, self.quality)
        self.notes = self.generate_notes()  # Generate notes upon initialization

    def generate_notes(self) -> List[Note]:
        """Generate notes for this chord with proper inversion handling."""
        if self.notes is not None:
            return self.notes

        intervals = self.quality.get_intervals()
        notes = [self._transpose_note(self.root, interval) for interval in intervals]
        
        # Apply inversion if specified
        if self.inversion is not None and 0 < self.inversion < len(notes):
            notes = notes[self.inversion:] + notes[:self.inversion]
        
        return notes

    def calculate_notes(self) -> List[Note]:
        if not self.root:
            raise ValueError("Root note cannot be None.")
        if self.quality is None:
            raise ValueError("Chord quality cannot be None.")

        logger.debug('Generating notes for chord quality: %s', self.quality)
        logger.debug('Quality type: %s, Value: %s', type(self.quality), self.quality)
        
        try:
            intervals = self.quality.get_intervals()
            logger.debug('Retrieved intervals for %s: %s', self.quality, intervals)
            
            notes = []
            for interval in intervals:
                transposed_note = self._transpose_note(self.root, interval)
                logger.debug('Transposing root %s by interval %s -> %s', self.root.note_name if isinstance(self.root, Note) else self.root, interval, transposed_note.note_name)
                notes.append(transposed_note)
            
            note_names = [note.note_name for note in notes]
            logger.debug('Generated notes for chord %s of quality %s: %s', self.root.note_name if isinstance(self.root, Note) else self.root, self.quality, note_names)
            
            if self.inversion is not None and 0 <= self.inversion < len(notes):
                notes = notes[self.inversion:] + notes[:self.inversion]
                logger.debug('Applied inversion %s, resulting notes: %s', self.inversion, [note.note_name for note in notes])
                
            return notes
            
        except Exception as e:
            logger.error('Error generating notes for chord %s with quality %s: %s', self.root.note_name if isinstance(self.root, Note) else self.root, self.quality, e)
            raise

    @classmethod
    def from_quality(cls, root: Note, quality: ChordQuality, inversion: Optional[int] = None, duration: Optional[float] = None) -> 'Chord':
        if root is None:
            raise ValueError("Root note cannot be None")
        if quality is None:
            raise ValueError("Quality cannot be None")
        return cls(root=root, quality=quality, inversion=inversion, duration=duration)

    def __str__(self) -> str:
        return 'Chord(root=%s, quality=%s, notes=%s, inversion=%s, duration=%s)' % (
            self._get_note_name(self.root),
            self.quality,
            [self._get_note_name(note) for note in self.notes] if self.notes else None,
            self.inversion,
            self.duration
        )

    def __repr__(self) -> str:
        return 'Chord(root=%s, quality=%s, notes=%s, inversion=%s, duration=%s)' % (
            self._get_note_name(self.root),
            self.quality,
            [self._get_note_name(note) for note in self.notes] if self.notes else None,
            self.inversion,
            self.duration
        )

    def get_notes(self) -> List[Note]:
        if self.notes is None:
            self.notes = self.generate_notes()
        return self.notes

    def json(
        self,
        *,
        include: Any | None = None,
        exclude: Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Callable[[Any], Any] | None = None,
        models_as_dict: bool = True,
        **dumps_kwargs: Any
    ) -> str:
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            models_as_dict=models_as_dict,
            **dumps_kwargs
        )

    def model_dump(self, *, mode: Literal['json', 'python'] | str = 'json', include: Any | None = None, exclude: Any | None = None, context: Any | None = None, by_alias: bool = False, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False, round_trip: bool = False, warnings: Literal['none', 'warn', 'error'] | bool = True, serialize_as_any: bool = False) -> dict[str, Any]:
        """Convert the model to a dictionary representation."""
        if self.notes is None:
            return {
                "root": self._get_note_attributes(self.root),
                "quality": self.quality,
                "inversion": self.inversion,
                "duration": self.duration,
                "notes": None
            }
        return {
            "root": self._get_note_attributes(self.root),
            "quality": self.quality,
            "inversion": self.inversion,
            "duration": self.duration,
            "notes": [self._get_note_attributes(note) for note in self.notes]
        }

    @classmethod
    def parse_chord_str(cls, chord_str: str) -> 'Chord':
        root_end = 2
        if len(chord_str) > 1 and chord_str[1] in ['b', '#']:
            root_end = 2
        root_str = chord_str[:root_end]
        
        quality = Chord.quality_enum.MAJOR
        
        if len(chord_str) > root_end:
            quality_str = chord_str[root_end:]
            quality = Chord.quality_enum(quality_str)
        
        root = Note.parse_note_name(root_str)
        
        return cls(root=root, quality=quality)

    def transpose(self, semitones: int) -> 'Chord':
        if isinstance(self.root, Note):
            return self.copy(update={'root': self.root.transpose(semitones)})
        elif isinstance(self.root, str):
            return self.copy(update={'root': Note(note_name=self.root, octave=4).transpose(semitones)})
        raise TypeError(f"Cannot transpose root of type {type(self.root)}")

    def __len__(self) -> int:
        if self.notes is None:
            self.notes = self.generate_notes()
        return len(self.notes or [])

    def set_scale_degrees(self, scale_degree: int) -> None:
        if self.notes is not None:
            for note in self.notes:
                note.scale_degree = scale_degree

    @staticmethod
    def _enharmonic_note_name(note_name: str) -> str:
        enharmonic_map = {
            'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 
            'G#': 'Ab', 'A#': 'Bb',
            'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 
            'Ab': 'G#', 'Bb': 'A#'
        }
        return enharmonic_map.get(note_name, note_name)

class MockDatabase:
    data: List[Any] = []

    def __init__(self) -> None:
        self.data = []

    async def insert(self, pattern: Any) -> None:
        self.data.append(pattern)
