"""
Module for handling musical scales.
"""

from __future__ import annotations
import logging
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator
from .musical_elements import Note
from .scale_type import ScaleType
from .scale_degree import ScaleDegree
from .scale_info import ScaleInfo
from .chord import Chord  # Import Chord class

logger = logging.getLogger(__name__)


class Scale(BaseModel):
    """A musical scale."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Note
    quality: str = Field('major', description="Scale quality (e.g., major, minor)")
    scale_type: str = Field('major', description="Scale type (e.g., major, minor)")
    notes: List[Note] = Field(default_factory=list)
    intervals: List[int] = Field(default_factory=list)
    scale_degree: int = Field(1, description="Scale degree (1-7)")
    numeral: str = Field(default="I")
    numeral_str: str = Field(default="")
    is_major: bool = Field(default=False)
    is_diminished: bool = Field(default=False)
    is_augmented: bool = Field(default=False)
    is_half_diminished: bool = Field(default=False)
    has_seventh: bool = Field(default=False)
    has_ninth: bool = Field(default=False)
    has_eleventh: bool = Field(default=False)
    inversion: int = Field(default=0)
    scale_info_v2: Optional[ScaleInfo] = None

    SCALE_INTERVALS: Dict[str, List[int]] = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10]
    }

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: str) -> str:
        valid_qualities = ["major", "minor", "diminished", "augmented"]
        if v not in valid_qualities:
            raise ValueError(f"Invalid scale quality: {v}")
        return v

    @field_validator("scale_type")
    @classmethod
    def validate_scale_type(cls, v: str) -> str:
        valid_types = ["major", "minor", "harmonic_minor", "melodic_minor"]
        if v not in valid_types:
            raise ValueError(f"Invalid scale type: {v}")
        return v

    def get_notes(self) -> List[Note]:
        """Get all notes in the scale."""
        if not self.notes:
            self.notes = self._generate_scale_notes()
        return self.notes

    def _generate_scale_notes(self) -> List[Note]:
        """Generate notes for the scale."""
        notes = []
        base_midi = self.root.midi_number
        intervals = self.SCALE_INTERVALS.get(self.quality.lower(), self.SCALE_INTERVALS['major'])
        
        for interval in intervals:
            midi_number = base_midi + interval
            if 0 <= midi_number <= 127:
                notes.append(Note.from_midi(midi_number))
        return notes

    def get_scale_degree(self, degree: int) -> Optional[Note]:
        """Get the note at a specific scale degree."""
        if not 1 <= degree <= 7:
            return None
        # Calculate the midi number based on the root note and the degree
        intervals = self.SCALE_INTERVALS[self.scale_type]
        midi_number = self.root.midi_number + intervals[degree - 1]
        note_name = Note.from_midi(midi_number).note_name
        octave = Note.from_midi(midi_number).octave
        return Note(note_name=note_name, octave=octave, midi_number=midi_number)

    def get_chord_at(self, degree: int) -> Chord:
        """Get the chord at a specific scale degree."""
        if not 1 <= degree <= 7:
            raise ValueError("Scale degree must be between 1 and 7")

        # Calculate the root note for the chord based on the scale degree
        chord_root = self.get_scale_degree(degree)
        if chord_root is None:
            raise ValueError("No note found for the specified scale degree")

        # Create and return the chord using the chord quality
        return Chord(root=chord_root, quality=self.quality) 

    @classmethod
    def create_default(cls, root: Note, quality: str = "major", scale_degree: int = 1, numeral: str = "I") -> 'Scale':
        """Create a default scale."""
        return cls(
            root=root,
            quality=quality,
            scale_type=quality,
            numeral=numeral,
            scale_degree=scale_degree,
            is_major=quality == "major"
        )

    @classmethod
    def from_scale_info(cls, scale_info: ScaleInfo, numeral: str = 'I', scale_degree: int = 1) -> 'Scale':
        """Create a scale from ScaleInfo."""
        scale = cls.create_default(
            root=scale_info.root,
            quality='major',
            scale_degree=scale_degree,
            numeral=numeral
        )
        scale.scale_info_v2 = scale_info
        return scale

    def __str__(self) -> str:
        """String representation of the scale."""
        return f"{self.root.full_note_name} {self.quality}"
