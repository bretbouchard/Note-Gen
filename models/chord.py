"""Module for handling chords."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, AbstractSet
from pydantic import BaseModel, Field, model_validator
from typing import Mapping

from .scale import Scale, ScaleInfo
from .roman_numeral import RomanNumeral
from .chord_base import CHORD_SYMBOLS, CHORD_INTERVALS
from .note import Note

# Define intervals for each chord quality
# CHORD_INTERVALS is now imported from chord_base.py

class Chord(BaseModel):
    """A class for representing musical chords."""
    chord_notes: List[Note]
    duration: Optional[float] = None
    velocity: Optional[int] = None
    root: Note
    bass: Note
    quality: str = Field(default="major")
    inversion: int = Field(default=0)
    notes_list: Optional[List[Note]] = Field(default=None, alias="notes")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.notes_list is None:
            self._generate_notes()

    def _generate_notes(self) -> None:
        """Generate the notes for this chord based on its quality and inversion."""
        intervals = CHORD_INTERVALS.get(self.quality, [])
        if not intervals:
            raise ValueError(f"Unknown chord quality: {self.quality}")

        # Generate notes based on intervals
        base_note = self.root.midi_number
        self.notes_list = [Note(midi_number=base_note + interval) for interval in intervals]

        # Apply inversion if needed
        if self.inversion > 0:
            for _ in range(self.inversion):
                first_note = self.notes_list.pop(0)
                self.notes_list.append(Note(midi_number=first_note.midi_number + 12))

    @property
    def notes(self) -> List[Note]:
        """Get the notes in this chord."""
        return self.notes_list

    @notes.setter
    def notes(self, value: List[Note]) -> None:
        """Set the notes in this chord."""
        self.notes_list = value

    def get_notes(self) -> List[Note]:
        """Get the notes in this chord."""
        return self.notes

    @classmethod
    def from_roman_numeral(cls, numeral_str: str, scale: Union[Scale, ScaleInfo]) -> 'Chord':
        """Create a chord from a Roman numeral."""
        roman = RomanNumeral.from_str(numeral_str, scale)
        root = roman.get_note()
        quality = roman.chord_quality
        
        return cls(
            root=root,
            quality=quality,
            inversion=roman.inversion
        )

    @classmethod
    def from_root(cls, root: Note, quality: str = "major") -> Chord:
        """Create a chord from a root note and quality."""
        return cls(root=root, quality=quality)

    def to_note(self) -> Note:
        """Convert to a Note object."""
        return self.root

    @property
    def bass_note(self) -> Note:
        """Get the lowest note of the chord (considering inversions)."""
        notes = self.notes
        if not notes:
            raise ValueError("No notes in chord")
        return notes[0]

    @property
    def intervals(self) -> List[int]:
        """Get the intervals between adjacent notes in the chord."""
        notes = self.notes
        if not notes:
            return []
        return [
            notes[i + 1].midi_number - notes[i].midi_number
            for i in range(len(notes) - 1)
        ]

    def __sub__(self, other: Union['Chord', int]) -> int:
        """Get the interval between two chords or transpose down."""
        if isinstance(other, int):
            return int(self.root.midi_number - other)
        return int(self.root.midi_number - other.root.midi_number)

    def __lt__(self, other: 'Chord') -> bool:
        """Compare two chords based on their root notes."""
        return int(self.root.midi_number) < int(other.root.midi_number)

    def __gt__(self, other: 'Chord') -> bool:
        """Compare two chords based on their root notes."""
        return int(self.root.midi_number) > int(other.root.midi_number)

    def __eq__(self, other: object) -> bool:
        """Compare chords for equality."""
        if not isinstance(other, Chord):
            return NotImplemented
        return self.root.midi_number == other.root.midi_number and self.quality == other.quality

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = super().dict(**kwargs)
        if isinstance(d, dict):
            d['notes'] = [note.__dict__ for note in self.notes]
        return d

    def transpose(self, semitones: int) -> 'Chord':
        """Transpose the chord by the given number of semitones."""
        new_root = Note(midi_number=self.root.midi_number + semitones)
        new_notes = [Note(midi_number=note.midi_number + semitones) for note in self.notes]
        return Chord(
            root=new_root,
            quality=self.quality,
            inversion=self.inversion,
            notes=new_notes
        )

    def model_copy(self, *, include: Optional[AbstractSet[Union[int, str]]] = None,
                exclude: Optional[AbstractSet[Union[int, str]]] = None,
                update: Optional[Dict[str, Any]] = None,
                deep: bool = False) -> 'Chord':
        """Create a copy of the chord."""
        new_notes = [Note(midi_number=note.midi_number) for note in self.notes]
        return Chord(
            root=Note(midi_number=self.root.midi_number),
            quality=self.quality,
            inversion=self.inversion,
            notes=new_notes
        )

    def copy(
        self,
        *,
        include: AbstractSet[int] | AbstractSet[str] | Mapping[int, Any] | Mapping[str, Any] | None = None,
        exclude: AbstractSet[int] | AbstractSet[str] | Mapping[int, Any] | Mapping[str, Any] | None = None,
        update: dict[str, Any] | None = None,
        deep: bool = False
    ) -> 'Chord':
        return super().copy(include=include, exclude=exclude, update=update, deep=deep)

    def is_inversion(self) -> bool:
        return self.root.midi_number != self.bass.midi_number
