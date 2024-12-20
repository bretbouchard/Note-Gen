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

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict, field_validator
import logging

from src.models.note import Note
from src.models.chord import Chord
from src.models.chord_quality import ChordQuality
from src.models.enums import ChordQualityType
from src.models.scale_info import ScaleInfo

# Set up logging
logger = logging.getLogger(__name__)

class ChordProgression(BaseModel):
    """Class representing a progression of chords."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    chords: List[Chord]
    scale_info: Optional[ScaleInfo] = None


    @field_validator('chords')
    def validate_chords(cls, v: List[Chord]) -> List[Chord]:
        """Validate the chords in the progression."""
        if not v:
            raise ValueError("Chords cannot be empty.")
        for chord in v:
            if not isinstance(chord, Chord):
                raise ValueError("All items in chords must be instances of Chord.")
        return v

    def add_chord(self, chord: Chord) -> None:
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        """Get a chord at a specific index."""
        if index < 0 or index >= len(self.chords):
            raise IndexError("Index out of range")
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:
        return self.chords

    def transpose(self, interval: int) -> None:
        """Transpose the chord progression by the given interval."""
        logger.debug(f"Transposing progression by {interval} intervals")
        for chord in self.chords:
            if chord.root:
                new_midi_number = chord.root.midi_number + interval
                new_root = Note.from_midi(midi_number=new_midi_number)
                
                # Determine new quality
                if chord.quality is None:
                    new_quality = ChordQualityType.MAJOR
                    logger.warning("No chord quality found, defaulting to MAJOR")
                else:
                    new_quality = chord.quality  # Already a ChordQualityType
                
                chord.root = new_root
                chord.quality = new_quality
                chord.chord_notes = chord.generate_chord_notes(new_root, new_quality, chord.inversion)
                logger.debug(f"Transposed chord: root={new_root}, quality={new_quality}")

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = super().dict(*args, **kwargs)
        d['chords'] = [chord.dict() for chord in self.chords]
        if self.scale_info:
            d['scale_info'] = self.scale_info.dict()
        return d