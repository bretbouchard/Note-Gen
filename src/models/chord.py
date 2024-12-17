from __future__ import annotations

"""Module for defining chords in music theory.

This module provides classes and functions for representing musical chords, including their structure, qualities, and relationships to scales."""

import logging
from typing import TypeAlias, Literal, Any, Dict, List, Optional, Union, AbstractSet, Mapping
from typing_extensions import NotRequired
from pydantic import BaseModel, ConfigDict, Field, field_validator


from .chord_base import CHORD_INTERVALS, CHORD_COUNT  # Ensure CHORD_COUNT is imported
from .note import Note  # Ensure Note is imported
from .chord_quality import ChordQuality  # Import ChordQuality from chord_quality.py
from models.chord_roman_utils import get_chord_from_roman_numeral  # Updated import

# Define Literal types for warnings and modes
Modes: TypeAlias = Literal['json', 'python']
Warnings: TypeAlias = Literal['none', 'warn', 'error']

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chord(BaseModel):
    """Class representing a musical chord.

    This class encapsulates the properties of a chord, including its root, quality, and any alterations.

    Attributes:
        root (Note): The root note of the chord.
        quality (ChordQuality): The quality of the chord.
        bass (Optional[Note]): The bass note of the chord.
        chord_notes (List[Note]): The notes of the chord.
        duration (Optional[float]): The duration of the chord.
        velocity (Optional[int]): The velocity of the chord.
        inversion (int): The inversion of the chord.
        notes_list (Optional[List[Note]]): The list of notes in the chord.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Optional[Note] = None
    quality: Optional[ChordQuality] = None  # Allow None for quality
    bass: Optional[Note]
    chord_notes: List[Note]
    duration: Optional[float] = None
    velocity: Optional[int] = None
    inversion: int = Field(default=0)
    notes_list: Optional[List[Note]] = Field(default=None, alias="notes")

    @field_validator('quality')
    @classmethod
    def validate_quality(cls, value: Union[ChordQuality, str, None]) -> Optional[ChordQuality]:
        """Validate chord quality. Must be a valid chord quality."""
        logger.debug(f"Validating chord quality: {value} (type: {type(value)})")
        if isinstance(value, str):
            try:
                value = ChordQuality(value)
            except ValueError:
                logger.error(f"Invalid chord quality: {value}. Must be one of: {', '.join(ChordQuality.__members__.keys())}.")
                raise ValueError(f"Invalid chord quality: {value}. Must be one of: {', '.join(ChordQuality.__members__.keys())}.")
        return value
 
    @field_validator('root')
    @classmethod
    def validate_root(cls, value: Optional[Note]) -> Optional[Note]:
        logger.debug('Validating root')
        if value is not None and not isinstance(value, Note):
            logger.error('Root must be a valid Note instance or None.')
            raise ValueError('Root must be a valid Note instance or None.')
        return value

    @field_validator('bass')
    @classmethod
    def validate_bass(cls, value: Optional[Note]) -> Optional[Note]:
        logger.debug('Validating bass')
        if value is not None and not isinstance(value, Note):
            logger.error('Bass must be a valid Note instance or None.')
            raise ValueError('Bass must be a valid Note instance or None.')
        return value

    @field_validator('chord_notes')
    @classmethod
    def validate_chord_notes(cls, value: List[Note]) -> List[Note]:
        logger.debug('Validating chord notes')
        if not all(isinstance(note, Note) for note in value):
            logger.error('All chord notes must be valid Note instances.')
            raise ValueError('All chord notes must be valid Note instances.')
        return value

    @field_validator('notes', check_fields=False)
    def validate_notes(cls, value: List[Note]) -> List[Note]:
        logger.debug('Validating notes')
        if not value:
            raise ValueError('Notes list cannot be empty.')
        return value

    @field_validator('inversion')
    @classmethod
    def validate_inversion(cls, value: int) -> int:
        logger.debug('Validating inversion')
        if value < 0:
            logger.error('Inversion must be a non-negative integer.')
            raise ValueError('Inversion must be a non-negative integer.')
        return value

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, value: Optional[float]) -> Optional[float]:
        logger.debug('Validating duration')
        if value is not None and value < 0:
            logger.error('Duration must be a non-negative float.')
            raise ValueError('Duration must be a non-negative float.')
        return value

    def __init__(self, root: Optional[Note], quality: Optional[ChordQuality], notes: List[Note], bass: Optional[Note] = None, inversion: int = 0) -> None:
        logger.debug(f"Initializing chord with data: {{root: {root}, quality: {quality}, notes: {notes}, bass: {bass}, inversion: {inversion}}}")
        if root is not None:
            self.root = self.validate_root(root)
        else:
            self.root = None
        self.quality = self.validate_quality(quality)  # Validate quality
        self.chord_notes = [note for note in notes if note is not None]  # Filter out None values
        if not self.chord_notes:
            logger.error("Chord notes cannot be empty")
            raise ValueError("Chord notes cannot be empty")
        self.bass = self.validate_bass(bass) if bass is not None else None
        self.inversion = inversion  # Ensure inversion is properly initialized
        self._initialize_bass(self.bass)  # Call to initialize bass
        self._initialize_chord_notes(self.root, self.quality, self.inversion)  # Initialize chord notes

    def _validate_root(self, root: Optional[Note]) -> None:
        """Validate the root note in the chord data."""
        logger.debug(f"Validating root note: {root}")
        if root is None:
            logger.error("Root note is required for chord validation.")
            raise ValueError("Root note is required for chord validation.")
        logger.info(f"Root note validated: {root}")

    def _initialize_chord_notes(self, root: Optional[Note], quality: Optional[ChordQuality], inversion: int) -> None:
        """Initialize chord notes based on root and quality."""
        logger.debug(f"Initializing chord notes with data: {{root: {root}, quality: {quality}, inversion: {inversion}}}")
        if root is not None:
            self.chord_notes = self.generate_chord_notes(root, quality, inversion)
            logger.info(f"Chord notes initialized: {self.chord_notes}")

    def _initialize_bass(self, bass: Optional[Note]) -> None:
        """Initialize the bass note for the chord."""
        logger.debug(f"Initializing bass from data: {bass}")
        if bass:
            self.bass = bass
            logger.info(f"Bass initialized: {self.bass}")
        else:
            logger.warning("Bass note not provided, defaulting to None.")

    def generate_chord_notes(self, root: Note, quality: Optional[ChordQuality], inversion: int) -> List[Note]:
        """Generate the notes for this chord based on its quality and inversion."""
        logger.debug(f"Generating chord notes for root: {root}, quality: {quality}, inversion: {inversion}")
        if quality is None:
            logger.error("Quality must not be None")
            raise ValueError("Quality must not be None")
        intervals = CHORD_INTERVALS.get(quality, [])  # Ensure dictionary access is correctly typed
        expected_count = CHORD_COUNT.get(quality, len(intervals))  # Adjusted to use quality directly
        if not intervals:
            logger.error(f"Invalid chord quality: {quality}")
            raise ValueError(f"Invalid chord quality: {quality}")

        logger.debug(f"Root note MIDI number: {root.midi_number}")
        logger.debug(f"Intervals for quality '{quality}': {intervals}")

        notes_list = []  # Start with an empty list for notes
        logger.debug(f"Using intervals for quality '{quality}': {intervals}")

        for interval in intervals:
            note = self._create_note_from_interval(root, interval)
            if note:
                notes_list.append(note)
                logger.info(f"Generated note: {note} for interval: {interval}")
            else:
                logger.warning(f"Failed to create note for interval {interval}.")

        logger.debug(f"Expected {expected_count} notes for {quality} chord, generated {len(notes_list)}.")

        # Apply inversion if needed
        if inversion > 0:
            notes_list = self._apply_inversion(notes_list, inversion)

        logger.debug(f"Final notes generated: {[note.note_name for note in notes_list]}")
        return notes_list

    def _create_note_from_interval(self, root: Note, interval: int) -> Optional[Note]:
        """Create a note from the root and interval."""
        logger.debug(f"Creating note from root: {root} with interval: {interval}")
        midi_number = root.midi_number + interval
        logger.debug(f"Creating note with MIDI number: {midi_number}")
        note = Note.from_midi(midi_number)
        logger.info(f"Created note: {note.note_name} from root: {root} with interval: {interval}")
        return note

    def _apply_inversion(self, notes_list: List[Note], inversion: int) -> List[Note]:
        """Apply inversion to the given chord notes."""
        logger.debug(f"Applying inversion: {inversion} to notes: {notes_list}")
        inversion_index = inversion - 1
        if inversion_index < len(notes_list):
            return notes_list[inversion_index:] + notes_list[:inversion_index]  # Rotate notes for inversion
        logger.error(f"Invalid inversion index: {inversion}")
        raise ValueError(f"Invalid inversion index: {inversion}")

    def some_method(self) -> None:
        logger.debug("some_method called")
        if self.root:
            midi_num = self.root.midi_number  # Access midi_number correctly

    def another_method(self) -> List[Note]:
        logger.debug("another_method called")
        return [note for note in self.chord_notes if note is not None]  # Ensure no None values are returned

    def get_notes(self) -> List[Note]:
        """Get the notes in this chord."""
        logger.debug("get_notes called")
        return self.chord_notes

    @property
    def notes(self) -> List[Note]:
        """Get the notes in this chord."""
        logger.debug("notes property accessed")
        return self.chord_notes

    @notes.setter
    def notes(self, value: List[Note]) -> None:
        """Set the notes in this chord."""
        logger.debug("notes setter called")
        if isinstance(value, list) and any(note is None for note in value):
            logger.error("Chord notes cannot contain None values")
            raise ValueError("Chord notes cannot contain None values")
        self.chord_notes = value

    @classmethod
    def from_roman_numeral(cls, roman_numeral: str) -> Chord:
        """Create a chord from a Roman numeral."""
        if roman_numeral is None:
            raise ValueError("Roman numeral cannot be None when creating a chord.")
        
        logger.debug(f"Creating chord from Roman numeral: {roman_numeral}")
        return get_chord_from_roman_numeral(roman_numeral)

    @classmethod
    def from_root(cls, root: Note, quality: Union[ChordQuality, str] = ChordQuality.major) -> Chord:
        """Create a chord from a root note and quality."""
        logger.debug(f"Creating chord from root: {root} and quality: {quality}")
        if root is None:
            logger.error("Root cannot be None")
            raise ValueError("Root cannot be None")
        if isinstance(quality, str):
            quality = ChordQuality(quality)  # Convert string to ChordQuality
        return cls(root=root, quality=quality, notes=[])

    def to_note(self) -> Note:
        """Convert to a Note object."""
        logger.debug("to_note called")
        if self.root is None:
            logger.error("Generated note is None")
            raise ValueError("Generated note cannot be None")   
        note = self.root
        if note is None:
            logger.error("Generated note is None")
            raise ValueError("Generated note cannot be None")
        return note

    @property
    def bass_note(self) -> Note:
        """Get the lowest note of the chord (considering inversions)."""
        logger.debug("bass_note property accessed")
        notes = self.chord_notes
        if not notes:
            logger.error("No notes in chord")
            raise ValueError("No notes in chord")
        if notes[0] is None:
            logger.error("Bass note is None")
            raise ValueError("Bass note cannot be None")
        return notes[0]

    @property
    def intervals(self) -> List[int]:
        """Get the intervals between adjacent notes in the chord."""
        logger.debug("intervals property accessed")
        notes = self.chord_notes
        if not notes:
            return []
        if any(note is None for note in notes):
            logger.error("Notes in chord cannot be None")
            raise ValueError("Notes in chord cannot be None")
        return [
            notes[i + 1].midi_number - notes[i].midi_number
            for i in range(len(notes) - 1)
        ]

    def __sub__(self, other: Union['Chord', int]) -> int:
        """Get the interval between two chords or transpose down."""
        logger.debug(f"__sub__ called with other: {other}")
        if isinstance(other, int):
            if self.root is None:
                logger.error("Root note is None")
                raise ValueError("Root note cannot be None")
            return int(self.root.midi_number - other)
        if self.root is None or other.root is None:
            logger.error("Root note is None")
            raise ValueError("Root note cannot be None")
        return int(self.root.midi_number - other.root.midi_number)

    def __lt__(self, other: 'Chord') -> bool:
        """Compare two chords based on their root notes."""
        logger.debug(f"__lt__ called with other: {other}")
        if self.root is None or other.root is None:
            logger.error("Root note is None")
            raise ValueError("Root note cannot be None")
        return int(self.root.midi_number) < int(other.root.midi_number)

    def __gt__(self, other: 'Chord') -> bool:
        """Compare two chords based on their root notes."""
        logger.debug(f"__gt__ called with other: {other}")
        if self.root is None or other.root is None:
            logger.error("Root note is None")
            raise ValueError("Root note cannot be None")
        return int(self.root.midi_number) > int(other.root.midi_number)

    def __eq__(self, other: object) -> bool:
        """Compare chords for equality."""
        logger.debug(f"__eq__ called with other: {other}")
        if not isinstance(other, Chord):
            return NotImplemented
        if self.root is None or other.root is None:
            logger.error("Root note is None")
            raise ValueError("Root note cannot be None")
        return self.root.midi_number == other.root.midi_number and self.quality == other.quality

    def transpose(self, semitones: int) -> 'Chord':
        """Transpose the chord by the given number of semitones."""
        logger.debug(f"transpose called with semitones: {semitones}")
        if self.root is None:
            logger.error("Root note is None")
            raise ValueError("Root note cannot be None")
        new_root = Note.from_midi(self.root.midi_number + semitones)
        new_notes = [Note.from_midi(note.midi_number + semitones) for note in self.chord_notes]
        return Chord(
            root=new_root,
            quality=self.quality,
            inversion=self.inversion,
            notes=new_notes
        )

    def get_chord_notes(self, quality: ChordQuality) -> List[Note]:
        """Get the chord notes for the given quality."""
        logger.debug(f"get_chord_notes called with quality: {quality}")
        # Return all chord notes without filtering by quality
        return self.chord_notes

    # Update the model_dump method signature
 
    def model_dump(
        self,
        *,
        mode: Literal['json', 'python'] | str = 'json',
        include: Any | None = None,
        exclude: Any | None = None,
        context: Any | None = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: Literal['none', 'warn', 'error'] | bool = 'warn',
        serialize_as_any: bool = False
    ) -> Dict[str, Any]:
        """Dump the model to a dictionary."""
        logger.debug("model_dump called")
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any
        )

            
    def dict(self, *, include: Optional[Any] = None, exclude: Optional[Any] = None, by_alias: bool = True, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False) -> dict[str, Any]:
        """Return a dictionary representation of the model."""
        logger.debug("dict called")
        return super().dict(include=include, exclude=exclude, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none)

    def copy(self, *, deep: bool = False, **kwargs: Any) -> Chord:
        """Create a copy of the model."""
        logger.debug("copy called")
        return super().copy(deep=deep, **kwargs)

    def model_copy(self, *, update: Optional[Mapping[str | ChordQuality, Any]] = None, deep: bool = False) -> 'Chord':
        """Create a copy of the chord."""
        logger.debug("model_copy called")
        if self.root is not None:
            root = Note.from_midi(self.root.midi_number)
        else:
            root = None
        new_notes = [Note.from_midi(note.midi_number) for note in self.chord_notes]
        return Chord(
            root=root,
            quality=ChordQuality(self.quality) if isinstance(self.quality, str) else self.quality,
            inversion=self.inversion,
            notes=new_notes
        )

    def is_inversion(self) -> bool:
        logger.debug("is_inversion called")
        if self.root is None or self.bass is None:
            logger.error("Root or bass note is None")
            raise ValueError("Root or bass note cannot be None")
        return self.root.midi_number != self.bass.midi_number

    def get_scale(self, root_note: Note) -> List[Note]:
        logger.debug(f"get_scale called with root_note: {root_note}")
        logger.debug(f"Root note passed to get_scale: {root_note.note_name_octave()}")  # Corrected debugging output
        root = root_note.note_name_octave()  # Use note_name_octave to include octave
        logger.debug(f"Root note passed to get_scale: {root}")  # Debugging output
        intervals = [0, 2, 4, 5, 7, 9, 11]
        note_from_str = Note.from_str(root)
        logger.debug(f"Output of Note.from_str('{root}'): {Note.from_str(root)}")  # Log the output of Note.from_str
        logger.debug(f"Note created from string '{root}': {note_from_str}")  # Log the created note
        scale_notes = [Note.from_midi(note_from_str.midi_number + interval) for interval in intervals]
        logger.debug(f"Generated scale notes for {root}: {[note.note_name for note in scale_notes]}")  # Log generated scale notes
        return scale_notes

# Example instantiation for testing