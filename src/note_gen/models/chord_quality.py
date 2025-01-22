from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from src.note_gen.models.enums import ChordQualityType
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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
        
        logging.debug(f"Converting chord quality from string: {quality_str}")
        
        if quality_str == "M":
            return cls(quality_type=ChordQualityType.MAJOR)

        quality_str = quality_str.lower()  # Convert to lowercase for consistent mapping
        
        # Try to convert the string to a ChordQualityType
        mapping = {
            "major": ChordQualityType.MAJOR,
            "maj": ChordQualityType.MAJOR,
            "minor": ChordQualityType.MINOR,
            "min": ChordQualityType.MINOR,
            "m": ChordQualityType.MINOR,
            "diminished": ChordQualityType.DIMINISHED,
            "dim": ChordQualityType.DIMINISHED,
            "°": ChordQualityType.DIMINISHED,
            "7": ChordQualityType.DOMINANT_7,
            "maj7": ChordQualityType.MAJOR_7,
            "m7": ChordQualityType.MINOR_7,
            "dim7": ChordQualityType.DIMINISHED_7,
            "ø7": ChordQualityType.HALF_DIMINISHED_7,
            "m7b5": ChordQualityType.HALF_DIMINISHED_7,
            "aug": ChordQualityType.AUGMENTED,
            "+": ChordQualityType.AUGMENTED,
            # Add other mappings as necessary
        }

        logging.debug(f"Input quality string: {quality_str}")  # Log the input quality string
        quality = mapping.get(quality_str)
        logging.debug(f"Mapped quality: {quality}")  # Log the mapped quality
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
        if self.quality_type == ChordQualityType.DOMINANT_7:
            return "7"
        if self.quality_type == ChordQualityType.MAJOR_7:
            return "maj7"
        if self.quality_type == ChordQualityType.MINOR_7:
            return "m7"
        return self.quality_type.value
