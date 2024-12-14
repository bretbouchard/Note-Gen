"""Module for handling chord progressions."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, root_validator

from .chord import Chord
from .scale_info import ScaleInfo




class ChordProgression(BaseModel):
    """A chord progression."""
    chords: List[Chord] = Field(default_factory=list)
    scale_info: Optional[ScaleInfo] = None

    @root_validator(pre=True)
    def validate_chords(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the chords in the progression."""
        if 'chords' not in values:
            values['chords'] = []
        return values

    def add_chord(self, chord: Chord) -> None:
        """Add a chord to the progression."""
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        """Get chord at specified index."""
        if index < 0 or index >= len(self.chords):
            raise ValueError(f"Invalid chord index: {index}")
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:
        """Get all chords in the progression."""
        return self.chords

    def transpose(self, semitones: int) -> ChordProgression:
        """Transpose the progression by a number of semitones."""
        new_chords = []
        for chord in self.chords:
            new_root = chord.root.transpose(semitones)
            new_chord = Chord(
                root=new_root,
                quality=chord.quality,
                inversion=chord.inversion,
                duration=chord.duration,
                velocity=chord.velocity
            )
            new_chords.append(new_chord)

        return ChordProgression(
            chords=new_chords,
            scale_info=self.scale_info
        )

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = super().dict(*args, **kwargs)
        d['chords'] = [chord.dict() for chord in self.chords]
        if self.scale_info:
            d['scale_info'] = self.scale_info.dict()
        return d
