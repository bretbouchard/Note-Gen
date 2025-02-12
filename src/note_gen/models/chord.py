from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import logging

from src.note_gen.models.note import Note
from .chord_quality import ChordQualityType
from src.note_gen.models.enums import ChordQualityType as ChordQualityEnum

# Set up logging configuration
logger = logging.getLogger(__name__)

class Chord(BaseModel):
    """
    Represents a musical chord with a root note, quality, and optional notes.
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow custom types like Note
        validate_assignment=True,      # Enable validation on attribute assignment
        extra='forbid'                 # Prevent extra fields
    )

    root: Note
    quality: ChordQualityEnum
    notes: Optional[List[Note]] = None
    inversion: Optional[int] = Field(
        default=None, 
        ge=0, 
        le=3,
        validation_alias="inversion"
    )

    @model_validator(mode='before')
    @classmethod
    def validate_input_types(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input types before model creation.
        Ensures all critical fields are of the correct type and not None.
        """
        # Check for None values in critical fields
        if data.get('root') is None:
            raise ValueError("Root note cannot be None")
        if data.get('quality') is None:
            raise ValueError("Chord quality cannot be None")
        
        # Ensure root is a Note instance
        if not isinstance(data['root'], Note):
            raise TypeError("root must be a Note instance")
        
        # Ensure quality is a valid ChordQualityEnum
        if not isinstance(data['quality'], ChordQualityEnum):
            try:
                data['quality'] = ChordQualityEnum(data['quality'])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid chord quality: {data['quality']}")
        
        # Optional notes handling
        if data.get('notes') is None:
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

    @model_validator(mode='after')
    def generate_notes(self) -> 'Chord':
        """
        Generate the notes for the chord after validation.
        Ensures notes are generated automatically upon initialization.
        """
        if not self.root:
            raise ValueError("Root note cannot be None.")
        if self.quality is None:
            raise ValueError("Chord quality cannot be None.")

        # Only generate notes if they are not already provided
        if not self.notes:
            logger.info(f"Generating notes for {self.root} {self.quality} chord")
            self.notes = self._generate_chord_notes()

        return self

    def _generate_chord_notes(self) -> List[Note]:
        """
        Generate the actual notes for the chord based on root and quality.
        Uses instance attributes instead of a values dictionary.
        """
        if not self.root:
            raise ValueError("Root note cannot be None.")
        if self.quality is None:
            raise ValueError("Chord quality cannot be None.")

        # Determine intervals based on chord quality
        intervals_dict = ChordQualityType.get_chord_intervals()
        intervals = intervals_dict[self.quality.value]

        # Generate chord notes
        notes = [
            self.root.transpose(interval) 
            for interval in intervals
        ]

        # Apply inversion if specified
        if self.inversion is not None and 0 <= self.inversion < len(notes):
            notes = notes[self.inversion:] + notes[:self.inversion]

        return notes

    @classmethod
    def from_quality(cls, root: Note, quality: ChordQualityEnum, inversion: Optional[int] = None) -> 'Chord':
        """
        Create a Chord instance with a specified root note and quality.
        Ensures notes are generated during initialization.
        """
        if root is None:
            raise ValueError("Root note cannot be None")
        if quality is None:
            raise ValueError("Chord quality cannot be None")
        
        return cls(root=root, quality=quality, inversion=inversion)

    def __str__(self) -> str:
        """String representation of the chord."""
        return f"{self.root} {self.quality} Chord"

    def __repr__(self) -> str:
        """Detailed string representation of the chord."""
        return f"Chord(root={self.root}, quality={self.quality}, notes={self.notes}, inversion={self.inversion})"

    def get_notes(self) -> List[Note]:
        """
        Safely retrieve chord notes, generating if not already present.
        """
        if not self.notes:
            logger.warning("Notes not generated, generating now")
            self.notes = self._generate_chord_notes()
        return self.notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Chord to a dictionary representation."""
        return {
            "root": self.root.to_dict() if self.root else None,
            "quality": self.quality.value if self.quality else None,
            "notes": [note.to_dict() for note in self.notes] if self.notes else [],
            "inversion": self.inversion
        }

    def to_json(self) -> dict:
        """Convert the Chord to a JSON-serializable dictionary."""
        return {
            'root': self.root.to_json() if self.root else None,
            'quality': self.quality.value if self.quality else None,
            'notes': [note.to_json() for note in self.notes] if self.notes else None,
            'inversion': self.inversion
        }

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
        
        quality = ChordQualityEnum.MAJOR
        
        if len(chord_str) > root_end:
            quality_str = chord_str[root_end:]
            try:
                quality = ChordQualityEnum.from_string(quality_str)
            except ValueError:
                raise ValueError(f"Invalid quality string: {quality_str}")
        
        root = Note.parse_note_name(root_str)
        
        return cls(root=root, quality=quality)

    def transpose(self, semitones: int) -> 'Chord':
        """Transpose the chord by the given number of semitones."""
        new_root = self.root.transpose(semitones)
        return Chord(root=new_root, quality=self.quality, inversion=self.inversion)

    def __len__(self) -> int:
        """
        Return the number of notes in the chord.
        Ensures notes are generated if not already present.
        """
        # If notes are not generated, generate them without triggering __len__ again
        if self.notes is None:
            logger.info("Generating notes during len() call")
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
