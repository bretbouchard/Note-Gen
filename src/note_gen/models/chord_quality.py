from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from src.note_gen.models.enums import ChordQualityType

class ChordQuality(BaseModel):
    """A class representing chord quality with methods for interval calculation."""
    
    quality_type: ChordQualityType = Field(default=ChordQualityType.MAJOR)
    
    @classmethod
    def from_string(cls, quality_str: str) -> ChordQuality:
        """Create a ChordQuality from a string representation.
        
        Args:
            quality_str: String representation of the chord quality
            
        Returns:
            ChordQuality: A new ChordQuality instance
            
        Raises:
            ValueError: If the quality string is invalid
        """
        if not quality_str:
            raise ValueError("Quality string cannot be empty")
        
        # Try to convert the string to a ChordQualityType
        quality = ChordQualityType._missing_(cls=ChordQualityType, value=quality_str)
        if quality is None:
            raise ValueError(f"Invalid chord quality: {quality_str}")
            
        return cls(quality_type=quality)
    
    def get_intervals(self) -> List[int]:
        """Get the intervals for this chord quality.
        
        Returns:
            List[int]: List of semitone intervals from the root
        """
        return self.quality_type.get_intervals()
    
    def __str__(self) -> str:
        """Get the string representation of the chord quality.
        
        Returns:
            str: String representation
        """
        return self.quality_type.value
