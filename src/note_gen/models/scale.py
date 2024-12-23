"""
Module for handling musical scales.
"""
from __future__ import annotations
import logging
from typing import List, Optional, Dict, Any, ClassVar, TYPE_CHECKING, Tuple
from pydantic import BaseModel, ConfigDict

from src.note_gen.models.base_types import MusicalBase
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.note import Note  # Moved import to the top of the file to avoid NameError

if TYPE_CHECKING:
    from src.note_gen.models.chord import Chord

logger = logging.getLogger(__name__)

class Scale(BaseModel):
    """A musical scale."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    root: Note
    quality: str
    scale_degree: int
    notes: List[Note] = []
    numeral: str
    scale_degrees: List[ScaleDegree] = []
    scale_info_v2: Optional[ScaleInfo] = None

    # Consolidated scale patterns for different keys
    SCALE_PATTERNS: ClassVar[Dict[str, Dict[str, List[Tuple[str, str]]]]] = {
        "major": {
            "C": [("C",""), ("D",""), ("E",""), ("F",""), ("G",""), ("A",""), ("B","")],
            "G": [("G",""), ("A",""), ("B",""), ("C",""), ("D",""), ("E",""), ("F","#")],
            "D": [("D",""), ("E",""), ("F","#"), ("G",""), ("A",""), ("B",""), ("C","#")],
            "A": [("A",""), ("B",""), ("C","#"), ("D",""), ("E",""), ("F","#"), ("G","#")],
            "E": [("E",""), ("F","#"), ("G","#"), ("A",""), ("B",""), ("C","#"), ("D","#")],
            "B": [("B",""), ("C","#"), ("D","#"), ("E",""), ("F","#"), ("G","#"), ("A","#")],
            "F#": [("F","#"), ("G","#"), ("A","#"), ("B",""), ("C","#"), ("D","#"), ("E","#")],
            "C#": [("C","#"), ("D","#"), ("E",""), ("F","#"), ("G","#"), ("A","#"), ("B","#")],
            "G#": [("G","#"), ("A","#"), ("B",""), ("C","#"), ("D","#"), ("E","#"), ("F","##")],
            "F": [("F",""), ("G",""), ("A",""), ("B","b"), ("C",""), ("D",""), ("E","")],
            "Bb": [("B","b"), ("C",""), ("D",""), ("E","b"), ("F",""), ("G",""), ("A","")],
            "Eb": [("E","b"), ("F",""), ("G",""), ("A","b"), ("B","b"), ("C",""), ("D","")],
            "Ab": [("A","b"), ("B","b"), ("C",""), ("D","b"), ("E","b"), ("F",""), ("G","")],
            "Db": [("D","b"), ("E","b"), ("F",""), ("G","b"), ("A","b"), ("B","b"), ("C","")],
            "Gb": [("G","b"), ("A","b"), ("B","b"), ("C","b"), ("D","b"), ("E","b"), ("F","")],
        },
        "minor": {
            "C": [("C",""), ("D",""), ("E","b"), ("F",""), ("G",""), ("A","b"), ("B","b")],
            "G": [("G",""), ("A",""), ("B","b"), ("C",""), ("D",""), ("E","b"), ("F","")],
            "D": [("D",""), ("E",""), ("F",""), ("G",""), ("A",""), ("B","b"), ("C","")],
            "A": [("A",""), ("B",""), ("C",""), ("D",""), ("E",""), ("F",""), ("G","")],
            "E": [("E",""), ("F","#"), ("G",""), ("A",""), ("B",""), ("C",""), ("D","")],
            "B": [("B",""), ("C","#"), ("D",""), ("E",""), ("F","#"), ("G",""), ("A","")],
            "F#": [("F","#"), ("G","#"), ("A",""), ("B",""), ("C","#"), ("D",""), ("E","")],
            "C#": [("C","#"), ("D","#"), ("E",""), ("F","#"), ("G","#"), ("A",""), ("B","")],
            "Bb": [("B","b"), ("C",""), ("D","b"), ("E","b"), ("F",""), ("G","b"), ("A","b")],
            "Eb": [("E","b"), ("F",""), ("G","b"), ("A","b"), ("B","b"), ("C","b"), ("D","b")]
        },
        # Additional scale patterns...
    }

    SCALE_INTERVALS: ClassVar[Dict[str, List[int]]] = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
        "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "locrian": [0, 1, 3, 5, 6, 8, 10],
        "whole_tone": [0, 2, 4, 6, 8, 10],
        "diminished": [0, 2, 3, 5, 6, 8, 9, 11],
        "augmented": [0, 3, 4, 7, 8, 11],
        "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    }

    is_major: bool
    is_diminished: bool
    is_augmented: bool
    is_half_diminished: bool
    has_seventh: bool
    has_ninth: bool
    has_eleventh: bool
    inversion: int

    def __init__(self, scale: ScaleInfo, numeral: str, numeral_str: str, scale_degree: int, quality: str, is_major: bool,
                 is_diminished: bool, is_augmented: bool, is_half_diminished: bool,
                 has_seventh: bool, has_ninth: bool, has_eleventh: bool, inversion: int):
        # Ensure proper initialization
        if scale is None:
            raise ValueError("Scale cannot be None. Please provide a valid Scale object.")
        if numeral is None:
            raise ValueError("Numeral cannot be None. Please provide a valid numeral.")
        if numeral_str is None:
            raise ValueError("Numeral string cannot be None. Please provide a valid numeral string.")
        if scale_degree is None:
            raise ValueError("Scale degree cannot be None. Please provide a valid scale degree.")

        # Validate ScaleInfo fields
        if not isinstance(scale, ScaleInfo):
            raise ValueError("Invalid scale type. Expected ScaleInfo.")
        if scale.root is None:
            raise ValueError("ScaleInfo must have a valid root note.")
        if len(scale.scale_degrees) == 0:
            raise ValueError("ScaleInfo must have at least one scale degree.")


        super().__init__(root=scale.root, quality=quality, notes=[], scale_degrees=[], scale_info_v2=scale, numeral=numeral,
                         is_major=is_major, is_diminished=is_diminished, is_augmented=is_augmented, is_half_diminished=is_half_diminished,
                         has_seventh=has_seventh, has_ninth=has_ninth, has_eleventh=has_eleventh, inversion=inversion, scale_degree=scale_degree)  # Ensure all required fields are passed
        self.root = scale.root  # Add this line to initialize the root field
        self.numeral = numeral
        self.is_major = is_major
        self.is_diminished = is_diminished
        self.is_augmented = is_augmented
        self.is_half_diminished = is_half_diminished
        self.has_seventh = has_seventh
        self.has_ninth = has_ninth
        self.has_eleventh = has_eleventh
        self.inversion = inversion
        self.notes = self._build_scale_from_intervals()
        self.scale_degrees = self._get_scale_degrees()
        logging.debug(f"Initializing Scale with: scale={scale}, numeral={numeral}, numeral_str={numeral_str}, scale_degree={scale_degree}, quality={quality}, is_major={is_major}, is_diminished={is_diminished}, is_augmented={is_augmented}, is_half_diminished={is_half_diminished}, has_seventh={has_seventh}, has_ninth={has_ninth}, has_eleventh={has_eleventh}, inversion={inversion}")

    def _validate_quality(self, quality: str) -> None:
        """Validate the quality of the scale. Must be one of the valid scale types."""
        valid_qualities = ['major', 'minor', 'harmonic_minor', 'melodic_minor']
        if quality not in valid_qualities:
            logger.error(f"Invalid scale quality: {quality}. Must be one of {valid_qualities}.")
            raise ValueError(f"Invalid scale quality: {quality}. Must be one of {valid_qualities}.")
        logger.info(f"Scale quality validated: {quality}")

    def _build_scale_from_intervals(self) -> List[Note]:
        """Build a scale from intervals based on the quality and root note."""
        logger.info(f"Building scale from intervals for quality: {self.quality}")
        intervals = self.SCALE_INTERVALS[self.quality]
        logger.debug(f"Intervals used for scale: {intervals}")
        
        scale_notes = [self.root]  # Start with the root note
        base_midi = self.root.midi_number  # Use root note as reference
        
        for interval in intervals[1:]:  # Skip first interval (0)
            next_midi = base_midi + interval  # Calculate from root
            next_note = self._get_next_note(next_midi)
            logger.debug(f"Next note calculated: {next_note.note_name} with MIDI number: {next_midi}")
            scale_notes.append(next_note)
            
        return scale_notes
    
    def _get_next_note(self, midi_number: int) -> Note:
        """Create a note from a MIDI number."""
        logger.debug(f"Creating note from MIDI number: {midi_number}")
        
        # Ensure MIDI number is in valid range
        midi_number = midi_number % 128
        
        # Get note name and octave
        note_name = Note.get_note_name(midi_number)
        octave = midi_number // 12
        
        # If note name includes octave, separate it
        if note_name[-1].isdigit():
            note_name = note_name[:-1]
        
        return Note(name=note_name, octave=octave)

    def get_notes(self) -> List[Note]:
        """Get the notes in this scale."""
        logger.debug("Retrieving notes from the scale.")
        return self.notes

    # Additional methods for building scales and retrieving scale degrees...
    def _get_scale_degrees(self) -> List[ScaleDegree]:
        """Retrieve the scale degrees for the scale."""
        logger.debug(f"Getting scale degrees for scale: {self.quality}")
        scale_degrees: List[ScaleDegree] = []
        for i, note in enumerate(self.notes, start=1):
            scale_degrees.append(ScaleDegree(
                degree=i,
                note=note,
                scale=self.quality  # Pass a string representation of the scale
            ))
        return scale_degrees

    def get_scale_notes(self) -> List[Note]:
        """Get the notes in this scale."""
        logger.info("Retrieving scale notes.")
        notes = self._build_scale_from_intervals()
        logger.debug(f"Scale notes retrieved: {[note.note_name for note in notes]}")
        return notes

    def get_scale_degrees(self) -> List[ScaleDegree]:
        """Get the scale degrees in this scale."""
        logger.debug("Getting scale degrees")
        return self.scale_degrees[:]

    def get_scale_degree(self, degree: int) -> Note:
        """Get the note at a specific scale degree (1-based indexing)."""
        logger.debug(f"Getting scale degree: {degree}")
        if degree < 1:
            raise ValueError("Scale degree must be positive")
        scale_notes = self.get_scale_notes()
        index = (degree - 1) % len(scale_notes)
        return scale_notes[index]

    def get_note_from_scale_degree(self, scale_degree: int) -> Note:
        """Get a note from its scale degree."""
        logger.debug(f"Getting note from scale degree: {scale_degree}")
        if not (1 <= scale_degree <= len(self.notes)):
            raise ValueError(f"Invalid scale degree: {scale_degree}")
        return self.notes[scale_degree - 1]  # Convert to 0-based index

    def get_note_by_degree(self, degree: int) -> Optional[Note]:
        """Get the note at a specific scale degree (1-based indexing)."""
        logger.info(f"Retrieving note for degree: {degree}")
        if degree < 1 or degree > len(self.scale_degrees):
            logger.error(f"Invalid degree: {degree}. Must be between 1 and {len(self.scale_degrees)}.")
            raise ValueError(f"Invalid degree: {degree}. Must be between 1 and {len(self.scale_degrees)}.")
        note = self.scale_degrees[degree - 1].note
        if note is None:
            logger.error(f"Note at degree {degree} is None.")
            return None
        logger.debug(f"Note retrieved for degree {degree}: {note.note_name}")
        return note

    def _get_scale_degree_name(self, degree: int) -> str:
        """Get the name of the scale degree."""
        logger.debug(f"Getting scale degree name: {degree}")
        # Define the natural note sequence
        NATURAL_NOTES = ["C", "D", "E", "F", "G", "A", "B"]
        
        # Find the root note's position in the natural note sequence
        root_idx = NATURAL_NOTES.index(self.root.name)
        
        # Calculate the scale degree note
        degree_idx = (root_idx + degree) % 7
        return NATURAL_NOTES[degree_idx]

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Dump the Scale object to a dictionary."""
        logger.debug("Dumping Scale object to dictionary")
        d = super().model_dump(*args, **kwargs)
        d['root'] = self.root.name  # Include root note name
        d['scale_notes'] = [note.name for note in self.notes]  # Include scale notes
        return d

    @property
    def scale_type(self) -> str:
        """Return the type of scale."""
        return self.quality

    @property
    def notes_computed(self) -> List[Note]:
        """Get the notes in the scale."""
        logger.debug("Getting notes in the scale")
        return self.get_scale_notes()

    @property
    def scale_notes(self) -> List[Note]:
        """Get the notes of the scale."""
        logger.debug("Getting notes of the scale")
        return self.get_notes()

    @property
    def root_name(self) -> str:
        """Get the root note name as a string."""
        logger.debug("Getting root note name")
        if not hasattr(self.root, 'note_name'):
            return str(self.root)
        note_name = self.root.note_name
        return str(note_name) if note_name is not None else ""

    @property
    def quality_str(self) -> str:
        """Get the quality as a string."""
        logger.debug("Getting quality as string")
        return str(self.quality) if self.quality is not None else ""

    @property
    def scale_info(self) -> ScaleInfo:
        """Get the scale info."""
        logger.debug("Getting scale info")
        return ScaleInfo(root=self.root, scale_type=self.quality)

    def _get_scale_intervals(self) -> List[int]:
        """Get the intervals for the scale."""
        logger.debug("Getting intervals for the scale")
        return self.SCALE_INTERVALS.get(self.quality, [])

    def get_scale_degree_v2(self, degree: int) -> Note:
        """Get the note at a specific scale degree (1-based indexing)."""
        logger.debug(f"Getting scale degree: {degree}")
        if degree < 1:
            raise ValueError("Scale degree must be positive")
        
        scale_notes = self.get_scale_notes()
        index = (degree - 1) % len(scale_notes)
        return scale_notes[index]

    def get_note_from_scale_degree_v2(self, scale_degree: int) -> Note:
        """Get a note from its scale degree."""
        logger.debug(f"Getting note from scale degree: {scale_degree}")
        if not (1 <= scale_degree <= len(self.notes)):
            raise ValueError(f"Invalid scale degree: {scale_degree}")
        return self.notes[scale_degree - 1]  # Convert to 0-based index

    def _get_accidentals(self) -> Dict[str, List[Tuple[str, str]]]:
        """Get the accidentals for this scale."""
        logger.debug("Getting accidentals for the scale")
        accidental_map: Dict[str, List[Tuple[str, str]]] = {
            'C': [],
            'G': [('F', '#')],
            'D': [('F', '#'), ('C', '#')],
            'A': [('F', '#'), ('C', '#'), ('G', '#')],
            'E': [('F', '#'), ('C', '#'), ('G', '#'), ('D', '#')],
            'B': [('F', '#'), ('C', '#'), ('G', '#'), ('D', '#'), ('A', '#')],
            'F#': [('F', '#'), ('C', '#'), ('G', '#'), ('D', '#'), ('A', '#'), ('E', '#')],
            'C#': [('F', '#'), ('C', '#'), ('G', '#'), ('D', '#'), ('A', '#'), ('E', '#'), ('B', '#')],
            'F': [('B', 'b')],
            'Bb': [('B', 'b'), ('E', 'b')],
            'Eb': [('B', 'b'), ('E', 'b'), ('A', 'b')],
            'Ab': [('B', 'b'), ('E', 'b'), ('A', 'b'), ('D', 'b')],
            'Db': [('B', 'b'), ('E', 'b'), ('A', 'b'), ('D', 'b'), ('G', 'b')],
            'Gb': [('B', 'b'), ('E', 'b'), ('A', 'b'), ('D', 'b'), ('G', 'b'), ('C', 'b')],
            'Cb': [('B', 'b'), ('E', 'b'), ('A', 'b'), ('D', 'b'), ('G', 'b'), ('C', 'b'), ('F', 'b')]
        }
        return accidental_map

    def get_value(self) -> int:
        return 10

    def validate_accidental(self, note: Note) -> bool:
        """Validate if the accidental of a note is valid within the context of this scale."""
        logger = logging.getLogger(__name__)
        logger.info(f"Validating accidental for note: {note}")
        if note.accidental not in ['sharp', 'flat', 'natural']:
            logger.warning(f"Invalid accidental: {note.accidental}")
            return False
        # Determine valid accidentals based on the scale notes
        valid_notes = [n.name for n in self.notes]
        if note.name not in valid_notes:
            logger.warning(f"Note name {note.name} is not in the scale notes.")
            return False
        return True
