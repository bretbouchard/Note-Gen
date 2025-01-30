# src/note_gen/models/note.py
import re
from pydantic import BaseModel, Field, validator, ValidationError, root_validator, ConfigDict
from typing import Any, ClassVar, Dict, Tuple, Optional, Union
import logging

# Configure logging to output to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class NoteConfig(ConfigDict):
    arbitrary_types_allowed = True
    use_enum_values = True
    validate_assignment = True

class Note(BaseModel):
    "A musical note with optional MIDI number auto-population."
    note_name: str
    octave: int
    duration: float = Field(default=1.0)
    velocity: int = Field(default=64)
    stored_midi_number: Optional[int] = None

    Config = NoteConfig

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

    @validator('octave')
    @classmethod
    def validate_octave(cls, octave):
        if octave < 0 or octave > 8:
            raise ValueError("Invalid octave:")
        return octave

    @validator('note_name')
    @classmethod
    def validate_note_name(cls, note_name):
        if not re.match(r'^[A-G][#b]?\d?$', note_name):
            raise ValueError(f"Invalid note name: {note_name}")  # Include the invalid note name
        return note_name

    @validator('duration')
    @classmethod
    def validate_duration(cls, duration):
        if duration <= 0:
            raise ValueError("Input should be greater than 0")
        return duration

    @validator('velocity')
    @classmethod
    def validate_velocity(cls, velocity):
        if not (0 <= velocity <= 127):
            raise ValueError('Velocity must be between 0 and 127')
        return velocity

    @classmethod
    def calculate_midi_number(cls, note_name: str, octave: int) -> int:
        note_to_semitone = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        semitone = note_to_semitone.get(note_name)
        if semitone is None:
            raise ValueError("Invalid note name:")  # Updated error message
        
        midi_number = (octave + 1) * 12 + semitone  # MIDI numbers start from C-1 (MIDI 0)
        if midi_number < 0 or midi_number > 127:
            raise ValueError("MIDI number out of range:")
        return midi_number

    @classmethod
    def normalize_note_name(cls, note_name: str) -> str:
        """Normalize the note name to uppercase and valid accidentals."""
        match = re.match(r"^[A-Ga-g][#b]?\d{0,1}$", note_name)
        if not match:
            raise ValueError("Invalid note name:")  # Reverted error message  
        # Keep the accidental in the same case
        base_note = note_name[0].upper()
        if len(note_name) > 1 and note_name[1] in ['#', 'b']:
            return base_note + note_name[1]
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
            raise ValueError("MIDI number out of range:")
        note_name, octave = cls._midi_to_note_octave(midi_number)
        return cls(
            note_name=note_name,
            octave=octave,
            duration=duration,
            velocity=velocity,
        )

    @classmethod
    def from_name(cls, note_name: str, octave: int = 4, duration: float = 1.0, velocity: int = 64):
        logging.debug(f"Creating Note from name: {note_name}, octave: {octave}, duration: {duration}, velocity: {velocity}")
        if not isinstance(note_name, str) or not note_name:
            raise ValueError("Invalid note name: Must be a non-empty string")
        match = re.match(r'([A-G][#b]?)(\d?)', note_name)
        if not match:
            raise ValueError("Invalid note name:")  # Updated error message
        note_name, octave = match.groups()
        octave = int(octave) if octave else 4
        if octave < 0 or octave > 8:
            raise ValueError("Invalid octave:")
        midi_number = cls.calculate_midi_number(note_name, octave)
        if midi_number < 0 or midi_number > 127:
            raise ValueError("MIDI number out of range:")
        return cls(note_name=cls.normalize_note_name(note_name), octave=octave, duration=duration, velocity=velocity)

    @classmethod
    def from_midi_number(cls, midi_number: int, duration: float, velocity: int) -> 'Note':
        """Create a Note from a MIDI number."""
        if not (0 <= midi_number <= 127):
            raise ValueError("MIDI number out of range:")
        # Logic to convert MIDI number to note name and octave
        note_name, octave = cls._midi_to_note_octave(midi_number)
        
        # Validate octave range
        if octave < 0 or octave > 8:
            raise ValueError("Invalid octave:")
    
        # Create new note with transposed values
        return cls(note_name=note_name, octave=octave, duration=duration, velocity=velocity)

    @classmethod
    def fill_missing_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if data is None:
            raise ValueError("Expected a dict, int, or str for Note")

        if isinstance(data, int):
            return cls._fill_from_midi(data)

        if isinstance(data, str):
            raise ValueError("Invalid note name format")

        if not isinstance(data, dict):
            raise ValueError("Expected a dict, int, or str for Note")  # Updated error message

        if not data:
            return {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 64}

        # Validate note_name format
        if 'note_name' in data and not re.match(r'^[A-G][#b]?\d?$', data['note_name']):
            raise ValueError("Unrecognized note name")  # Ensure consistency with initialization error message

        # Add octave validation here
        if 'octave' in data:
            if data['octave'] < 0 or data['octave'] > 8:
                raise ValueError(f"Octave must be between 0 and 8: {data['octave']}")

        # Set default values for missing fields
        data.setdefault('duration', 1.0)
        data.setdefault('velocity', 64)

        if 'note_name' not in data:
            raise ValueError("Missing note_name in dictionary")
        if 'octave' not in data:
            raise ValueError("Missing octave in dictionary")
        data['stored_midi_number'] = None
        return data

    @classmethod
    def _fill_from_midi(cls, midi_number: int) -> Dict[str, Any]:
        if not (0 <= midi_number <= 127):
            raise ValueError("MIDI number out of range:")
        note_name, octave = cls._midi_to_note_octave(midi_number)
        return {
            "note_name": note_name, 
            "octave": octave,
            "stored_midi_number": midi_number  
        }

    @classmethod
    def _fill_from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if 'note_name' not in data:
            raise ValueError("Missing note_name in dictionary")
        if 'octave' not in data:
            raise ValueError("Missing octave in dictionary")
        data['stored_midi_number'] = cls.calculate_midi_number(data['note_name'], data['octave'])
        return data

    @classmethod
    def _fill_from_str(cls, note_str: str) -> Dict[str, Any]:
        match = re.match(r'([A-Ga-g][#b]?)(\d+)', note_str)
        if not match:
            raise ValueError("Invalid note name format")
        note_name, octave = match.groups()
        return {
            "note_name": note_name,
            "octave": int(octave),
            "stored_midi_number": cls.calculate_midi_number(note_name, int(octave))
        }

    @classmethod
    def note_name_to_midi(cls, note_name: str) -> int:
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
            raise ValueError("MIDI number out of range:")
        semitone_to_note = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_number // 12) - 1
        note_index = midi_number % 12
        # Handle edge cases for octave 0
        if octave < 0:
            octave = 0
        # For MIDI number 127, we should allow octave 10
        if octave > 10:
            raise ValueError("Invalid octave:")
        return semitone_to_note[note_index], octave

    @staticmethod
    def _note_octave_to_midi(note_name: str, octave: int) -> int:
        """Convert a note name and octave to a MIDI number."""
        if not (0 <= octave <= 10):
            raise ValueError("Invalid octave:")
        note_to_semitone = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        if note_name not in note_to_semitone:
            raise ValueError("Unrecognized note name")
        return note_to_semitone[note_name] + (octave + 1) * 12

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the note, including stored_midi_number."""
        return {
            'note_name': self.note_name,
            'octave': self.octave,
            'duration': self.duration,
            'velocity': self.velocity,
            'stored_midi_number': self.stored_midi_number
        }  

    def get_note_at_interval(self, interval: int) -> str:
        """Get the note name at the specified interval from this note."""
        base_semitone = self.NOTE_TO_SEMITONE[self.note_name]
        new_semitone = (base_semitone + interval) % 12
        return self.SEMITONE_TO_NOTE[new_semitone]

    def transpose(self, semitones: int) -> 'Note':
        new_semitone = (self.NOTE_TO_SEMITONE[self.note_name] + semitones) % 12
        new_octave = self.octave + (self.NOTE_TO_SEMITONE[self.note_name] + semitones) // 12
    
        # Check for valid octave range
        if new_octave < 0:
            raise ValueError("MIDI number out of range")
        elif new_octave > 8:
            raise ValueError("MIDI number out of range")
    
        new_note_name = self.SEMITONE_TO_NOTE[new_semitone]
        return Note(note_name=new_note_name, octave=new_octave, duration=self.duration, velocity=self.velocity)

    def full_note_name(self) -> str:
        """Return the full note name."""
        return f'{self.note_name}{self.octave}' if self.octave is not None else self.note_name

    def __str__(self) -> str:
        return self.full_note_name()