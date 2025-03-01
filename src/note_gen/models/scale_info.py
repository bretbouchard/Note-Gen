from typing import Optional, Dict, ClassVar, List
from pydantic import BaseModel, ConfigDict, Field
import logging

from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_quality import ChordQualityType
from src.note_gen.models.enums import ScaleDegree, ScaleType

logger = logging.getLogger(__name__)

class ScaleInfo(BaseModel):
    """Information about a musical scale."""
    root: Note
    key: str = Field(default='C')
    scale_type: Optional[str] = 'MAJOR'

    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, ChordQualityType]] = {
        1: ChordQualityType.MAJOR,
        2: ChordQualityType.MINOR,
        3: ChordQualityType.MINOR,
        4: ChordQualityType.MAJOR,
        5: ChordQualityType.MAJOR,
        6: ChordQualityType.MINOR,
        7: ChordQualityType.DIMINISHED
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, ChordQualityType]] = {
        1: ChordQualityType.MINOR,
        2: ChordQualityType.DIMINISHED,
        3: ChordQualityType.MAJOR,
        4: ChordQualityType.MINOR,
        5: ChordQualityType.MINOR,
        6: ChordQualityType.MAJOR,
        7: ChordQualityType.MAJOR
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

    def get_chord_quality_for_degree(self, degree: int) -> ChordQualityType:
        """Get the chord quality for a given scale degree."""
        if degree < 1 or degree > 7:
            raise ValueError("Degree must be between 1 and 7")
        logger.debug(f"Getting chord quality for degree: {degree}")
        quality: ChordQualityType = self.MAJOR_SCALE_QUALITIES[degree] if self.scale_type == 'MAJOR' else self.MINOR_SCALE_QUALITIES[degree]
        logger.debug(f"Degree: {degree}, Chord Quality: {quality}")
        logger.debug(f"Returning chord quality: {quality}")
        return quality

    def compute_scale_degrees(self) -> List[int]:
        """Compute the scale degrees based on the root and scale type."""
        scale = Scale(root=self.root, scale_type=self.scale_type)
        return scale.calculate_intervals()
