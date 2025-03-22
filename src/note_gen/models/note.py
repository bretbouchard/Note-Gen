"""
Note model implementation for music generation

This module contains the Note class which represents musical notes with
various properties and validation rules.
"""

import re
import logging
import math
from typing import Dict, Optional, Any, ClassVar, Union, Pattern
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
    ValidationError,
    ValidationInfo,
    root_validator,  # Import root_validator
)
from functools import total_ordering


def validate_midi_range(v: Optional[int]) -> Optional[int]:
    """Validate MIDI number is within valid range."""
    if v is not None and not (0 <= v <= 127):
        raise ValueError("MIDI number out of range")
    return v


@total_ordering
class Note(BaseModel):
    """Model representing a musical note"""

    # Add the regex pattern as a properly annotated class variable
    FULL_NOTE_REGEX: ClassVar[Pattern] = re.compile(r"^([A-G][#b]?)([0-8])$")

    # Add note mapping constants
    NOTE_TO_SEMITONE: ClassVar[Dict[str, int]] = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11
    }

    SEMITONE_TO_SHARP: ClassVar[Dict[int, str]] = {
        0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E',
        5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A',
        10: 'A#', 11: 'B'
    }

    SEMITONE_TO_FLAT: ClassVar[Dict[int, str]] = {
        0: 'C', 1: 'Db', 2: 'D', 3: 'Eb', 4: 'E',
        5: 'F', 6: 'Gb', 7: 'G', 8: 'Ab', 9: 'A',
        10: 'Bb', 11: 'B'
    }

    note_name: str = Field(..., pattern="^[A-G][#b]?$")
    octave: int = Field(..., ge=0, le=8)
    duration: float = Field(1.0, gt=0)
    position: float = Field(0.0, ge=0)
    velocity: int = Field(64, ge=0, le=127)
    stored_midi_number: Optional[int] = Field(
        None,
        description="Stored MIDI number",
    )
    scale_degree: Optional[int] = Field(
        None,
        description="Scale degree of the note (1-7)",
    )
    prefer_flats: bool = Field(False, description="Whether to prefer flat notation")

    model_config = ConfigDict(validate_assignment=True)

    @classmethod
    def normalize_note_name(cls, note_name: str) -> str:
        """Normalize note name to standard format."""
        if not note_name:
            raise ValueError("Note name cannot be empty")
        
        # Convert first letter to uppercase, keep the rest as is
        name = note_name[0].upper() + note_name[1:] if len(note_name) > 1 else note_name.upper()
        
        # Basic validation of note letter
        if not name[0] in 'ABCDEFG':
            raise ValueError(f"Invalid note letter: {note_name}")
        
        # Handle accidentals
        if len(name) > 1:
            if name[1] not in '#b':
                raise ValueError(f"Invalid accidental in note name: {note_name}")
            if len(name) > 2:
                raise ValueError(f"Note name too long: {note_name}")
        
        # Validate against known notes
        if name not in cls.NOTE_TO_SEMITONE:
            raise ValueError(f"Invalid note name: {note_name}")
        
        return name

    @field_validator('stored_midi_number')
    @classmethod
    def validate_stored_midi(cls, v: Optional[int]) -> Optional[int]:
        """Validate stored MIDI number range."""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError("MIDI number must be an integer")
            if not (0 <= v <= 127):
                raise ValueError("Input should be less than or equal to 127")
        return v

    @field_validator('note_name')
    @classmethod
    def validate_note_name(cls, v: str) -> str:
        """Validate and normalize note name."""
        if not v:
            raise ValueError("Note name cannot be empty")
        normalized = cls.normalize_note_name(v)
        return normalized

    @model_validator(mode='after')
    def validate_note(self) -> 'Note':
        """Validate the note and calculate MIDI number if needed."""
        # First validate octave 8 notes
        if self.octave == 8:
            base_note = self.note_name[0]
            if base_note > 'G' or (base_note == 'G' and len(self.note_name) > 1):
                raise ValueError("Note exceeds MIDI range")
        
        # Calculate MIDI number before validating stored_midi_number
        calculated_midi = self._calculate_midi_number(self.note_name, self.octave)
        
        # Validate stored_midi_number if present
        if self.stored_midi_number is not None:
            # First check the range
            if not (0 <= self.stored_midi_number <= 127):
                raise ValueError("Input should be less than or equal to 127")
            # Then check if it matches calculated value
            if self.stored_midi_number != calculated_midi:
                raise ValueError(
                    f"Stored MIDI number {self.stored_midi_number} does not match "
                    f"calculated value {calculated_midi}"
                )
        else:
            object.__setattr__(self, 'stored_midi_number', calculated_midi)
        
        return self

    @property
    def full_note_name(self) -> str:
        """Returns the full note name including octave"""
        return f"{self.note_name}{self.octave}"

    @field_validator('note_name', 'octave')
    def validate_note_range(cls, v, info: ValidationInfo) -> Any:
        """Validate that the note is within valid MIDI range."""
        if info.field_name == 'octave' and v == 8:
            note_name = info.data.get('note_name', '')
            if note_name:
                base_note = note_name[0].upper()
                if base_note > 'G' or (base_note == 'G' and len(note_name) > 1):
                    raise ValueError(f"Note {note_name}{v} exceeds MIDI range")
        return v

    @classmethod
    def _calculate_midi_number(cls, note_name: str, octave: int) -> int:
        """Calculate MIDI number from note name and octave."""
        try:
            semitone = cls.NOTE_TO_SEMITONE[note_name]
        except KeyError:
            raise ValueError(f"Invalid note name: {note_name}")
        
        # Calculate MIDI number
        midi_num = ((octave + 1) * 12) + semitone
        
        # Validate MIDI range
        if not 0 <= midi_num <= 127:
            raise ValueError("Note exceeds MIDI range")
        
        # Special handling for octave 8
        if octave == 8:
            base_note = note_name[0]
            if base_note > 'G' or (base_note == 'G' and len(note_name) > 1):
                raise ValueError("Note exceeds MIDI range")
            # G8 should be MIDI 127
            if base_note == 'G' and len(note_name) == 1:
                return 127
        
        return midi_num

    @property
    def midi_number(self) -> int:
        """Get the MIDI number for this note."""
        if self.stored_midi_number is not None:
            return self.stored_midi_number
        
        return self._calculate_midi_number(self.note_name, self.octave)

    def get_midi_number(self) -> int:
        """Alias for midi_number property for backward compatibility."""
        return self.midi_number

    @classmethod
    def from_midi_number(
        cls,
        midi_num: int,
        duration: float = 1.0,
        position: float = 0.0,
        velocity: int = 64,
        scale_degree: Optional[int] = None,
        stored_midi_number: Optional[int] = None,
        prefer_flats: bool = False,
    ) -> "Note":
        """Create a Note from a MIDI number."""
        if not 0 <= midi_num <= 127:
            raise ValueError(f"MIDI number must be between 0 and 127, got {midi_num}")
        
        note_name, octave = cls._midi_to_note_octave(midi_num, prefer_flats)
        
        return cls(
            note_name=note_name,
            octave=octave,
            duration=duration,
            position=position,
            velocity=velocity,
            stored_midi_number=stored_midi_number if stored_midi_number is not None else midi_num,
            scale_degree=scale_degree,
            prefer_flats=prefer_flats
        )

    @classmethod
    def fill_missing_fields(
        cls, data: Union[Dict[str, Any], int, str]
    ) -> Dict[str, Any]:
        """Fill in missing fields from a dictionary, MIDI number, or note name."""
        if not isinstance(data, (dict, int, str)):
            raise ValueError("Input data must be a dictionary, integer, or string")

        if isinstance(data, dict):
            if not data:
                return {
                    "note_name": "C",
                    "octave": 4,
                    "duration": 1,
                    "position": 0.0,
                    "velocity": 64,
                    "stored_midi_number": None,
                    "scale_degree": None,
                    "prefer_flats": False,
                }

            if "note_name" not in data:
                raise ValueError("Missing required field: note_name")

            if data["note_name"] not in cls.NOTE_TO_SEMITONE:
                raise ValueError(f'Unrecognized note name: {data["note_name"]}')

            try:
                return cls(**data).model_dump()
            except ValidationError:
                raise ValueError("Invalid note data")

        if isinstance(data, int):
            if not 0 <= data <= 127:
                raise ValueError(f"Invalid MIDI number: {data}")
            return cls.from_midi_number(data).model_dump()

        if isinstance(data, str):
            try:
                note = cls.from_name(data)
                return note.model_dump()
            except ValueError as e:
                raise ValueError(f"Invalid note name format: {data}") from e

        raise ValueError(
            f"Expected dict, int, or str for Note, got {type(data).__name__}"
        )

    @classmethod
    def note_name_to_midi(cls, note_name: str) -> int:
        """Convert a note name to its MIDI semitone offset.

        Args:
            note_name: Note name (e.g., 'C', 'C#', 'Db')

        Returns:
            int: MIDI semitone offset (0-11)

        Raises:
            ValueError: If the note name is invalid
        """
        try:
            normalized_name = cls.normalize_note_name(note_name)
            return cls.NOTE_TO_SEMITONE[normalized_name]
        except ValueError:
            raise ValueError(f"Unrecognized note name: {note_name}")

    @classmethod
    def _note_octave_to_midi(cls, note_name: str, octave: int) -> int:
        """Convert note name and octave to MIDI number."""
        note_name = cls.normalize_note_name(note_name)
        
        # Special handling for octave 8 - only C through G are valid
        if octave == 8:
            if note_name > 'G':
                raise ValueError(f"Note {note_name}{octave} exceeds MIDI range")
            if note_name == 'G':
                return 127
        
        # Calculate MIDI number
        semitone = cls.NOTE_TO_SEMITONE[note_name]
        midi_num = ((octave + 1) * 12) + semitone
        
        # Validate the range
        if not (0 <= midi_num <= 127):
            raise ValueError(f"Note {note_name}{octave} exceeds MIDI range")
        
        return midi_num

    @classmethod
    def _is_valid_note_name(cls, note_name: str) -> bool:
        """Check if a note name is valid.

        Args:
            note_name: The note name to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return note_name in cls.NOTE_TO_SEMITONE

    @classmethod
    def from_name(
        cls,
        full_name: str,
        velocity: int = 64,
        duration: float = 1.0,
        position: float = 0.0,
    ) -> "Note":
        """Create a Note from a full note name (e.g., 'C4', 'D#5').
        Alias for from_full_name for backward compatibility.

        Args:
            full_name: Full note name with octave (e.g., 'C4', 'D#5')
            velocity: Note velocity (0-127)
            duration: Note duration in beats
            position: Note position in beats

        Returns:
            Note: A new Note object
        """
        return cls.from_full_name(full_name, velocity, duration, position)

    @classmethod
    def from_midi(
        cls,
        midi_number: int,
        duration: float = 1.0,
        position: float = 0.0,
        velocity: int = 64,
        scale_degree: Optional[int] = None,
        stored_midi_number: Optional[int] = None,
        prefer_flats: bool = False,
    ) -> "Note":
        """Create a Note from a MIDI number."""
        if not 0 <= midi_number <= 127:
            raise ValueError(
                f"Invalid MIDI number: {midi_number}. MIDI number must be between 0 and 127."
            )

        # Get note name and octave, this will raise ValueError for invalid notes like A8
        note_name, octave = cls._midi_to_note_octave(midi_number, prefer_flats)

        # Additional validation for octave 8
        if octave == 8:
            base_note = note_name[0].upper()
            if base_note > 'G' or (base_note == 'G' and len(note_name) > 1):
                raise ValueError(f"Note {note_name}{octave} exceeds MIDI range")

        return Note(
            note_name=note_name,
            octave=octave,
            duration=duration,
            position=position,
            velocity=velocity,
            stored_midi_number=(
                midi_number if stored_midi_number is None else stored_midi_number
            ),
            scale_degree=scale_degree,
            prefer_flats=prefer_flats,
        )

    @classmethod
    def from_full_name(
        cls,
        full_name: str,
        velocity: int = 64,
        duration: float = 1.0,
        position: float = 0.0,
        scale_degree: Optional[int] = None,
        stored_midi_number: Optional[int] = None,
        prefer_flats: bool = False
    ) -> "Note":
        """Create a Note from a full note name (e.g., "C4").

        Args:
            full_name: Full note name (e.g., "C4")
            velocity: MIDI velocity (0-127)
            duration: Duration in beats
            position: Position in beats
            scale_degree: Scale degree of the note
            stored_midi_number: The MIDI number of the note
            prefer_flats: Whether to prefer flat notation

        Returns:
            Note: Note object

        Raises:
            ValueError: If the note name is invalid
        """
        if not full_name:
            raise ValueError("Invalid note name format: empty string")

        # Extract note name and octave
        match = cls.FULL_NOTE_REGEX.match(full_name)
        if not match:
            raise ValueError(f"Invalid note name format: {full_name}")

        note_name = match.group(1)
        octave = int(match.group(2))

        # Validate note name
        if not cls._is_valid_note_name(note_name):
            raise ValueError(f"Invalid note name: {note_name}")

        # Calculate MIDI number for storage
        midi_number = cls._note_octave_to_midi(note_name, octave)

        return Note(
            note_name=note_name,
            octave=octave,
            velocity=velocity,
            duration=duration,
            position=position,
            stored_midi_number=(
                midi_number if stored_midi_number is None else stored_midi_number
            ),
            scale_degree=scale_degree,
            prefer_flats=prefer_flats
        )

    @classmethod
    def from_note_name(
        cls,
        note_name: str,
        *,
        duration: float = 1.0,
        position: float = 0.0,
        velocity: int = 64,
        stored_midi_number: Optional[int] = None,
        scale_degree: Optional[int] = None,
        prefer_flats: bool = False
    ) -> "Note":
        """Create a Note from just a note name.

        Args:
            note_name: Note name without octave (e.g., 'C', 'D#')
            duration: Duration in beats
            position: Position in beats
            velocity: MIDI velocity (0-127)
            stored_midi_number: The MIDI number of the note
            scale_degree: Scale degree of the note
            prefer_flats: Whether to prefer flat notation

        Returns:
            Note: A new Note object

        Raises:
            ValueError: If the note name is invalid
        """
        if not cls._is_valid_note_name(note_name):
            raise ValueError(f"Invalid note name: {note_name}")

        return cls(
            note_name=note_name,
            octave=4,  # Default octave
            duration=duration,
            position=position,
            velocity=velocity,
            stored_midi_number=stored_midi_number,
            scale_degree=scale_degree,
            prefer_flats=prefer_flats
        )

    @classmethod
    def parse_note_name(cls, note_name: str) -> "Note":
        """Parse a note name string into a Note object."""
        match = cls.FULL_NOTE_REGEX.match(note_name)
        if not match:
            raise ValueError(f"Invalid note name: {note_name}")
        return Note(note_name=match.group(1), octave=int(match.group(2)))

    @classmethod
    def _midi_to_note_octave(cls, midi_number: int, prefer_flats: bool = False) -> tuple[str, int]:
        """Convert a MIDI number to a note name and octave."""
        if not 0 <= midi_number <= 127:
            raise ValueError(f"MIDI number must be between 0 and 127, got {midi_number}")
        
        octave = (midi_number // 12) - 1
        semitone_value = midi_number % 12
        
        # Choose between sharp and flat notation based on preference
        if prefer_flats:
            note_name = cls.SEMITONE_TO_FLAT[semitone_value]
        else:
            note_name = cls.SEMITONE_TO_SHARP[semitone_value]
        
        return note_name, octave

    @model_validator(mode='after')
    def validate_note_octave(self) -> 'Note':
        """Validate the combination of note name and octave."""
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Validating note-octave combination: note_name='{self.note_name}', octave={self.octave}")
        
        if not 0 <= self.octave <= 8:
            logger.error(f"Invalid octave value: {self.octave}")
            raise ValueError("Octave must be between 0 and 8")
            
        # Check for notes that exceed MIDI range in octave 8
        if self.octave == 8:
            base_note = self.note_name[0].upper()
            logger.debug(f"Octave 8 detected. Base note: '{base_note}', full note: '{self.note_name}'")
            
            if base_note > 'G':
                logger.error(f"Note exceeds MIDI range: base_note '{base_note}' > 'G'")
                raise ValueError(f"Note {self.note_name}{self.octave} exceeds MIDI range")
            elif base_note == 'G' and len(self.note_name) > 1 and self.note_name[1] in ['#', 'b']:
                logger.error(f"Note exceeds MIDI range: G with accidental '{self.note_name}'")
                raise ValueError(f"Note {self.note_name}{self.octave} exceeds MIDI range")
                
        logger.debug("Note-octave combination validation passed")
        return self

    @model_validator(mode='before')
    @classmethod
    def validate_note_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the complete note data before individual field validation."""
        if isinstance(data, dict):
            note_name = data.get('note_name')
            octave = data.get('octave')
            
            if note_name and octave is not None:
                # Normalize note name for consistent validation
                note_name = cls.normalize_note_name(note_name)
                
                # Validate octave range
                if not 0 <= octave <= 8:
                    raise ValueError(f"Octave must be between 0 and 8, got {octave}")
                
                # Special validation for octave 8
                if octave == 8:
                    base_note = note_name[0].upper()
                    if base_note > 'G':
                        raise ValueError(f"Note {note_name}{octave} exceeds MIDI range")
                    elif base_note == 'G' and len(note_name) > 1:
                        raise ValueError(f"Note {note_name}{octave} exceeds MIDI range")
                
                # Calculate MIDI number
                calculated_midi = cls._note_octave_to_midi(note_name, octave)
                
                # Set the stored_midi_number if not provided
                if 'stored_midi_number' not in data or data['stored_midi_number'] is None:
                    data['stored_midi_number'] = calculated_midi
                elif data['stored_midi_number'] != calculated_midi:
                    raise ValueError(f"Stored MIDI number {data['stored_midi_number']} does not match calculated value {calculated_midi}")
                
                # Update the data with normalized values
                data['note_name'] = note_name
        
        return data

    @model_validator(mode='before')
    @classmethod
    def validate_note_octave_combination(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the combination of note name and octave before instance creation."""
        if 'note_name' in data and 'octave' in data:
            note_name = data['note_name']
            octave = data['octave']
            
            # Handle case-insensitive validation
            if isinstance(note_name, str):
                base_note = note_name[0].upper()
                
                # Special validation for octave 8
                if octave == 8:
                    if base_note > 'G' or (base_note == 'G' and len(note_name) > 1 and note_name[1] in '#b'):
                        raise ValueError(f"Note {note_name}{octave} exceeds MIDI range")
                
                # Calculate MIDI number to validate range
                try:
                    midi_num = ((octave + 1) * 12) + cls.NOTE_TO_SEMITONE[cls.normalize_note_name(note_name)]
                    if midi_num > 127:
                        raise ValueError(f"Note {note_name}{octave} exceeds MIDI range")
                except KeyError:
                    pass  # Let the note_name validator handle invalid note names
        
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert Note object to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of Note
        """
        return {
            "note_name": self.note_name,
            "octave": self.octave,
            "duration": self.duration,
            "position": self.position,
            "velocity": self.velocity,
            "stored_midi_number": self.stored_midi_number,
            "scale_degree": self.scale_degree,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        """Create Note object from dictionary.

        Args:
            data: Dictionary containing note data

        Returns:
            Note: Note object created from dictionary
        """
        return cls(**data)

    def __eq__(self, other: object) -> bool:
        """Compare notes for equality based on their MIDI numbers."""
        if not isinstance(other, Note):
            return NotImplemented
        return self.midi_number == other.midi_number

    def __lt__(self, other: object) -> bool:
        """Compare notes based on their MIDI numbers."""
        if not isinstance(other, Note):
            return NotImplemented
        return self.midi_number < other.midi_number

    def __hash__(self) -> int:
        """Hash based on immutable properties."""
        return hash((self.note_name, self.octave, self.duration, self.position, self.velocity))

    def __repr__(self) -> str:
        """String representation of Note object.

        Returns:
            str: String representation of Note
        """
        return (
            f"Note(note_name='{self.note_name}', octave={self.octave}, "
            f"duration={self.duration}, position={self.position}, "
            f"velocity={self.velocity}, stored_midi_number={self.stored_midi_number}, "
            f"scale_degree={self.scale_degree})"
        )

    def __str__(self) -> str:
        """Concise string representation of Note object (e.g., 'C4').

        Returns:
            str: Concise string representation of Note
        """
        return f"{self.note_name}{self.octave}"

    def clone(self) -> 'Note':
        """Create a copy of this note."""
        return Note(
            note_name=self.note_name,
            octave=self.octave,
            duration=self.duration,
            position=self.position,
            velocity=self.velocity,
            scale_degree=self.scale_degree,
            stored_midi_number=self.stored_midi_number,
            prefer_flats=self.prefer_flats
        )
    
    def transpose(self, semitones: int) -> 'Note':
        """Transpose this note by the given number of semitones."""
        # Calculate new MIDI number
        new_midi = self.midi_number + semitones
        
        # Validate new MIDI number
        if not (0 <= new_midi <= 127):
            raise ValueError(f"Transposition by {semitones} exceeds MIDI range")
        
        # Calculate new octave and note name
        new_note_name, new_octave = self._midi_to_note_octave(new_midi, self.prefer_flats)
        
        # Create and return a new note
        return Note(
            note_name=new_note_name,
            octave=new_octave,
            duration=self.duration,
            position=self.position,
            velocity=self.velocity,
            stored_midi_number=new_midi,
            scale_degree=None,  # Reset scale degree as it's no longer valid
            prefer_flats=self.prefer_flats
        )

    def to_midi_number(self) -> int:
        """Convert note to MIDI note number."""
        # Define base values for notes (C = 0, C# = 1, etc.)
        note_values = {
            'C': 0, 'C#': 1, 'Db': 1,
            'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4,
            'F': 5, 'F#': 6, 'Gb': 6,
            'G': 7, 'G#': 8, 'Ab': 8,
            'A': 9, 'A#': 10, 'Bb': 10,
            'B': 11
        }
        
        # Get base value for note name
        base_value = note_values[self.note_name]
        
        # Calculate MIDI note number
        # MIDI note 60 is middle C (C4)
        return base_value + (self.octave * 12) + 12

    def get_enharmonic(self) -> str:
        """Return enharmonic equivalents."""
        enharmonic_map = {
            'C#': 'Db',
            'Db': 'C#',
            'D#': 'Eb',
            'Eb': 'D#',
            'F#': 'Gb',
            'Gb': 'F#',
            'G#': 'Ab',
            'Ab': 'G#',
            'A#': 'Bb',
            'Bb': 'A#'
        }
        return enharmonic_map.get(self.note_name, self.note_name)


class RhythmNote(BaseModel):
    """Represents a rhythm note with its properties."""

    model_config = {
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
        "extra": "ignore",
        "frozen": True,  # Make instances immutable
    }

    position: float = Field(
        0.0, description="Position of the note in time", ge=0, lt=float("inf")
    )
    duration: float = Field(
        1.0, description="Duration of the note in beats", gt=0, lt=float("inf")
    )
    velocity: int = Field(64, description="Velocity of the note (0-127)", ge=0, le=127)
    accent: bool = Field(False, description="Whether the note is accented")
    tuplet_ratio: tuple[int, int] = Field(
        (1, 1), description="Tuplet ratio (e.g., (3,2) for triplets)"
    )
    groove_offset: float = Field(
        0.0, description="Timing offset for groove (-1.0 to 1.0)", ge=-1.0, le=1.0
    )
    groove_velocity: float = Field(
        1.0, description="Velocity multiplier for groove (0.0 to 2.0)", ge=0.0, le=2.0
    )

    @field_validator("tuplet_ratio")
    @classmethod
    def validate_tuplet_ratio(cls, v: tuple[int, int]) -> tuple[int, int]:
        """Validate tuplet ratio."""
        if len(v) != 2:
            raise ValueError("Tuplet ratio must be a tuple of two integers")
        if v[0] <= 0 or v[1] <= 0:
            raise ValueError("Tuplet ratio values must be positive")
        if v == (1, 1):
            return v
        if v[0] <= v[1]:
            raise ValueError("First number in tuplet ratio must be larger than second")
        return v

    @property
    def actual_duration(self) -> float:
        """Calculate actual duration considering tuplets."""
        return self.duration * (self.tuplet_ratio[1] / self.tuplet_ratio[0])

    @property
    def actual_position(self) -> float:
        """Calculate actual position considering tuplet ratio and groove offset."""
        # Apply tuplet ratio to position
        tuplet_adjusted_pos = self.position * (
            self.tuplet_ratio[1] / self.tuplet_ratio[0]
        )
        # Add groove offset
        return tuplet_adjusted_pos + (self.groove_offset * self.duration)

    @property
    def actual_velocity(self) -> int:
        """Calculate actual velocity considering accent and groove."""
        base_velocity = self.velocity * (1.2 if self.accent else 1.0)
        return min(127, max(0, round(base_velocity * self.groove_velocity)))

    # Keep the original methods for backward compatibility
    def get_actual_duration(self) -> float:
        """Deprecated: Use actual_duration property instead."""
        return self.actual_duration

    def get_actual_position(self) -> float:
        """Deprecated: Use actual_position property instead."""
        return self.actual_position

    def get_actual_velocity(self) -> int:
        """Deprecated: Use actual_velocity property instead."""
        return self.actual_velocity

    @model_validator(mode="after")
    def validate_position_and_duration(self) -> "RhythmNote":
        """Validate that position and duration make sense together."""
        if self.position + self.duration <= 0:
            raise ValueError("Position plus duration must be positive")
        return self

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: float) -> float:
        """Validate that position is a non-negative number."""
        if not isinstance(v, (int, float)):
            raise TypeError("Position must be a number")
        if v < 0:
            raise ValueError("Position must be a non-negative number")
        return float(v)

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        """Validate that duration is a positive number."""
        if not isinstance(v, (int, float)):
            raise TypeError("Duration must be a number")
        if v <= 0:
            raise ValueError("Duration must be a positive number")
        return float(v)

    @field_validator("velocity")
    @classmethod
    def validate_velocity(cls, v: int) -> int:
        """Validate that velocity is within MIDI range (0-127)."""
        if not isinstance(v, int):
            raise TypeError("Velocity must be an integer")
        if not 0 <= v <= 127:
            raise ValueError("Velocity must be between 0 and 127")
        return v

    def __eq__(self, other: Any) -> bool:
        """Compare RhythmNote instances."""
        if isinstance(other, dict):
            # Convert self to dict for comparison
            self_dict = self.model_dump()
            return self_dict == other
        elif isinstance(other, RhythmNote):
            return (
                self.position == other.position
                and self.duration == other.duration
                and self.velocity == other.velocity
                and self.accent == other.accent
            )
        return False

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump to handle special serialization logic."""
        result = super().model_dump(**kwargs)
        return result
