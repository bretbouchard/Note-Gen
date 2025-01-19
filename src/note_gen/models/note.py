# src/note_gen/models/note.py
import re
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError
from typing import Any, ClassVar, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Note(BaseModel):
    """A musical note with optional MIDI number auto-population."""

    note_name: str
    octave: int
    duration: float = 1.0  # Default duration
    velocity: int = 64  # Default velocity
    stored_midi_number: Optional[int] = None  # Add stored_midi_number attribute

    # Maps note names to their semitone values
    NOTE_TO_SEMITONE: ClassVar[Dict[str, int]] = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11
    }

    # Maps semitone values to their note names (using sharps)
    SEMITONE_TO_NOTE: ClassVar[Dict[int, str]] = {
        0: 'C', 1: 'C#', 2: 'D',
        3: 'D#', 4: 'E', 5: 'F',
        6: 'F#', 7: 'G', 8: 'G#',
        9: 'A', 10: 'A#', 11: 'B'
    }


    @field_validator('octave')
    def validate_octave(cls, v: int) -> int:
        if not isinstance(v, int) or v < 0 or v > 9:
            raise ValueError(f'Invalid octave: {v}. Octave must be between 0 and 9.')
        return v

    @field_validator('note_name')
    def validate_note_name(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Invalid type for note_name")
        match = re.match(r"^[A-Ga-g][#b]?\d{0,1}$", v)
        if not match:
            raise ValueError(f"Invalid note name: {v}.")
        return v

    @field_validator('duration')
    def validate_duration(cls, v: float) -> float:
        if not isinstance(v, (int, float)) or v <= 0:  # Ensure duration is a number and greater than 0
            raise ValueError('Input should be greater than 0. Duration should be a positive number.')
        return v
    
    @field_validator('velocity')
    def validate_velocity(cls, v: int) -> int:
        if not isinstance(v, int):
            raise ValueError("Invalid type for velocity")
        if not (0 <= v <= 127):
            raise ValueError("Invalid velocity. Velocity should be an integer between 0 and 127.")
        return v


    @model_validator(mode='before')
    def validate_and_fill(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if 'note_name' not in values:
            raise ValueError("Missing field: note_name")
        if 'octave' not in values:
            raise ValueError("Missing field: octave")
        if 'duration' not in values:
            values['duration'] = 1.0  # Default duration
        if 'velocity' not in values:
            values['velocity'] = 64  # Default velocity
        return values

    @classmethod
    def calculate_midi_number(cls, note_name: str, octave: int) -> int:
        """Calculate the MIDI number based on the note name and octave."""
        note_to_semitone = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        semitone = note_to_semitone.get(note_name)
        if semitone is None:
            raise ValueError(f"Invalid note name: {note_name}")
        return (octave + 1) * 12 + semitone  # MIDI numbers start from C-1 (MIDI 0)

    @staticmethod
    def normalize_note_name(name: str) -> str:
        """Normalize the note name to uppercase and valid accidentals."""
        match = re.match(r"^[A-Ga-g][#b]?\d{0,1}$", name)
        if not match:
            raise ValueError(f"Invalid note name: {name}")  # Changed error message
        # Keep the accidental in the same case
        base_note = name[0].upper()
        if len(name) > 1 and name[1] in ['#', 'b']:
            return base_note + name[1]
        return base_note

    @classmethod
    def from_full_name(cls, full_name: str, duration: float = 1.0, velocity: int = 64) -> 'Note':
        """Create a Note from a full note name (e.g. 'C#4')."""
        match = re.match(r"^([A-Ga-g][#b]?)(\d+)$", full_name)
        if not match:
            raise ValueError("Invalid note name format")
        note_name, octave = match.groups()
        return cls(note_name=cls.normalize_note_name(note_name), octave=int(octave), duration=duration, velocity=velocity)

    @classmethod
    def from_midi(cls, midi_number: int, velocity: int = 64, duration: float = 1.0) -> "Note":
        """Create a Note from a MIDI number (0–127)."""
        if not (0 <= midi_number <= 127):
            raise ValueError(f"MIDI number out of range: {midi_number}")
        note_name, octave = cls._midi_to_note_octave(midi_number)
        return cls(
            note_name=note_name,
            octave=octave,
            duration=duration,
            velocity=velocity,
        )

    @classmethod
    def from_name(cls, note_name: str, duration: float = 1.0, velocity: int = 64) -> 'Note':
        if not isinstance(note_name, str) or not note_name:
            raise ValueError("Invalid note name: Must be a non-empty string")
        if not re.match(r'^[A-G][#b]?\d?$', note_name):
            raise ValueError(f"Invalid note name format: {note_name}")
        match = re.match(r'([A-G][#b]?)(\d?)', note_name)
        if not match:
            raise ValueError(f"Invalid note name format: {note_name}")
        note_name, octave = match.groups()
        octave = int(octave) if octave else 4
        if octave < 0 or octave > 8:
            raise ValueError(f"Invalid octave: {octave}")
        midi_number = cls.calculate_midi_number(note_name, octave)
        if midi_number < 0 or midi_number > 127:
            raise ValueError("MIDI number out of range")
        return cls(note_name=cls.normalize_note_name(note_name), octave=octave, duration=duration, velocity=velocity)

    @classmethod
    def from_midi_number(cls, midi_number: int, duration: float, velocity: int) -> 'Note':
        """Create a Note from a MIDI number."""
        if not (0 <= midi_number <= 127):
            raise ValueError("MIDI number out of range")
        # Logic to convert MIDI number to note name and octave
        note_name, octave = cls._midi_to_note_octave(midi_number)
        return cls(note_name=note_name, octave=octave, duration=duration, velocity=velocity)

    @classmethod
    def fill_missing_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill missing fields in note data with defaults."""
        logging.debug(f"Input data for fill_missing_fields: {data}")
        
        if data is None:
            raise ValueError("Expected a dict, int, or str for Note")
        
        # Handle MIDI number input
        if isinstance(data, int):
            if not (0 <= data <= 127):
                raise ValueError("MIDI number out of range")
            note_name, octave = cls._midi_to_note_octave(data)
            data = {
                "note_name": note_name, 
                "octave": octave,
                "stored_midi_number": data  # Store original MIDI number
            }
        
        if isinstance(data, str):
            raise ValueError("Invalid note name format")
                        
        if not isinstance(data, dict):
            raise ValueError("Expected a dict, int, or str for Note")
        
        # Create a copy to modify
        result = data.copy()
        
        # Add defaults
        if 'duration' not in result:
            result['duration'] = 1.0
        if 'velocity' not in result:
            result['velocity'] = 64
        if 'stored_midi_number' not in result:
            result['stored_midi_number'] = None
        
        # Validate required fields
        if 'note_name' not in result:
            result['note_name'] = 'C'  # Default note name
                        
        if 'octave' not in result:
            result['octave'] = 4  # Default octave
                        
        # Validate values - note_name first
        if result['note_name'] not in cls.NOTE_TO_SEMITONE:
            raise ValueError("Unrecognized note name")
                            
        # Then validate octave
        logging.debug(f"Validating octave value: {result['octave']}")
        if result['octave'] < 0 or result['octave'] > 8:  # Octaves 0-8 are valid
            logging.debug(f"Invalid octave detected: {result['octave']}")
            raise ValueError(f"Invalid octave: {result['octave']}")
        logging.debug(f"Octave validation passed: {result['octave']}")
                        
        return result

    @staticmethod
    def note_name_to_midi(note_name: str) -> int:
        """Convert a note name to its MIDI offset."""
        note_to_number = {
            "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
            "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
        }
        if note_name not in note_to_number:
            raise ValueError("Unrecognized note name")
        return note_to_number[note_name]

    @property
    def midi_number(self) -> int:
        """Get the MIDI number for this note."""
        return self._note_octave_to_midi(self.note_name, self.octave)

    @classmethod
    def _midi_to_note_octave(cls, midi_number: int) -> Tuple[str, int]:
        """Convert a MIDI number to a note name and octave."""
        if not (0 <= midi_number <= 127):
            raise ValueError("MIDI number out of range")
        semitone_to_note = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_number // 12) - 1
        note_index = midi_number % 12
        # Handle edge cases for octave 0
        if octave < 0:
            octave = 0
        # For MIDI number 127, we should allow octave 10
        if octave > 10:
            raise ValueError("MIDI number out of range")
        return semitone_to_note[note_index], octave

    @staticmethod
    def _note_octave_to_midi(note_name: str, octave: int) -> int:
        """Convert a note name and octave to a MIDI number."""
        if not (0 <= octave <= 10):
            raise ValueError("Octave must be between 0 and 10")
        note_to_semitone = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        if note_name not in note_to_semitone:
            raise ValueError(f"Unrecognized note name: {note_name}")
        return note_to_semitone[note_name] + (octave + 1) * 12

    def get_note_at_interval(self, interval: int) -> str:
        """Get the note name at the specified interval from this note."""
        base_semitone = self.NOTE_TO_SEMITONE[self.note_name]
        new_semitone = (base_semitone + interval) % 12
        return self.SEMITONE_TO_NOTE[new_semitone]

    def transpose(self, steps: int) -> 'Note':
        """
        Transpose the note by the specified number of semitones.
        
        Args:
            steps: Number of semitones to transpose by (positive or negative)
            
        Returns:
            A new Note object transposed by the specified number of steps
            
        Raises:
            ValueError: If the resulting note would be outside valid MIDI range (0-127)
        """
        current_midi = self.midi_number
        new_midi_number = current_midi + steps
        
        # Test transposition before creating new note
        if new_midi_number < 0 or new_midi_number > 127:
            raise ValueError("MIDI number out of range")
        
        note_name, octave = self._midi_to_note_octave(new_midi_number)
        
        # Validate octave range
        if octave < 0 or octave > 8:  # Changed from 10 to 8
            raise ValueError("MIDI number out of range")  # Changed error message
        
        # Create new note with transposed values
        return Note(
            note_name=note_name,
            octave=octave,
            duration=self.duration,
            velocity=self.velocity
        )

    def full_note_name(self) -> str:
        """Return the full note name."""
        return f'{self.note_name}{self.octave}' if self.octave is not None else self.note_name

    def __str__(self) -> str:
        return self.full_note_name()