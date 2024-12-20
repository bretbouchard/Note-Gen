from __future__ import annotations
import logging
from typing import ClassVar, Dict, Any, TYPE_CHECKING
from pydantic import Field, field_validator, ConfigDict, BaseModel
from src.models.base_types import MusicalBase
from src.models.enums import AccidentalType


if TYPE_CHECKING:
    from src.models.chord import Chord
    from src.models.scale import Scale
    from src.models.scale_degree import ScaleDegree
    from src.models.note_event import NoteEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Note(MusicalBase, BaseModel):

    NOTES: ClassVar[Dict[str, int]] = {
        'C': 0,
        'C#': 1,
        'Db': 1,
        'D': 2,
        'D#': 3,
        'Eb': 3,
        'E': 4,
        'F': 5,
        'F#': 6,
        'Gb': 6,
        'G': 7,
        'G#': 8,
        'A': 9,
        'A#': 10,
        'B': 11,
        'Cb': -1,
        'B#': 12,
        'Dbb': 1,
        'Ebb': 2,
        'Fb': 4,
        'Gbb': 5,
        'Abb': 8,
        'Bbb': 10,
        'C4': 0,
        'C#4': 1,
        'Db4': 1,
        'D4': 2,
        'D#4': 3,
        'Eb4': 3,
        'E4': 4,
        'F4': 5,
        'F#4': 6,
        'Gb4': 6,
        'G4': 7,
        'G#4': 8,
        'Ab4': 8,
        'A4': 9,
        'A#4': 10,
        'Bb4': 10,
        'B4': 11,
        'Cb4': -1,
        'B#4': 12,
        'Dbb4': 1,
        'Ebb4': 2,
        'Fb4': 4,
        'Gbb4': 5,
        'Abb4': 8,
        'Bbb4': 10
    }
    ACCIDENTALS: ClassVar[Dict[str, int]] = {
        'natural': 0,
        '': 0,
        '#': 1,
        'b': -1,
        '##': 2,
        'bb': -2
    }
    MIDDLE_C_MIDI: ClassVar[int] = 60  # Default MIDI number for Middle C
    name: str = Field(..., description="Note name (A-G)")
    accidental: str = Field(default="", description="Accidental (# or b)")
    octave: int = Field(default=4, description="Octave number")
    duration: float = Field(default=1.0, description="Note duration")
    velocity: int = Field(default=64, description="Note velocity")
    midi_number: int = Field(default=MIDDLE_C_MIDI, description="MIDI number")


    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # Calculate MIDI number based on note properties
        self.midi_number = self.calculate_midi_number()

    def calculate_midi_number(self) -> int:
        """Calculate MIDI number based on note name, accidental, and octave."""
        # Get the base value for the note from NOTES dictionary
        base_value = self.NOTES.get(self.name, 0)
        
        # Add accidental modification
        accidental_value = self.ACCIDENTALS.get(self.accidental, 0)
        
        # Calculate the complete MIDI number
        midi_number = ((self.octave + 1) * 12) + base_value + accidental_value
        
        return midi_number


    @field_validator('name')
    def validate_note_name(cls, value: str) -> str:
        valid_notes = {'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'}
        if value not in valid_notes:
            raise ValueError('Invalid note name')
        return value

    @field_validator('accidental')
    def validate_accidental(cls, value: str) -> str:
        valid_accidentals = {'', '#', 'b'}
        if value not in valid_accidentals:
            raise ValueError('Invalid accidental')
        return value

    @field_validator('octave')
    def validate_octave(cls, value: int) -> int:
        # MIDI standard supports notes from C-1 to G9
        if value < -1 or value > 9:
            raise ValueError('Octave must be between -1 and 9 (MIDI standard range)')
        return value

    @field_validator('duration')
    def validate_duration(cls, value: float) -> float:
        if value <= 0:
            raise ValueError('Duration must be greater than 0')
        return value

    @staticmethod
    def get_note_name(midi_number: int) -> str:
        """Get the note name from a MIDI number without octave."""
        # Map MIDI note numbers (0-11) to note names
        note_names = {
            0: 'C',
            1: 'C#',
            2: 'D',
            3: 'D#',
            4: 'E',
            5: 'F',
            6: 'F#',
            7: 'G',
            8: 'G#',
            9: 'A',
            10: 'A#',
            11: 'B'
        }
        # Get the note name by taking the modulo 12 of the MIDI number
        return note_names.get(midi_number % 12, 'Unknown Note')

    def note_name(self) -> str:
        """Note name without octave (e.g., C)

        Returns:
            str: Note name
        """
        return self.name

    def note_name_octave(self) -> str:
        """Note name with octave (e.g., C4)

        Returns:
            str: Note name with octave
        """
        return f"{self.name}{self.octave}"

    @classmethod
    def from_name(cls, note_name: str) -> 'Note':
        """Create a note from a string name (e.g., 'C#4').

        Args:
            note_name (str): String representation of the note

        Returns:
            Note: Created note object

        Raises:
            ValueError: If the note name is invalid
        """
        logger.debug(f"Attempting to create Note from string: {note_name}")
        try:
            # Extract note components
            name = note_name[0].upper()
            accidental = ""
            octave = 4  # Default octave

            # Extract accidental if present
            pos = 1
            while pos < len(note_name) and note_name[pos] in ['#', 'b']:
                accidental += note_name[pos]
                pos += 1

            # Extract octave if present
            if pos < len(note_name):
                octave = int(note_name[pos:])

            note = cls(name=name, accidental=accidental, octave=octave)
            logger.debug(f"Created Note: {note}")
            return note
        except ValueError as e:
            logger.error(f"Invalid note name: {note_name}")
            raise ValueError(f"Invalid note name: {note_name}") from e

    @classmethod
    def from_str(cls, note_str: str) -> 'Note':
        """Create a Note from a string representation.

        Args:
            note_str (str): String representation of the note

        Returns:
            Note: Created note object

        Raises:
            ValueError: If the note string is invalid
        """
        if not note_str:
            logger.error("Empty note string")
            raise ValueError("Empty note string")

        logger.debug(f"Creating Note from string: {note_str}")
        try:
            # Extract components
            name = note_str[0].upper()
            pos = 1
            accidental = ""
            while pos < len(note_str) and note_str[pos] in ['#', 'b']:
                accidental += note_str[pos]
                pos += 1
        
            # Get octave if present
            octave = 4
            if pos < len(note_str):
                octave = int(note_str[pos:])

            note = cls(name=name, accidental=accidental, octave=octave)
            logger.debug(f"Created Note: {note}")
            return note
        except ValueError as e:
            logger.error(f"Invalid note string: {note_str}")
            raise ValueError(f"Invalid note string: {note_str}") from e

    @classmethod
    def from_midi(cls, midi_number: int) -> 'Note':
        """Create a Note instance from a MIDI number.

        Args:
            midi_number (int): MIDI number

        Returns:
            Note: Created note object
        """
        octave = min(midi_number // 12, 8)  # Calculate octave from MIDI number, capping at 8
        note_name = cls.get_note_name(midi_number % 12)  # Get note name from MIDI number
        return cls(name=note_name, octave=octave, midi_number=midi_number)

    def transpose(self, interval: int) -> 'Note':
        """Transpose note by given interval.

        Args:
            interval (int): Interval to transpose by

        Returns:
            Note: Transposed note object

        Raises:
            ValueError: If the transposition would result in an invalid MIDI number
        """
        new_midi = self.midi_number + interval
        logger.debug(f"Transposing {self.note_name} by {interval} to MIDI {new_midi}")
        if not 0 <= new_midi <= 127:
            logger.error(f"Transposition would result in invalid MIDI number: {new_midi}")
            raise ValueError(f"Transposition would result in invalid MIDI number: {new_midi}")
        return Note.from_midi(new_midi)

    def enharmonic(self) -> 'Note':
        """Get enharmonic equivalent of note.

        Returns:
            Note: Enharmonic equivalent note object
        """
        midi_num = self.midi_number
        current_note = (self.NOTES[self.name] + self.ACCIDENTALS[self.accidental]) % 12

        # Return natural notes as is
        if not self.accidental:
            return self
        # Logic for enharmonic equivalent can be added here
        for name, base_num in self.NOTES.items():
            if (base_num - 1) % 12 == current_note:
                return Note(name=name, accidental='b', octave=self.octave, midi_number=midi_num)
            elif (base_num + 1) % 12 == current_note:
                return Note(name=name, accidental='#', octave=self.octave, midi_number=midi_num)

        # No enharmonic found
        return self

    def is_enharmonic(self, other: 'Note') -> bool:
        """Check if two notes are enharmonically equivalent.

        Args:
            other (Note): Other note to compare with

        Returns:
            bool: Whether the notes are enharmonically equivalent
        """
        return self.midi_number == other.midi_number

    def __str__(self) -> str:
        """String representation of note."""
        accidental_str = 'natural'  # Default to natural
        if self.accidental == 'b':
            accidental_str = 'flat'
        elif self.accidental == '#':
            accidental_str = 'sharp'
        return f'{self.name} {accidental_str} in octave {self.octave}'

    def __eq__(self, other: object) -> bool:
        """Compare notes by MIDI number.

        Args:
            other (object): Other note to compare with

        Returns:
            bool: Whether the notes are equal
        """
        if not isinstance(other, Note):
            return NotImplemented
        return self.midi_number == other.midi_number

    def __add__(self, interval: int) -> 'Note':
        """Add an interval (in semitones) to the current note.
        
        Args:
            interval (int): The interval to add.
        
        Returns:
            Note: A new Note object representing the transposed note.
        """
        # Calculate the new MIDI number
        new_midi_number = self.midi_number + interval
        # Create a new Note from the new MIDI number
        return Note.from_midi(new_midi_number)

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of note
        """
        d = super().model_dump(*args, **kwargs)
        return d

    @staticmethod
    def test_midi_number() -> None:
        """Test the MIDI number calculations."""
        note = Note(name='C', octave=4)
        assert note.midi_number == 60  # Middle C (C4)
        
        note = Note(name='C', accidental='#', octave=4)
        assert note.midi_number == 61  # C# in octave 4