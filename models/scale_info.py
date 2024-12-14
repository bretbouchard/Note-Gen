"""Module for handling scale info."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .note import Note
from .scale_degree import ScaleDegree

# Define scale intervals for different modes
SCALE_INTERVALS = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10]
}

class ScaleInfo(BaseModel):
    """Information about a musical scale."""
    root: Note
    scale_type: str = Field(default="major")
    key_signature: str = Field(default="")
    intervals: List[int] = Field(default_factory=list)
    scale_degrees: Optional[List[ScaleDegree]] = Field(default=None)
    mode: Optional[str] = None
    _notes: List[Note] = Field(default_factory=list)

    def compute_scale_degrees(self) -> List[ScaleDegree]:
        """Compute the scale degrees for this scale."""
        if self.scale_degrees is not None:
            return self.scale_degrees

        # Choose intervals based on mode
        intervals = SCALE_INTERVALS.get(self.scale_type, SCALE_INTERVALS['major'])

        # Create scale degrees
        scale_degrees = []
        for i, interval in enumerate(intervals):
            note = self.root.transpose(interval)
            scale_degree = ScaleDegree(
                degree=i + 1,
                note=note,
                scale_info=self
            )
            scale_degrees.append(scale_degree)

        self.scale_degrees = scale_degrees
        return scale_degrees

    def get_scale_degree(self, degree: int) -> Optional[Note]:
        """Get a note at a specific scale degree."""
        if not self.scale_degrees:
            return None
        if degree < 1 or degree > len(self.scale_degrees):
            return None
        return self.scale_degrees[degree - 1].note

    def get_scale_notes(self) -> List[Note]:
        """Get all notes in the scale."""
        if not self.scale_degrees:
            return []
        return [degree.note for degree in self.scale_degrees]

    def get_notes(self) -> List[Note]:
        return [note for note in self._notes if note]

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = super().dict(*args, **kwargs)
        d['root'] = self.root.dict()
        if self.scale_degrees:
            d['scale_degrees'] = [sd.dict() for sd in self.scale_degrees]
        return d
