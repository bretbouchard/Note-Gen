from pydantic import BaseModel, ConfigDict, model_validator, field_validator, Field, validator
import logging
from typing import List, Dict, Any, Union, Optional, ClassVar, Type, Tuple, Literal
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
            ChordQuality.DIMINISHED_SEVENTH: [0, 3, 6, 10],
            ChordQuality.AUGMENTED: [0, 4, 8],
            ChordQuality.DOMINANT: [0, 4, 7],
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
    root: Optional[Note] = None  # Can be null for placeholder chords
    quality: Union[Dict[str, Any], ChordQuality] = ChordQuality.MAJOR
    inversion: Optional[int] = Field(None, ge=0, le=3, description="Chord inversion (0-3)")
    duration: Optional[float] = Field(None, gt=0, description="Duration in beats")
    notes: List[Note] = []

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
    def validate_quality(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if 'quality' in data and isinstance(data['quality'], ChordQuality):
            data['quality'] = {
                'name': data['quality'].name,
                'symbol': data['quality'].value,
                'intervals': data['quality'].get_intervals(),
                'description': str(data['quality'])
            }
        return data

    @field_validator('quality')
    @classmethod
    def validate_quality_dict(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        required_keys = ['name', 'symbol', 'intervals']
        if not all(key in v for key in required_keys):
            raise ValueError("Quality dictionary must contain %s", required_keys)
        return v

    def __init__(self, **data: Dict[str, Any]) -> None:
        # Ensure quality is processed correctly
        if 'quality' in data:
            quality = data['quality']
            logger.debug('Processing chord quality parameter: %s (type: %s)', quality, type(quality))
            
            if isinstance(quality, str):
                try:
                    # Try to handle common shortened notation
                    if quality == "MAJOR7":
                        quality = "MAJOR_SEVENTH"
                        logger.debug('Converted MAJOR7 to MAJOR_SEVENTH')
                    elif quality == "MINOR7":
                        quality = "MINOR_SEVENTH"
                        logger.debug('Converted MINOR7 to MINOR_SEVENTH')
                    elif quality == "DOMINANT7":
                        quality = "DOMINANT_SEVENTH"
                        logger.debug('Converted DOMINANT7 to DOMINANT_SEVENTH')
                    
                    data['quality'] = ChordQuality.from_string(quality)  # Convert string to enum
                    logger.debug('Converted string quality %s to %s', quality, data['quality'])
                except ValueError as e:
                    logger.error('Error converting quality string %s: %s', quality, e)
                    # Provide a detailed error message showing available values
                    available_values = [q.name for q in ChordQuality]
                    logger.error('Available ChordQuality values: %s', available_values)
                    raise
            elif isinstance(quality, ChordQuality):
                data['quality'] = quality  # Already a ChordQuality instance
                logger.debug('Using ChordQuality instance %s', quality)
            elif isinstance(quality, type(self).quality_enum):
                # Convert from Chord.Quality to ChordQuality
                try:
                    quality_value = quality.value
                    data['quality'] = ChordQuality(quality_value)
                    logger.debug('Converted Chord.Quality %s to ChordQuality %s', quality, data['quality'])
                except (ValueError, TypeError) as e:
                    logger.error('Error converting Chord.Quality %s: %s', quality, e)
                    raise TypeError('Failed to convert Chord.Quality to ChordQuality: %s', e)
            else:
                logger.error('Invalid quality type: %s, value: %s', type(quality), quality)
                raise TypeError("Quality must be a string, a ChordQuality instance, or a Chord.Quality instance")
        
        # Convert root to Note instance if it's a dictionary
        if isinstance(data['root'], dict):
            try:
                data['root'] = Note(**data['root'])
            except (TypeError, ValueError) as e:
                raise ValueError('Invalid root note: %s', e)
        elif not isinstance(data['root'], Note):
            raise TypeError("root must be a Note instance or a valid note name")

        # Validate notes
        if 'notes' in data and data['notes'] is not None:
            notes = []
            for note in data['notes']:
                if isinstance(note, dict):
                    try:
                        notes.append(Note(**note))
                    except (TypeError, ValueError) as e:
                        raise ValueError('Invalid note in notes list: %s', e)
                elif isinstance(note, Note):
                    notes.append(note)
                else:
                    raise TypeError("notes must be a list of Note instances or dictionaries")
            data['notes'] = notes
        
        # Convert inversion value but let Pydantic handle the validation
        if 'inversion' in data and data['inversion'] is not None:
            try:
                data['inversion'] = int(data['inversion'])
            except (TypeError, ValueError):
                raise ValueError("Inversion must be a valid integer")
        
        # Validate duration
        if 'duration' in data and data['duration'] is not None:
            try:
                duration = float(data['duration'])
                if duration <= 0:
                    raise ValueError("Duration must be a positive number")
                data['duration'] = duration
            except ValueError:
                raise ValueError("Duration must be a valid number")
        
        # Call Pydantic's initializer with the processed data
        super().__init__(**data)  
        logger.debug('Initialized Chord with root: %s, quality: %s', self.root.note_name, self.quality)
        self.notes = self.generate_notes()  # Generate notes upon initialization

    def generate_notes(self) -> List[Note]:
        logger.debug('Generating notes for chord with root: %s and quality: %s', self.root.note_name, self.quality)
        notes = []

        if self.quality == ChordQuality.MAJOR:
            notes = [self.root, self.root.transpose(4), self.root.transpose(7)]
        elif self.quality == ChordQuality.MINOR:
            notes = [self.root, self.root.transpose(3), self.root.transpose(7)]
        elif self.quality == ChordQuality.MAJOR_SEVENTH:
            notes = [self.root, self.root.transpose(4), self.root.transpose(7), self.root.transpose(11)]
        elif self.quality == ChordQuality.MINOR_SEVENTH:
            notes = [self.root, self.root.transpose(3), self.root.transpose(7), self.root.transpose(10)]
        elif self.quality == ChordQuality.DOMINANT_SEVENTH:
            notes = [self.root, self.root.transpose(4), self.root.transpose(7), self.root.transpose(10)]
            logger.debug('Generated notes for DOMINANT_SEVENTH: %s', [note.note_name for note in notes])
        elif self.quality == ChordQuality.DOMINANT:
            notes = [self.root, self.root.transpose(4), self.root.transpose(7)]
        elif self.quality == ChordQuality.DIMINISHED:
            notes = [self.root, self.root.transpose(3), self.root.transpose(6)]
        elif self.quality == ChordQuality.AUGMENTED:
            notes = [self.root, self.root.transpose(4), self.root.transpose(8)]

        # Handle inversion
        if self.inversion == 1:
            notes = [notes[1]] + notes[2:] + [notes[0]]  # Move the second note (E) to the front
        elif self.inversion == 2:
            notes = [notes[2]] + notes[:2]  # Move the third note (G) to the front

        # Add detailed logging with full note information
        note_details = []
        for i, note in enumerate(notes):
            note_details.append('%s%s (MIDI: %s)' % (note.note_name, note.octave, note.midi_number))
            
        logger.debug('Generated notes: %s', [note.note_name for note in notes])
        logger.debug('Note details: %s', note_details)
        logger.debug('Total notes in chord: %s', len(notes))
        return notes

    def calculate_notes(self) -> List[Note]:
        if not self.root:
            raise ValueError("Root note cannot be None.")
        if self.quality is None:
            raise ValueError("Chord quality cannot be None.")

        logger.debug('Generating notes for chord quality: %s', self.quality)
        logger.debug('Quality type: %s, Value: %s', type(self.quality), self.quality)
        
        try:
            intervals = self.quality.get('intervals', [])
            logger.debug('Retrieved intervals for %s: %s', self.quality, intervals)
            
            notes = []
            for interval in intervals:
                transposed_note = self.root.transpose(interval)
                logger.debug('Transposing root %s by interval %s -> %s', self.root.note_name, interval, transposed_note.note_name)
                notes.append(transposed_note)
            
            note_names = [note.note_name for note in notes]
            logger.debug('Generated notes for chord %s of quality %s: %s', self.root.note_name, self.quality, note_names)
            
            if self.inversion is not None and 0 <= self.inversion < len(notes):
                notes = notes[self.inversion:] + notes[:self.inversion]
                logger.debug('Applied inversion %s, resulting notes: %s', self.inversion, [note.note_name for note in notes])
                
            return notes
            
        except Exception as e:
            logger.error('Error generating notes for chord %s with quality %s: %s', self.root.note_name, self.quality, e)
            raise

    @classmethod
    def from_quality(cls, root: Note, quality: ChordQuality, inversion: Optional[int] = None, duration: Optional[float] = None) -> 'Chord':
        if root is None:
            raise ValueError("Root note cannot be None")
        if quality is None:
            raise ValueError("Quality cannot be None")
        return cls(root=root, quality=quality, inversion=inversion, duration=duration)

    def __str__(self) -> str:
        return '%s %s Chord' % (self.root, self.quality)

    def __repr__(self) -> str:
        return 'Chord(root=%s, quality=%s, notes=%s, inversion=%s, duration=%s)' % (self.root, self.quality, self.notes, self.inversion, self.duration)

    def get_notes(self) -> List[Note]:
        if not self.notes:
            self.notes = self.generate_notes()
        return self.notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root.json() if self.root else None,
            "quality": self.quality,
            "notes": [note.json() for note in self.notes] if self.notes else [],
            "inversion": self.inversion,
            "duration": self.duration
        }

    def model_dump(self, *, mode: Literal['json', 'python'] | str = 'json', include: Any | None = ..., exclude: Any | None = ..., context: Any | None = ..., by_alias: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ..., round_trip: bool = ..., warnings: Literal['none', 'warn', 'error'] | bool = ..., serialize_as_any: bool = ...) -> dict[str, Any]:
        """Convert the model to a dictionary representation."""
        return {
            "root": self.root.json() if self.root else None,
            "quality": self.quality,
            "inversion": self.inversion,
            "duration": self.duration,
            "notes": [note.json() for note in self.notes],
        }

    def json(self, *, include: Optional[Dict[str, Any]] = None, exclude: Optional[Dict[str, Any]] = None, by_alias: bool = False, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False, round_trip: bool = False, warnings: Literal['none', 'warn', 'error'] | bool = False, serialize_as_any: bool = False) -> Dict[str, Any]:
        """Override json method to ensure proper serialization of root."""
        data = super().model_dump(include=include, exclude=exclude, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, round_trip=round_trip, warnings=warnings, serialize_as_any=serialize_as_any)
        return data

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
        new_root = self.root.transpose(semitones)
        return Chord(root=new_root, quality=self.quality, inversion=self.inversion, duration=self.duration)

    def __len__(self) -> int:
        if self.notes is None:
            self.notes = self.generate_notes()
        return len(self.notes or [])

    def set_scale_degrees(self, scale_degree: int) -> None:
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
    def __init__(self) -> None:
        self.data = []

    async def insert(self, pattern: Any) -> None:
        self.data.append(pattern)
