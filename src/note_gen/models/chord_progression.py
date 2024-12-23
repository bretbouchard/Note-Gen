"""Module for defining chord progressions in music theory.

This module provides classes and functions for representing and manipulating chord progressions, including their structure, analysis, and relationships to musical scales. It allows for the creation of chord progressions that can be used in compositions and analyses.

ChordProgression Class
-----------------------

The ChordProgression class encapsulates a sequence of chords, allowing for manipulation and analysis of the progression.

Usage
-----

To create a chord progression, instantiate the ChordProgression class with a list of chords:

```python
progression = ChordProgression(ScaleInfo(), ['C', 'G', 'Am', 'F'])
progression.add_chord('Dm')
print(progression)
```

This module is designed to be extensible, allowing for the addition of new properties and methods related to chord progression analysis as needed.

This module allows for the creation and manipulation of chord progressions, including validation and transposition.
"""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field, model_validator, ConfigDict, validator, field_validator
import logging

from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_quality import ChordQuality
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.scale_info import ScaleInfo

# Set up logging
logger = logging.getLogger(__name__)

class ChordProgression(BaseModel):
    """Class representing a progression of chords."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    scale_info: ScaleInfo
    chords: List[Chord] = Field(default_factory=list)  # Ensure this is initialized correctly

    @field_validator('chords')
    def validate_chords(cls, v: List[Chord]) -> List[Chord]:
        if not v:  # Checks if the list is empty
            raise ValueError("Chords cannot be empty.")
        return v

    def add_chord(self, chord: Chord) -> None:
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:
        return self.chords

    def transpose(self, interval: int) -> None:
        logger.debug(f"Transposing progression by {interval} intervals")
        for chord in self.chords:
            if chord.root:
                new_midi_number = chord.root.midi_number + interval
                new_root = Note.from_midi(midi_number=new_midi_number)
                new_quality = chord.quality or ChordQualityType.MAJOR  # Default to MAJOR if None
                chord.root = new_root
                chord.quality = new_quality
                chord.chord_notes = chord.generate_chord_notes(new_root, new_quality, chord.inversion)
                logger.debug(f"Transposed chord: root={new_root}, quality={new_quality}")

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        d = super().dict(*args, **kwargs)
        d['chords'] = [chord.dict() for chord in self.chords]
        d['scale_info'] = self.scale_info.dict()
        return d