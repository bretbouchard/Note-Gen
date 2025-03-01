from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Dict, Any, Union, Type
import logging
import json

from src.note_gen.models.note import Note
from src.note_gen.models.chord_quality import ChordQualityType

# Set up logging configuration
logger = logging.getLogger(__name__)

class Chord(BaseModel):
    """
    Represents a musical chord with a root note, quality, and optional notes.
    """
    root: Note
    quality: ChordQualityType
    notes: Optional[List[Note]] = None
    inversion: Optional[int] = Field(
        default=None, 
        ge=0, 
        le=3,
        validation_alias="inversion"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow custom types like Note
        validate_assignment=True,      # Enable validation on attribute assignment
        extra='forbid',               # Prevent extra fields
        json_encoders={
            Note: lambda v: v.json(),  # Use the json method for Note instances
            ChordQualityType: lambda v: v.value
        }
    )

    @model_validator(mode='before')
    def validate_root_and_quality(cls , values: dict) -> Dict[str, Any]:
        root = values.get('root')
        quality = values.get('quality')

        if not isinstance(root, Note):
            raise ValueError(f"Expected root to be an instance of Note, got {type(root).__name__}")
        if not isinstance(quality, ChordQualityType):
            raise ValueError(f"Invalid chord quality: {quality}")

        return values
    
    duration: float = Field(default=4.0, description="Duration of each chord in beats")

    @model_validator(mode='before')
    @classmethod
    def validate_input_types(cls: 'Type[Chord]', data: Dict[str, Any]) -> Dict[str, Any]:


        """Validate input types before model creation."""
        """
        Validate input types before model creation.
        Ensures all critical fields are of the correct type and not None.
        """
        if isinstance(data, str):
            data = {'root': data}  # Adjust this based on your expected structure
        if data.get('root') is None:
            raise ValueError("'root' must be provided")
        # Check for None values in critical fields
        if data.get('quality') is None:
            raise ValueError("Chord quality cannot be None")
        
        logger.debug(f"Validating chord with root: {data['root']}, type: {type(data['root'])}")
        
        # Convert root to Note instance if it's a dictionary
        if isinstance(data['root'], dict):
            try:
                data['root'] = Note(**data['root'])
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid root note: {e}")
        # Ensure root is a Note instance
        elif not isinstance(data['root'], Note):
            try:
                data['root'] = Note.parse_note_name(data['root'])
            except (TypeError, ValueError) as e:
                raise TypeError("root must be a Note instance or a valid note name")
        
        # Ensure quality is a valid ChordQualityType
        if not isinstance(data['quality'], ChordQualityType):
            try:
                data['quality'] = ChordQualityType(data['quality'])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid chord quality: {data['quality']}")
        
        # Optional notes handling
        if data.get('notes') is not None:
            # Convert notes to Note instances if they're dictionaries
            notes = []
            for note in data['notes']:
                if isinstance(note, dict):
                    try:
                        notes.append(Note(**note))
                    except (TypeError, ValueError) as e:
                        raise ValueError(f"Invalid note in notes list: {e}")
                elif isinstance(note, Note):
                    notes.append(note)
                else:
                    raise TypeError("notes must be a list of Note instances or dictionaries")
            data['notes'] = notes
        else:
            logger.info("No notes provided, will generate during initialization")
        
        # Inversion handling
        if data.get('inversion') is not None:
            try:
                inversion = int(data['inversion'])
                if inversion < 0 or inversion > 3:
                    raise ValueError("Inversion must be between 0 and 3")
                data['inversion'] = inversion
            except ValueError:
                raise ValueError("Inversion must be a valid integer")
        
        # Duration handling
        if data.get('duration') is not None:
            try:
                duration = float(data['duration'])
                if duration <= 0:
                    raise ValueError("Duration must be a positive number")
                data['duration'] = duration
            except ValueError:
                raise ValueError("Duration must be a valid number")
        
        return data

    @field_validator('inversion')
    @classmethod
    def validate_inversion(cls, value: Optional[int]) -> Optional[int]:
        """
        Validate chord inversion with a specific error message.
        Ensures inversion is either None or between 0 and 3.
        """
        if value is not None:
            if value < 0:
                raise ValueError("Inversion cannot be negative")
            if value > 3:
                raise ValueError("Inversion must be between 0 and 3")
        return value

    def _generate_chord_notes(self) -> List[Note]:
        """
        Generate the actual notes for the chord based on root and quality.
        Uses instance attributes instead of a values dictionary.
        """
        if not self.root:
            raise ValueError("Root note cannot be None.")
        if self.quality is None:
            raise ValueError("Chord quality cannot be None.")

        # Log the quality value being used
        logger.debug(f"Generating notes for chord quality: {self.quality}")
        logger.debug(f"Quality value: {self.quality}")
        logger.debug(f"Intervals dictionary keys: {list(ChordQualityType.get_chord_intervals().keys())}")
        logger.debug(f"Current chord quality: {self.quality}")
        logger.debug(f"Intervals dictionary contents: {ChordQualityType.get_chord_intervals()}")

        # Determine intervals based on chord quality
        intervals_dict = ChordQualityType.get_chord_intervals()
        intervals = intervals_dict[self.quality.value] if self.quality.value != 'DOMINANT' else intervals_dict['DOMINANT7']

        # Generate chord notes
        notes = [
            self.root.transpose(interval) 
            for interval in intervals
        ]

        logger.debug(f"Generated notes for chord {self.root.note_name} of quality {self.quality}: {notes}")

        # Apply inversion if specified
        if self.inversion is not None and 0 <= self.inversion < len(notes):
            notes = notes[self.inversion:] + notes[:self.inversion]

        return notes

    @classmethod
    def from_quality(cls, root: Note, quality: ChordQualityType, inversion: Optional[int] = None, duration: Optional[float] = None) -> 'Chord':
        """
        Create a Chord instance with a specified root note and quality.
        Ensures notes are generated during initialization.
        """
        if root is None:
            raise ValueError("Root note cannot be None")
        if quality is None:
            raise ValueError("Chord quality cannot be None")
        
        return cls(root=root, quality=quality, inversion=inversion, duration=duration)

    def __str__(self) -> str:
        """String representation of the chord."""
        return f"{self.root} {self.quality} Chord"

    def __repr__(self) -> str:
        """Detailed string representation of the chord."""
        return f"Chord(root={self.root}, quality={self.quality}, notes={self.notes}, inversion={self.inversion}, duration={self.duration})"

    def get_notes(self) -> List[Note]:
        """
        Safely retrieve chord notes, generating if not already present.
        """
        if not self.notes:
            self.notes = self._generate_chord_notes()
        return self.notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Chord to a dictionary representation."""
        return {
            "root": self.root.json() if self.root else None,
            "quality": self.quality.value if self.quality else None,
            "notes": [note.json() for note in self.notes] if self.notes else [],
            "inversion": self.inversion,
            "duration": self.duration
        }

    def model_dump(self, **kwargs) -> dict:
        """Convert the model to a dictionary."""
        return {
            "root": self.root.json() if self.root else None,
            "quality": self.quality.value if self.quality else None,
            "notes": [note.json() for note in self.notes] if self.notes else [],
            "inversion": self.inversion,
            "duration": self.duration
        }

    def json(self, **kwargs):
        # Override json method to ensure proper serialization of root
        data = super().json(**kwargs)
        return data

    @classmethod
    def parse_chord_str(cls, chord_str: str) -> 'Chord':
        """
        Parse a chord string and create a Chord instance.
        Example: 'C', 'Dm', 'G7'
        """
        # Determine root note (1-2 characters)
        root_end = 2
        if len(chord_str) > 1 and chord_str[1] in ['b', '#']:
            root_end = 2
        root_str = chord_str[:root_end]
        
        quality = ChordQualityType.MAJOR
        
        if len(chord_str) > root_end:
            quality_str = chord_str[root_end:]
            try:
                quality = ChordQualityType.from_string(quality_str)
            except ValueError:
                raise ValueError(f"Invalid quality string: {quality_str}")
        
        root = Note.parse_note_name(root_str)
        
        return cls(root=root, quality=quality)

    def transpose(self, semitones: int) -> 'Chord':
        """Transpose the chord by the given number of semitones."""
        new_root = self.root.transpose(semitones)
        return Chord(root=new_root, quality=self.quality, inversion=self.inversion, duration=self.duration)

    def __len__(self) -> int:
        """
        Return the number of notes in the chord.
        Ensures notes are generated if not already present.
        """
        # If notes are not generated, generate them without triggering __len__ again
        if self.notes is None:
            self.notes = self._generate_chord_notes()
        return len(self.notes or [])

    def set_scale_degrees(self, scale_degree: int):
        """
        Set the scale degree for all notes in the chord.
        
        Args:
            scale_degree (int): The scale degree of the chord
        """
        for note in self.notes:
            note.scale_degree = scale_degree

    @staticmethod
    def _enharmonic_note_name(note_name: str) -> str:
        """Convert certain sharp/flat notes to their preferred enharmonic equivalent."""
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
