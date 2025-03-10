import logging
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)  # You can adjust the level as needed

from typing import List, Optional, Dict, Any, ClassVar, Tuple, Union
from pydantic import BaseModel, ConfigDict, field_validator, config
import re
from enum import Enum

from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.chord import Chord

class Scale(BaseModel):
    root: Note
    scale_type: ScaleType
    notes: List[Note] = []
    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook to generate notes if not provided."""
        if not self.notes:
            self.notes = self._generate_scale_notes()

    def _generate_scale_notes(self) -> List[Note]:
        """Generate the notes for this scale based on root note and scale type."""
        intervals_map = {
            ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11],
            ScaleType.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
            ScaleType.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11],
            ScaleType.PENTATONIC_MAJOR: [0, 2, 4, 7, 9],
            ScaleType.PENTATONIC_MINOR: [0, 3, 5, 7, 10],
            ScaleType.BLUES: [0, 3, 5, 6, 7, 10],
            ScaleType.WHOLE_TONE: [0, 2, 4, 6, 8, 10],
            ScaleType.CHROMATIC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
            ScaleType.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
            ScaleType.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
            ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
            ScaleType.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
        }
        
        if self.scale_type not in intervals_map:
            raise ValueError(f"No intervals defined for scale type: {self.scale_type}")
        
        intervals = intervals_map[self.scale_type]
        scale_notes = []
        base_midi = self.root.midi_number
        
        for interval in intervals:
            new_midi = base_midi + interval
            if new_midi < 0 or new_midi > 127:
                raise ValueError(f"Generated note would be out of MIDI range: {new_midi}")
                
            new_note = Note.from_midi_number(
                midi_number=new_midi,
                duration=int(self.root.duration),
                velocity=self.root.velocity
            )
            scale_notes.append(new_note)
            
        # Add the octave note
        octave_midi = base_midi + 12
        if octave_midi <= 127:
            octave_note = Note.from_midi_number(
                midi_number=octave_midi,
                duration=int(self.root.duration),
                velocity=self.root.velocity
            )
            scale_notes.append(octave_note)
            
        return scale_notes

    def get_scale_degree(self, degree: int) -> Note:
        """Get the note at a specific scale degree."""
        if not self.validate_degree(degree):
            raise ValueError(f"Scale degree must be between 1 and {len(self.notes)}")
            
        return self.notes[degree - 1]

    def validate_degree(self, degree: int) -> bool:
        """Validate if a scale degree is valid for this scale."""
        return 1 <= degree <= len(self.notes)

    @property
    def degree_count(self) -> int:
        """Get the number of degrees in this scale."""
        return len(self.notes)

    @property
    def is_diatonic(self) -> bool:
        """Check if this scale is diatonic (has 7 notes)."""
        return len(self.notes) == 7

    def get_scale_degrees(self) -> List[int]:
        """Get all valid scale degrees for this scale."""
        return list(range(1, len(self.notes) + 1))

    def __str__(self) -> str:
        note_names = [note.note_name for note in self.notes]
        return f"{self.root.note_name} {self.scale_type} Scale: {', '.join(note_names)}"

class ChordProgression(BaseModel):
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)

CHORD_QUALITY_ALIASES = {
    "dominant": Chord.quality.dominant7,           # Map to the enum value, not the enum name
    "dom": Chord.quality.dominant7, 
    'maj': Chord.quality.MAJOR,
    'min': Chord.quality.MINOR,
    'm': Chord.quality.MINOR,
    'dim': Chord.quality.DIMINISHED,
    'aug': Chord.quality.AUGMENTED,
    '7': Chord.quality.DOMINANT7,
    'maj7': Chord.quality.MAJOR7,
    'min7': Chord.quality.MINOR7,
    'm7': Chord.quality.MINOR7,
    'dim7': Chord.quality.DIMINISHED7,
    'm7b5': Chord.quality.M7B5,
    'sus2': Chord.quality.SUSPENDED2,
    'sus4': Chord.quality.SUSPENDED4,
    '6': Chord.quality.MAJOR7,
    'm6': Chord.quality.MINOR7,
    'minmaj7': Chord.quality.MINOR_MAJOR7,
    'aug7': Chord.quality.AUGMENTED7,
    'ø7': Chord.quality.HALF_DIMINISHED7,
    'b5': Chord.quality.FLAT5,
    '#5': Chord.quality.SHARP5,
    '#7': Chord.quality.SHARP7,
}
