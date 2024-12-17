"""Module for defining musical notes in music theory.

This module provides classes and functions for representing musical notes, including their properties, alterations, and relationships to scales. It allows for the creation and manipulation of notes, enabling various musical applications such as composition and analysis.

Note Class
----------

The `Note` class encapsulates the properties of a musical note, including its name and any alterations (e.g., sharps or flats).

Usage
-----

To create a musical note, instantiate the `Note` class with the desired note name and optional accidental:

```python
note = Note('C', AccidentalType.SHARP)
print(note)
```

This module is designed to be extensible, allowing for the addition of new properties and methods related to musical notes as needed."""

import logging
from typing import ClassVar, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Note(BaseModel):
    """Class representing a musical note.

    This class encapsulates the properties of a musical note, including its name, pitch, and any alterations. It provides methods for manipulating and analyzing notes.

    Attributes:
        name (str): Note name (A-G)
        accidental (str): Accidental (# or b)
        octave (int): Octave number
        duration (float): Note duration
        velocity (int): Note velocity
        midi_number (int): MIDI number
    """
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
        'Ab': 8,
        'A': 9,
        'A#': 10,
        'Bb': 10,
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
        '': 0, '#': 1, 'b': -1, '##': 2, 'bb': -2
    }
    name: str = Field(..., description="Note name (A-G)")
    accidental: str = Field(default="", description="Accidental (# or b)")
    octave: int = Field(default=4, description="Octave number")
    duration: float = Field(default=1.0, description="Note duration")
    velocity: int = Field(default=64, description="Note velocity")
    midi_number: int = Field(default=0, description="MIDI number")

    model_config = ConfigDict(arbitrary_types_allowed=True)

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
    def from_midi(cls, midi_num: int) -> 'Note':
        """Create a Note from a MIDI number. Must be between 0 and 127.

        Args:
            midi_num (int): MIDI number

        Returns:
            Note: Created note object

        Raises:
            ValueError: If the MIDI number is invalid
        """
        if not 0 <= midi_num <= 127:
            logger.error(f"MIDI number must be between 0 and 127, got {midi_num}")
            raise ValueError(f"MIDI number must be between 0 and 127, got {midi_num}. Invalid value found.")
        octave = (midi_num // 12) - 2
        note_num = midi_num % 12

        # Find closest natural note
        for name, base_num in cls.NOTES.items():
            if base_num == note_num:
                return cls(name=name, octave=octave, midi_number=midi_num)
            elif base_num > note_num:
                prev_name = list(cls.NOTES.keys())[list(cls.NOTES.values()).index(base_num) - 1]
                return cls(name=prev_name, accidental="#", octave=octave, midi_number=midi_num)

        # Handle special case for B#
        return cls(name='B', accidental="#", octave=octave, midi_number=midi_num)

    def to_midi(self) -> int:
        """Convert note to MIDI number.

        Returns:
            int: MIDI number
        """
        return self.midi_number

    def transpose(self, interval: int) -> 'Note':
        """Transpose note by given interval.

        Args:
            interval (int): Interval to transpose by

        Returns:
            Note: Transposed note object

        Raises:
            ValueError: If the transposition would result in an invalid MIDI number
        """
        new_midi = self.to_midi() + interval
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
        midi_num = self.to_midi()
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
        return self.to_midi() == other.to_midi()

    def __str__(self) -> str:
        """String representation of note.

        Returns:
            str: String representation of note
        """
        return f"{self.name}{self.accidental}{self.octave}"

    def __eq__(self, other: object) -> bool:
        """Compare notes by MIDI number.

        Args:
            other (object): Other note to compare with

        Returns:
            bool: Whether the notes are equal
        """
        if not isinstance(other, Note):
            return NotImplemented
        return self.to_midi() == other.to_midi()

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of note
        """
        d = super().model_dump(*args, **kwargs)
        return d
