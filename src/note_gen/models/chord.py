"""Module for handling chords."""

from __future__ import annotations
import logging
from typing import List, Optional, Any, Dict, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator, validator
from .musical_elements import Note
from .chord_quality import ChordQualityType

logger = logging.getLogger(__name__)

class Chord(BaseModel):
    """A class representing a musical chord."""
    root: Note
    quality: ChordQualityType = Field(..., description="The quality of the chord (e.g., major, minor)")
    notes: List[Note] = Field(default_factory=list)
    inversion: int = Field(default=0, ge=0)

    VALID_QUALITIES: ClassVar[List[ChordQualityType]] = [
        ChordQualityType.MAJOR,
        ChordQualityType.MINOR,
        ChordQualityType.DIMINISHED,
        ChordQualityType.AUGMENTED,
        ChordQualityType.DOMINANT_7,
        ChordQualityType.MAJOR_7,
        ChordQualityType.MINOR_7,
        ChordQualityType.DIMINISHED_7,
        ChordQualityType.HALF_DIMINISHED_7,
    ]

    @field_validator('root', 'quality', 'inversion')
    def validate_root_quality_inversion(cls, v, values):
        logger.debug(f"Validating {v} with value: {v}")
        if v == 'root' and not values.get('root'):
            logger.error("Root cannot be empty")
            raise ValueError("Root cannot be empty")
        if v == 'quality' and values.get('quality') not in cls.VALID_QUALITIES:
            logger.error(f"Invalid quality: {values.get('quality')}")
            raise ValueError(f"Invalid quality: {values.get('quality')}")
        if v == 'inversion' and values.get('inversion') < 0:
            logger.error("Inversion cannot be negative")
            raise ValueError("Inversion cannot be negative")
        logger.debug(f"Exiting validation for {v} with value: {v}")
        return v

    @field_validator('notes')
    def validate_notes(cls, v):
        logger.debug(f"Entering validate_notes method with notes: {v}")
        if not v or len(v) == 0:
            logger.error("Chord notes cannot be empty")
            raise ValueError("Chord notes cannot be empty")
        logger.debug(f"Exiting validate_notes method with notes: {v}")
        return v

    def generate_chord_notes(self, root: Note, quality: ChordQualityType, inversion: int = 0) -> List[Note]:
        """Generate the notes for this chord based on its root and quality."""
        logger.debug(f"Entering generate_chord_notes method with root: {root}, quality: {quality}, inversion: {inversion}")
        logger.debug(f"Input values: root={root}, quality={quality}, inversion={inversion}")
        logger.debug(f"Input values: root={root}, quality={quality}, inversion={inversion}")
        logger.debug(f"Intervals for quality '{quality}': {intervals.get(quality, 'Unknown quality')}")
        logger.debug(f"Intervals for quality '{quality}': {intervals.get(quality, 'Unknown quality')}")
        if not root:
            raise ValueError("Root note is required")
        
        # Base intervals for different chord qualities
        intervals = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            ChordQualityType.DOMINANT_7: [0, 4, 7, 10],
            ChordQualityType.MAJOR_7: [0, 4, 7, 11],
            ChordQualityType.MINOR_7: [0, 3, 7, 10],
            ChordQualityType.DIMINISHED_7: [0, 3, 6, 9],
            ChordQualityType.HALF_DIMINISHED_7: [0, 3, 6, 10],
        }

        if quality not in intervals:
            raise ValueError(f"Invalid chord quality: {quality}")

        base_intervals = intervals[quality]
        notes = []
        for interval in base_intervals:
            # Create a new note at the specified interval
            midi_num = root.midi_number + interval
            new_note = Note.from_midi(midi_number=midi_num)
            notes.append(Note(midi_number=midi_num, name=new_note.name, octave=new_note.octave, accidental=new_note.accidental))

        # Apply inversion if specified
        if inversion > 0:
            for i in range(inversion):
                if i < len(notes):
                    notes[i] = Note(
                        name=notes[i].name,
                        octave=notes[i].octave + 1,
                        midi_number=notes[i].midi_number + 12,
                        accidental=notes[i].accidental
                    )

        logger.debug(f"Exiting generate_chord_notes method with notes: {notes}")
        return notes


    def transpose(self, interval: int) -> None:
        """Transpose the chord by a given interval in semitones."""
        if self.root:
            new_midi_number = self.root.midi_number + interval
            self.root = Note.from_midi(midi_number=new_midi_number)  # Update root note
            self.notes = self.generate_chord_notes(self.root, self.quality, self.inversion)  # Regenerate chord notes

    @classmethod
    def from_quality(cls, root: Note, quality: ChordQualityType | str) -> 'Chord':
        """Create a chord from a root note and quality."""
        if isinstance(quality, str):
            try:
                quality = ChordQualityType(quality)
            except ValueError:
                raise ValueError("Input should be 'major', 'minor', 'diminished', 'augmented'")

        logger.debug(f"Creating chord with root: {root}, quality: {quality}")
        logger.debug(f"Quality being passed: {quality}")
        chord = cls(root=root, quality=quality)
        chord.notes = chord.generate_chord_notes(chord.root, chord.quality, 0)  # Generate chord notes
        return chord

    def __str__(self) -> str:
        return f"Chord(root={self.root.name} in octave {self.root.octave}, quality={self.quality})"

# Configure logging to output to console
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)