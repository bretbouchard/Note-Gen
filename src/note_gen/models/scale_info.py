from typing import Optional, Dict, ClassVar, List
from pydantic import BaseModel, ConfigDict, Field
import logging

from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.chord import Chord, ChordQuality

from src.note_gen.models.enums import ScaleDegree, ScaleType

logger = logging.getLogger(__name__)

class ScaleInfo(BaseModel):
    """Information about a musical scale."""
    root: Note
    key: str = Field(default='C')
    scale_type: Optional[str] = 'MAJOR'
    _scale_notes: Optional[List[Note]] = None  # Private field to cache scale notes

    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, Chord]] = {
        1: Chord(root=Note(note_name='C', octave=4), quality=ChordQuality.MAJOR),
        2: Chord(root=Note(note_name='D', octave=4), quality=ChordQuality.MINOR),
        3: Chord(root=Note(note_name='E', octave=4), quality=ChordQuality.MINOR),
        4: Chord(root=Note(note_name='F', octave=4), quality=ChordQuality.MAJOR),
        5: Chord(root=Note(note_name='G', octave=4), quality=ChordQuality.MAJOR),
        6: Chord(root=Note(note_name='A', octave=4), quality=ChordQuality.MINOR),
        7: Chord(root=Note(note_name='B', octave=4), quality=ChordQuality.DIMINISHED)
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, Chord]] = {
        1: Chord(root=Note(note_name='C', octave=4), quality=ChordQuality.MINOR),
        2: Chord(root=Note(note_name='D', octave=4), quality=ChordQuality.DIMINISHED),
        3: Chord(root=Note(note_name='E', octave=4), quality=ChordQuality.MAJOR),
        4: Chord(root=Note(note_name='F', octave=4), quality=ChordQuality.MINOR),
        5: Chord(root=Note(note_name='G', octave=4), quality=ChordQuality.MINOR),
        6: Chord(root=Note(note_name='A', octave=4), quality=ChordQuality.MAJOR),
        7: Chord(root=Note(note_name='B', octave=4), quality=ChordQuality.MAJOR)
    }

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    def get_note_for_degree(self, degree: int) -> Note:
        """Get the note for a given scale degree."""
        return self.root

    def get_scale_note_at_degree(self, degree: int) -> Note:
        """Get the note at a given scale degree."""
        scale: Scale = Scale(root=self.root, scale_type=self.scale_type)
        return scale.get_note_at_degree(degree)

    def get_chord_quality_for_degree(self, degree: int) -> Chord:
        """Get the chord quality for a given scale degree."""
        if degree < 1 or degree > 7:
            raise ValueError("Degree must be between 1 and 7")
        logger.debug(f"Getting chord quality for degree: {degree}")
        quality_dict = self.MAJOR_SCALE_QUALITIES[degree] if self.scale_type == 'MAJOR' else self.MINOR_SCALE_QUALITIES[degree]
        quality = quality_dict['quality']
        logger.debug(f"Degree: {degree}, Chord Quality: {quality.quality}")
        logger.debug(f"Returning chord quality: {quality}")
        return quality

    def compute_scale_degrees(self) -> List[int]:
        """Compute the scale degrees based on the root and scale type."""
        scale = Scale(root=self.root, scale_type=self.scale_type)
        return scale.calculate_intervals()

    def get_scale_notes(self) -> List[Note]:
        """
        Generate and return all notes in the scale.
        
        This method caches the scale notes to avoid redundant calculation.
        
        Returns:
            List[Note]: List of all notes in the scale
        """
        # Return cached notes if available
        if hasattr(self, '_scale_notes') and self._scale_notes is not None:
            logger.debug(f"Returning cached scale notes: {[note.note_name + str(note.octave) for note in self._scale_notes]}")
            return self._scale_notes
            
        logger.debug(f"Generating scale notes for {self.scale_type} scale with root {self.root.note_name}{self.root.octave}")
        scale = Scale(root=self.root, scale_type=self.scale_type)
        self._scale_notes = scale._generate_scale_notes()
        logger.debug(f"Generated {len(self._scale_notes)} scale notes: {[note.note_name + str(note.octave) for note in self._scale_notes]}")
        return self._scale_notes
