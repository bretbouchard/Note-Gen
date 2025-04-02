"""Note model module."""
from typing import Any, ClassVar, Optional, Dict
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import re
from src.note_gen.core.constants import FULL_NOTE_REGEX

class Note(BaseModel):
    """A musical note model."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        from_attributes=True
    )

    # MIDI note numbers for each pitch in octave 4
    MIDI_BASE_NOTES: ClassVar[Dict[str, int]] = {
        'C': 60, 'C#': 61, 'Db': 61,
        'D': 62, 'D#': 63, 'Eb': 63,
        'E': 64,
        'F': 65, 'F#': 66, 'Gb': 66,
        'G': 67, 'G#': 68, 'Ab': 68,
        'A': 69, 'A#': 70, 'Bb': 70,
        'B': 71
    }

    pitch: str = Field(..., description="The pitch of the note (A-G with optional # or b)")
    octave: Optional[int] = Field(None, ge=-1, le=9, description="The octave number (-1 to 9)")
    duration: float = Field(1.0, gt=0, description="Duration in beats")
    velocity: int = Field(64, ge=0, le=127, description="MIDI velocity (0-127)")
    position: float = Field(0.0, ge=0, description="Position in beats")
    stored_midi_number: Optional[int] = Field(None, description="Stored MIDI number")

    @property
    def accidental(self) -> Optional[str]:
        """Get the accidental of the note (#, b, or None)."""
        if len(self.pitch) > 1:
            return self.pitch[1]
        return None

    @property
    def midi_number(self) -> int:
        """Get the MIDI number for this note."""
        return self.to_midi_number()

    @classmethod
    def validate_midi_number(cls, midi_number: int) -> None:
        """Validate a MIDI number."""
        if not 0 <= midi_number <= 127:
            raise ValueError(f"MIDI number must be between 0 and 127, got {midi_number}")

    @classmethod
    def normalize_pitch(cls, pitch: str) -> str:
        """Normalize pitch string to standard format."""
        # Convert to uppercase but preserve 'b' for flats
        pitch = pitch.strip()
        if pitch.endswith('b'):
            pitch = pitch[:-1].upper() + 'b'
        else:
            pitch = pitch.upper()

        if not re.match(r'^[A-G][#b]?$', pitch):
            raise ValueError(f"Invalid pitch format: {pitch}")
        return pitch

    @classmethod
    def from_name(cls, name: str, duration: float = 1.0, velocity: int = 64,
                 position: float = 0.0, default_octave: int = 4, stored_midi_number: Optional[int] = None) -> 'Note':
        """Create a Note from a name string with optional parameters."""
        name = name.strip()

        # First try matching with octave
        match = re.match(r'^([A-G][#b]?)(\d)$', name)

        if match:
            pitch, octave = match.groups()
            octave = int(octave)
        else:
            # Try matching without octave
            match = re.match(r'^([A-G][#b]?)$', name)
            if not match:
                raise ValueError(f"Invalid note name: {name}")
            pitch = match.group(1)
            octave = default_octave

        return cls(
            pitch=pitch,
            octave=octave,
            duration=duration,
            velocity=velocity,
            position=position,
            stored_midi_number=stored_midi_number
        )

    @classmethod
    def from_midi_number(cls, midi_number: int, duration: float = 1.0,
                        velocity: int = 64, position: float = 0.0) -> 'Note':
        """Create a Note from a MIDI note number."""
        from src.note_gen.validation.midi_validation import midi_to_octave_pitch

        cls.validate_midi_number(midi_number)

        octave, pitch_number = midi_to_octave_pitch(midi_number)
        pitch_map = {
            0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
            6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
        }

        return cls(
            pitch=pitch_map[pitch_number],
            octave=octave,
            duration=duration,
            velocity=velocity,
            position=position,
            stored_midi_number=midi_number
        )

    def to_midi_number(self) -> int:
        """Convert note to MIDI note number."""
        if self.stored_midi_number is not None:
            return self.stored_midi_number

        if self.octave is None:
            raise ValueError("Octave must be set to convert to MIDI number")
        base = self.MIDI_BASE_NOTES[self.pitch]
        octave_diff = self.octave - 4  # Adjust for octave 4 being the base
        return base + (octave_diff * 12)

    def transpose(self, semitones: int) -> 'Note':
        """Create a new note transposed by the specified number of semitones."""
        if self.octave is None:
            raise ValueError("Cannot transpose note without octave")

        midi_num = self.to_midi_number()
        new_midi = midi_num + semitones

        self.validate_midi_number(new_midi)
        return self.from_midi_number(
            new_midi,
            duration=self.duration,
            velocity=self.velocity,
            position=self.position
        )

    def get_enharmonic(self, prefer_flats: bool = False) -> 'Note':
        """Get the enharmonic equivalent of this note."""
        enharmonic_map = {
            'C#': 'Db', 'Db': 'C#',
            'D#': 'Eb', 'Eb': 'D#',
            'F#': 'Gb', 'Gb': 'F#',
            'G#': 'Ab', 'Ab': 'G#',
            'A#': 'Bb', 'Bb': 'A#'
        }

        if self.pitch in enharmonic_map:
            new_pitch = enharmonic_map[self.pitch]
            if prefer_flats and not new_pitch.endswith('b'):
                new_pitch = enharmonic_map[new_pitch]

            return Note(
                pitch=new_pitch,
                octave=self.octave,
                duration=self.duration,
                velocity=self.velocity,
                position=self.position,
                stored_midi_number=self.stored_midi_number
            )
        return self.model_copy()

    @field_validator('pitch')
    @classmethod
    def validate_pitch(cls, v: str) -> str:
        """Validate and normalize pitch."""
        return cls.normalize_pitch(v)

    @property
    def note_name(self) -> str:
        """Get the full note name including octave."""
        octave_str = str(self.octave) if self.octave is not None else ""
        return f"{self.pitch}{octave_str}"

    @property
    def pitch_name(self) -> str:
        """Get just the pitch name without octave."""
        return self.pitch

    @property
    def full_name(self) -> str:
        """Alias for note_name for backward compatibility."""
        return self.note_name

    def __str__(self) -> str:
        """Return string representation of the note."""
        return self.note_name

    @classmethod
    def validate_note_name(cls, note_name: str) -> bool:
        """Validate note name format."""
        return bool(re.fullmatch(FULL_NOTE_REGEX, note_name))
