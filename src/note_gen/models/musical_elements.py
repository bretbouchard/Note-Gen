# src/note_gen/models/musical_elements.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.note_gen.models.enums import AccidentalType, ChordQualityType
from src.note_gen.models.note import Note


__all__ = ['Note', 'ChordQuality', 'Chord']


class ChordQuality(BaseModel):
    """Model for chord quality."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    quality_type: ChordQualityType = Field(default=ChordQualityType.MAJOR)
    has_seventh: bool = Field(default=False)
    has_ninth: bool = Field(default=False)
    has_eleventh: bool = Field(default=False)
    is_diminished: bool = Field(default=False)
    is_augmented: bool = Field(default=False)

    @classmethod
    def from_str(cls, quality_str: str) -> "ChordQuality":
        """Create a ChordQuality from a string."""
        quality_map = {
            'major': ChordQualityType.MAJOR,
            'minor': ChordQualityType.MINOR,
            'diminished': ChordQualityType.DIMINISHED,
            'augmented': ChordQualityType.AUGMENTED,
            'dominant': ChordQualityType.DOMINANT,
            'dominant7': ChordQualityType.DOMINANT_7,
            'major7': ChordQualityType.MAJOR_7,
            'minor7': ChordQualityType.MINOR_7,
            'diminished7': ChordQualityType.DIMINISHED_7,
            'half_diminished7': ChordQualityType.HALF_DIMINISHED_7,
            'major_seventh': ChordQualityType.MAJOR_SEVENTH,
            'minor_seventh': ChordQualityType.MINOR_SEVENTH,
            'diminished_seventh': ChordQualityType.DIMINISHED_SEVENTH,
        }
        quality_type = quality_map.get(quality_str.lower(), ChordQualityType.MAJOR)
        return cls(quality_type=quality_type)


class Chord(BaseModel):
    """Model for a musical chord."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Note
    quality: ChordQualityType = Field(default=ChordQualityType.MAJOR)
    notes: List[Note] = Field(default_factory=list)
    inversion: int = Field(default=0)

    QUALITY_INTERVALS: Dict[ChordQualityType, List[int]] = {
        ChordQualityType.MAJOR: [0, 4, 7],
        ChordQualityType.MINOR: [0, 3, 7],
        ChordQualityType.DIMINISHED: [0, 3, 6],
        ChordQualityType.AUGMENTED: [0, 4, 8],
        ChordQualityType.DOMINANT: [0, 4, 7, 10],
        ChordQualityType.MAJOR_7: [0, 4, 7, 11],
        ChordQualityType.MINOR_7: [0, 3, 7, 10],
    }



    def __init__(self, **data: Any) -> None:
        """Initialize chord and generate notes."""
        super().__init__(**data)
        if not self.notes:
            self.notes = self.generate_chord_notes()


    def _generate_notes(self) -> List[Note]:
        """Generate the notes of the chord based on quality and inversion."""
        intervals = self.QUALITY_INTERVALS[self.quality]
        base_midi = self.root.midi_number
        notes = []
        
        # Generate notes based on intervals
        for interval in intervals:
            note_midi = base_midi + interval
            notes.append(Note(midi_number=note_midi))
            
        # Apply inversion if specified
        for _ in range(self.inversion):
            first_note = notes.pop(0)
            first_note.midi_number += 12  # Move up an octave
            notes.append(first_note)
            
        return notes

    @classmethod
    def from_quality(cls, root: Note, quality: str) -> "Chord":
        """Create a chord from a root note and quality."""
        try:
            quality = ChordQualityType(quality)
        except ValueError:
            raise ValueError("Input should be 'major', 'minor', 'diminished', 'augmented', 'dominant', 'major7', or 'minor7'")
        return cls(root=root, quality=quality)

    def generate_chord_notes(self) -> List[Note]:
        """Generate the notes of the chord based on quality and inversion."""
        intervals = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
        }

        base_intervals = intervals.get(self.quality, intervals[ChordQualityType.MAJOR])
        notes = []
        for interval in base_intervals:
            note = Note(
                midi_number=self.root.midi_number + interval,
                velocity=self.root.velocity,
                duration=self.root.duration
            )
            notes.append(note)

        # Apply inversion
        if self.inversion > 0:
            for _ in range(self.inversion):
                first = notes.pop(0)
                first = Note(
                    midi_number=first.midi_number + 12,
                    velocity=first.velocity,
                    duration=first.duration
                )
                notes.append(first)

        return notes

