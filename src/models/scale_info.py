"""Module for handling scale info."""
from __future__ import annotations
import logging

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .note import Note
from .scale_degree import ScaleDegree

# Define scale intervals for different modes
SCALE_INTERVALS = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor': [0, 2, 3, 5, 7, 9, 11]
}

class ScaleInfo(BaseModel):
    """Information about a musical scale."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    scale_type: str = Field(default="major")
    root: Note
    quality: str = Field(default="major")
    key_signature: str = Field(default="")
    intervals: List[int] = Field(default_factory=list)
    scale_degrees: Optional[List[ScaleDegree]] = Field(default=None)
    mode: Optional[str] = None
    notes: List[Note] = Field(default_factory=list)
    scale_notes: List[Note] = Field(default_factory=list)  # Initialize scale_notes
    scale: List[str] = Field(default_factory=list)  # Add scale attribute to hold scale notes

    @field_validator('scale_type')
    def validate_scale_type(cls, value: str) -> str:
        if value not in ['major', 'minor', 'harmonic_minor', 'melodic_minor']:
            raise ValueError(f"Invalid scale type: {value}. Must be 'major', 'minor', 'harmonic_minor', or 'melodic_minor'.")
        return value

    def __init__(self, root: Note, scale_type: str = 'major', key_signature: str = '', intervals: List[int] = [], scale_degrees: Optional[List[ScaleDegree]] = None, mode: Optional[str] = 'major', notes: List[Note] = []) -> None:
        """Initialize a ScaleInfo object with root, scale type, key signature, and optional intervals and scale degrees."""
        logger = logging.getLogger(__name__)
        logger.info(f"Initializing ScaleInfo with root: {root}, scale_type: {scale_type}, key_signature: {key_signature}")
        if not root:
            logger.error("Root note is required.")
            raise ValueError("Root note is required. Please provide a valid Note object.")
        if not isinstance(scale_type, str):
            logger.error("Scale type must be a string.")
            raise ValueError("Scale type must be a string. Please provide a valid string.")
        if not isinstance(key_signature, str):
            logger.error("Key signature must be a string.")
            raise ValueError("Key signature must be a string. Please provide a valid string.")
        if not isinstance(intervals, list):
            logger.error("Intervals must be a list.")
            raise ValueError("Intervals must be a list. Please provide a valid list of integers.")
        if scale_degrees is not None and not isinstance(scale_degrees, list):
            logger.error("Scale degrees must be a list.")
            raise ValueError("Scale degrees must be a list. Please provide a valid list of ScaleDegree objects.")
        if mode is not None and not isinstance(mode, str):
            logger.error("Mode must be a string.")
            raise ValueError("Mode must be a string. Please provide a valid string.")
        if not isinstance(notes, list):
            logger.error("Notes must be a list.")
            raise ValueError("Notes must be a list. Please provide a valid list of Note objects.")
        super().__init__(root=root, scale_type=scale_type, key_signature=key_signature, intervals=intervals, scale_degrees=scale_degrees, mode=mode, notes=notes)

    def get_note_by_degree(self, degree: int) -> Optional[Note]:
        """Get the note corresponding to a specific scale degree."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Getting note for degree: {degree}")
        if 1 <= degree <= len(self.notes):
            note = self.notes[degree - 1]  # Convert to 0-based index
            logger.info(f"Note retrieved for degree {degree}: {note}")
            return note
        logger.warning(f"Degree {degree} is out of range for notes.")
        return None

    def compute_scale_degrees(self) -> List[ScaleDegree]:
        """Compute the scale degrees for this scale."""
        logger = logging.getLogger(__name__)
        logger.info("Computing scale degrees.")
        if self.scale_degrees is not None:
            logger.debug("Scale degrees already computed.")
            return self.scale_degrees

        # Choose intervals based on mode
        intervals = SCALE_INTERVALS.get(self.scale_type, SCALE_INTERVALS['major'])
        logger.info(f"Using intervals for scale type '{self.scale_type}': {intervals}")  # Log intervals used

        # Create scale degrees
        scale_degrees = []
        for i, interval in enumerate(intervals):
            note = self.root.transpose(interval)
            logger.info(f"Generated note for degree {i + 1}: {note}")  # Log generated notes
            scale_degree = ScaleDegree(
                degree=i + 1,
                note=note
            )
            scale_degrees.append(scale_degree)

        self.scale_degrees = scale_degrees
        self.scale_notes = [degree.note for degree in scale_degrees if degree.note is not None]  # Initialize scale_notes
        logger.debug(f"Computed scale degrees: {self.scale_degrees}")
        return scale_degrees

    def get_scale_degree(self, degree: int) -> Optional[Note]:
        """Get a note at a specific scale degree."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Getting scale degree for degree: {degree}")
        if not self.scale_degrees:
            logger.warning("Scale degrees not computed yet.")
            return None
        if degree < 1 or degree > len(self.scale_degrees):
            logger.warning(f"Requested degree {degree} is out of range.")
            return None
        logger.info(f"Requested scale degree: {degree}")  # Log requested degree
        return self.scale_degrees[degree - 1].note

    def get_scale_notes(self) -> List[Note]:
        """Get all notes in the scale."""
        logger = logging.getLogger(__name__)
        logger.debug("Retrieving all notes in the scale.")
        if not self.scale_degrees:
            logger.warning("Scale degrees not computed yet.")
            return []
        logger.info("Retrieving scale notes.")
        return self.scale_notes

    def get_notes(self) -> List[Note]:
        logger = logging.getLogger(__name__)
        logger.debug("Getting notes from ScaleInfo.")
        return [note for note in self.notes if note is not None]  # Ensure only Note objects are returned

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        logger = logging.getLogger(__name__)
        logger.debug("Converting ScaleInfo to dictionary representation.")
        d = super().model_dump(*args, **kwargs)
        d['root'] = self.root.name  # Include root note name
        d['scale_notes'] = [note.name for note in self.notes]  # Include scale notes
        logger.info("ScaleInfo converted to dictionary successfully.")
        return d
