from typing import List, Optional, Dict, ClassVar
from pydantic import BaseModel, Field

from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale, ScaleType
from src.note_gen.models.chord_quality import ChordQualityType

class ScaleInfo(BaseModel):
    """Information about a musical scale."""
    root: Note
    scale_type: Optional[str] = "major"

    # Define chord qualities for major and minor scales
    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, ChordQualityType]] = {
        1: ChordQualityType.MAJOR,      # I
        2: ChordQualityType.MINOR,      # ii
        3: ChordQualityType.MINOR,      # iii
        4: ChordQualityType.MAJOR,      # IV
        5: ChordQualityType.MAJOR,      # V
        6: ChordQualityType.MINOR,      # vi
        7: ChordQualityType.DIMINISHED  # vii°
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, ChordQualityType]] = {
        1: ChordQualityType.MINOR,      # i
        2: ChordQualityType.DIMINISHED, # ii°
        3: ChordQualityType.MAJOR,      # III
        4: ChordQualityType.MINOR,      # iv
        5: ChordQualityType.MINOR,      # v
        6: ChordQualityType.MAJOR,      # VI
        7: ChordQualityType.MAJOR       # VII
    }

    def get_note_for_degree(self, degree: int) -> Optional[Note]:
        """Get the note for a given scale degree."""
        if degree < 1 or degree > 7:
            return None
            
        if not self.scale_type:
            return None

        scale = Scale(root=self.root, scale_type=ScaleType(self.scale_type))
        notes = scale.get_notes()
        return notes[degree - 1] if notes else None

    def get_scale_note_at_degree(self, degree: int) -> Note:
        """Get the note at a given scale degree."""
        scale = Scale(root=self.root, scale_type=ScaleType(self.scale_type))
        return scale.get_note_at_degree(degree)

    def get_chord_quality_for_degree(self, degree: int) -> ChordQualityType:
        """Get the chord quality for a given scale degree."""
        if not isinstance(degree, int):
            raise ValueError(f"Degree must be an integer, got {type(degree)}")
            
        if degree < 1 or degree > 7:
            raise ValueError(f"Invalid scale degree: {degree}")
            
        if not self.scale_type:
            raise ValueError("scale_type cannot be None")

        qualities = (
            self.MAJOR_SCALE_QUALITIES if self.scale_type == "major"
            else self.MINOR_SCALE_QUALITIES
        )
        
        return qualities[degree]
