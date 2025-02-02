from typing import Dict, ClassVar, Optional, Tuple, Any, Union
from pydantic import BaseModel, field_validator, ConfigDict

class Note(BaseModel):
    """A musical note with a name, octave, duration, and velocity."""
    note_name: str
    octave: int
    duration: float = 1.0  # Default duration of 1 beat
    velocity: int = 100  # Default MIDI velocity
    stored_midi_number: Optional[int] = None

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

    # Maps semitone values to their preferred note names
    SEMITONE_TO_NOTE: ClassVar[Dict[int, str]] = {
        0: 'C', 1: 'C#', 2: 'D', 3: 'Eb',
        4: 'E', 5: 'F', 6: 'F#', 7: 'G',
        8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'
    }

    INVALID_NOTE_NAME_ERROR: ClassVar[str] = "Invalid note name format:"

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    @field_validator('note_name')
    @classmethod
    def validate_note_name(cls, v: str) -> str:
        try:
            normalized = cls.normalize_note_name(v)
            if normalized not in cls.NOTE_TO_SEMITONE:
                raise ValueError(cls.INVALID_NOTE_NAME_ERROR)
            return normalized
        except ValueError:
            raise ValueError(cls.INVALID_NOTE_NAME_ERROR)

    @field_validator('octave')
    def validate_octave(cls, v: int) -> int:
        """Validate the octave value."""
        if not (0 <= v <= 8):
            raise ValueError("Invalid octave:")
        return v

    @field_validator('duration')
    def validate_duration(cls, v: float) -> float:
        """Validate that the duration is positive."""
        if v <= 0:
            raise ValueError("Input should be greater than 0:")
        return v

    @field_validator('velocity')
    def validate_velocity(cls, v: int) -> int:
        """Validate that the velocity is within MIDI range (0-127)."""
        if not (0 <= v <= 127):
            raise ValueError(f"Velocity must be between 0 and 127: {v}")
        return v

    @property
    def midi_number(self) -> int:
        """Get the MIDI number for this note."""
        if self.stored_midi_number is not None:
            return self.stored_midi_number
        return self._note_octave_to_midi(self.note_name, self.octave)

    @classmethod
    def _note_octave_to_midi(cls, note_name: str, octave: int) -> int:
        """Convert a note name and octave to a MIDI number."""
        if note_name not in cls.NOTE_TO_SEMITONE:
            raise ValueError("Unrecognized note name:")
        semitone = cls.NOTE_TO_SEMITONE[note_name]
        midi_number = (octave + 1) * 12 + semitone
        if not (0 <= midi_number <= 127):
            raise ValueError(f"MIDI number out of range: {midi_number}")
        return midi_number

    @classmethod
    def _midi_to_note_octave(cls, midi_number: int) -> Tuple[str, int]:
        """Convert a MIDI number to a note name and octave."""
        if not (0 <= midi_number <= 127):
            raise ValueError(f"MIDI number out of range: {midi_number}")
        octave = (midi_number // 12) - 1
        if midi_number == 0:  # Special case for MIDI note 0 (C0)
            octave = 0
        semitone = midi_number % 12
        note_name = cls.SEMITONE_TO_NOTE[semitone]
        return note_name, octave

    @classmethod
    def from_midi(cls, midi_number: int, velocity: int = 100, duration: float = 1.0) -> 'Note':
        """Creates a Note instance from a MIDI number."""
        if not (0 <= midi_number <= 127):
            raise ValueError(f"Invalid MIDI number: {midi_number}")
        note_name = cls.SEMITONE_TO_NOTE[midi_number % 12]
        octave = midi_number // 12 - 1
        return cls(note_name=note_name, octave=octave, velocity=velocity, duration=duration)

    @classmethod
    def from_full_name(cls, full_name: str, duration: float = 1.0, velocity: int = 100) -> 'Note':
        """Create a Note from a full note name (e.g., 'C4')."""
        # Validate the note name format
        if len(full_name) < 2 or not full_name[-1].isdigit():
            raise ValueError('Invalid note name format:')
        
        # Handle cases like 'C#4' or 'Bb3'
        if full_name[-2].isdigit():
            octave = int(full_name[-2:])
            note_name = full_name[:-2]
        else:
            octave = int(full_name[-1])
            note_name = full_name[:-1]
        
        note_name = cls.normalize_note_name(note_name)
        if note_name not in cls.NOTE_TO_SEMITONE:
            raise ValueError('Invalid note name format:')
        return cls(note_name=note_name, octave=octave, duration=duration, velocity=velocity)

    @classmethod
    def from_name(cls, note_str: str, duration: float = 1.0, velocity: int = 100) -> 'Note':
        """Create a Note from a string like 'C4' or 'F#5'."""
        if len(note_str) < 2:
            raise ValueError("Invalid note name format")
            
        try:
            # Split into note name and octave
            if note_str[-2].isdigit():  # Handle cases like 'C#4'
                octave = int(note_str[-2:])
                note_name = note_str[:-2]
            else:  # Handle cases like 'C4'
                octave = int(note_str[-1])
                note_name = note_str[:-1]
                
            note_name = cls.normalize_note_name(note_name)
            return cls(note_name=note_name, octave=octave, duration=duration, velocity=velocity)
        except (ValueError, IndexError):
            raise ValueError(cls.INVALID_NOTE_NAME_ERROR)

    @classmethod
    def from_midi_number(cls, midi_number: int, duration: float = 1.0, velocity: int = 100) -> 'Note':
        """Alias for from_midi for backward compatibility."""
        return cls.from_midi(midi_number, duration, velocity)

    def transpose(self, semitones: int) -> 'Note':
        """Transpose the note by a number of semitones."""
        new_midi = self.midi_number + semitones
        try:
            return self.from_midi(new_midi, self.duration, self.velocity)
        except ValueError:
            raise ValueError("MIDI number out of range")

    @classmethod
    def normalize_note_name(cls, note_name: str) -> str:
        """Normalize a note name to standard format."""
        if not note_name or not note_name.strip():
            raise ValueError(cls.INVALID_NOTE_NAME_ERROR)
        
        # Convert to uppercase first character, lowercase rest
        try:
            normalized = note_name[0].upper() + note_name[1:].lower()
            
            # Handle special cases for accidentals
            if len(normalized) > 1 and normalized[1] in ['b', '#']:
                if normalized[1] == 'b':
                    normalized = normalized[0] + 'b'  # Keep 'b' lowercase
                else:
                    normalized = normalized[0] + '#'  # Keep '#' as is
            
            # Validate that the normalized note name is valid
            if normalized not in cls.NOTE_TO_SEMITONE:
                raise ValueError(cls.INVALID_NOTE_NAME_ERROR)
            
            return normalized
        except IndexError:
            raise ValueError(cls.INVALID_NOTE_NAME_ERROR)

    @classmethod
    def fill_missing_fields(cls, data: Union[Dict[str, Any], int, str]) -> Dict[str, Any]:
        """Fill in missing fields for note creation."""
        if isinstance(data, dict):
            if not data:
                # Allow empty dict and fill with defaults
                result = {
                    'note_name': 'C',
                    'octave': 4,
                    'duration': 1.0,
                    'velocity': 64,
                    'stored_midi_number': None
                }
            else:
                result = {
                    'duration': 1.0,
                    'velocity': 64,
                    'stored_midi_number': None,
                    **data
                }
                if "note_name" in result:
                    try:
                        result["note_name"] = cls.normalize_note_name(result["note_name"])
                        if result["note_name"] not in cls.NOTE_TO_SEMITONE:
                            raise ValueError("Unrecognized note name")
                    except ValueError:
                        raise ValueError("Unrecognized note name")
                if "octave" in result and not (0 <= result["octave"] <= 8):
                    raise ValueError(f"Octave must be between 0 and 8: {result['octave']}")
            return result
        elif isinstance(data, int):
            note_name, octave = cls._midi_to_note_octave(data)
            return {
                'note_name': note_name,
                'octave': octave,
                'duration': 1.0,
                'velocity': 64,
                'stored_midi_number': data
            }
        elif isinstance(data, str):
            try:
                note = cls.from_name(data)
                return note.model_dump()
            except ValueError:
                raise ValueError(cls.INVALID_NOTE_NAME_ERROR)
        else:
            raise ValueError("Expected a dict, int, or str for Note")

    def __eq__(self, other: object) -> bool:
        """Compare two notes for equality."""
        if not isinstance(other, Note):
            return NotImplemented
        return (
            self.note_name == other.note_name
            and self.octave == other.octave
            and self.duration == other.duration
            and self.velocity == other.velocity
        )

    @classmethod
    def note_name_to_midi(cls, note_name: str) -> int:
        """Convert a note name to its MIDI number offset (0-11)."""
        try:
            normalized = cls.normalize_note_name(note_name)
            if normalized not in cls.NOTE_TO_SEMITONE:
                raise ValueError("Unrecognized note name")
            return cls.NOTE_TO_SEMITONE[normalized]
        except ValueError as e:
            # Re-raise with the same message
            raise ValueError("Unrecognized note name")

    def full_note_name(self) -> str:
        """Get the full note name including octave."""
        return f"{self.note_name}{self.octave}"

    def __str__(self) -> str:
        return f'{self.note_name}{self.octave}'

    def __repr__(self) -> str:
        return f'Note(note_name={self.note_name}, octave={self.octave}, duration={self.duration}, velocity={self.velocity})'