"""Module for defining chord progressions in music theory.

This module provides classes and functions for representing and manipulating chord progressions, including their structure, analysis, and relationships to musical scales. It allows for the creation of chord progressions that can be used in compositions and analyses.

ChordProgression Class
-----------------------

The ChordProgression class encapsulates a sequence of chords, allowing for manipulation and analysis of the progression.

Usage
-----

To create a chord progression, instantiate the ChordProgression class with a list of chords:

```python
progression = ChordProgression(['C', 'G', 'Am', 'F'])
progression.add_chord('Dm')
print(progression)
```

This module is designed to be extensible, allowing for the addition of new properties and methods related to chord progression analysis as needed.

This module allows for the creation and manipulation of chord progressions, including validation and transposition.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
import logging

from .chord import Chord, ChordQuality
from .scale_info import ScaleInfo

logger = logging.getLogger(__name__)

class ChordProgression(BaseModel):
    """Class representing a progression of chords.

    This class encapsulates a sequence of chords, allowing for manipulation and analysis of the progression. It provides methods for adding chords, analyzing the progression, and converting it to a string representation.

    A chord progression consisting of multiple chords."""
    
    class Config:
        arbitrary_types_allowed = True
    
    chords: List[Chord] = Field(default_factory=list)
    scale_info: Optional[ScaleInfo] = None

    @model_validator(mode='before')
    def validate_chords(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the chords in the progression."""
        logger.info("Validating chords in the progression.")
        if 'chords' not in values:
            values['chords'] = []
        for chord in values['chords']:
            if not isinstance(chord, Chord):
                logger.error(f"Invalid chord: {chord}. Must be an instance of Chord.")
                raise ValueError(f"Invalid chord: {chord}. Must be an instance of Chord.")
        logger.info("Chord validation completed successfully.")
        return values

    def add_chord(self, chord: Chord) -> None:
        if chord is None or not isinstance(chord, Chord):
            raise ValueError("Invalid chord type. Must be a Chord instance.")
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:

        return self.chords

    def transpose(self, semitones: int) -> ChordProgression:
        """Transpose the progression by a number of semitones.
        
        Args:
            semitones (int): Number of semitones to transpose by
            
        Returns:
            ChordProgression: A new chord progression with transposed chords.
        """
        logger.info(f"Transposing progression by {semitones} semitones")
        new_chords = []
        for chord in self.chords:
            if chord.root is None:
                continue  # Skip chords with no root note
            new_root = chord.root.transpose(semitones)
            new_chord = Chord(
                root=new_root,
                quality=ChordQuality(chord.quality),
                notes=chord.get_notes(),
                bass=chord.bass,
                inversion=chord.inversion
            )
            new_chords.append(new_chord)

        return ChordProgression(
            chords=new_chords,
            scale_info=self.scale_info
        )

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dict[str, Any]: A dictionary representation of the chord progression.
        """
        d = super().dict(*args, **kwargs)
        d['chords'] = [chord.dict() for chord in self.chords]
        if self.scale_info:
            d['scale_info'] = self.scale_info.dict()
        return d