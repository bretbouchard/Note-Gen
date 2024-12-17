"""
Module for handling musical scales.
"""
from typing import Dict, List, Tuple, ClassVar, Any, Optional
from pydantic import BaseModel
import logging

from .note import Note
from .scale_info import ScaleInfo  # Import ScaleInfo
from .scale_degree import ScaleDegree  # Import ScaleDegree

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Scale(BaseModel):
    """A musical scale."""
    root: Note
    quality: str
    notes: List[Note] = []
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

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, root: Note, quality: str = 'major', notes: List[Note] = [], scale_degrees: List[ScaleDegree] = [], scale_info: Optional[ScaleInfo] = None) -> None:
        """Initialize a Scale object with root, quality, and optional notes and scale degrees."""
        logger.info(f"Initializing Scale object with root: {root}, quality: {quality}")
        self._validate_quality(quality)
        super().__init__(root=root, quality=quality, notes=notes, scale_degrees=scale_degrees, scale_info_v2=scale_info)
        self.notes = self._build_scale_from_intervals()
        self.scale_degrees = self._get_scale_degrees()
        if scale_info is None:
            self.scale_info_v2 = ScaleInfo(root=self.root, scale_type=self.quality)
        else:
            self.scale_info_v2 = scale_info

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
        scale_notes = [self.root]
        for interval in intervals[1:]:
            next_note = self._get_next_note(scale_notes[-1], interval)
            scale_notes.append(next_note)
        logger.debug(f"Scale built: {scale_notes}")
        return scale_notes

    def _get_next_note(self, current_note: Note, interval: int) -> Note:
        """Get the next note based on the current note and interval."""
        logger.debug(f"Getting next note from {current_note.note_name} with interval {interval}")
        # Logic to calculate the next note based on the interval
        # Assuming we have a method to get the note's position in the scale
        current_position = self.notes.index(current_note)
        next_position = (current_position + interval) % len(self.notes)
        next_note = self.notes[next_position]
        logger.debug(f"Next note is {next_note.note_name}")
        return next_note

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
        logger.debug(f"Scale notes retrieved: {notes}")
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
