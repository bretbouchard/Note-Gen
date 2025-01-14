from __future__ import annotations
from typing import List, Dict, ClassVar
from enum import Enum
from pydantic import BaseModel, Field

class ChordQualityType(str, Enum):
    """Enum representing different chord qualities."""
    
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT = "dominant"
    DOMINANT_SEVENTH = "dominant7"
    MAJOR_SEVENTH = "major7"
    MINOR_SEVENTH = "minor7"
    HALF_DIMINISHED = "half_diminished"
    FULLY_DIMINISHED = "fully_diminished"
    
    @classmethod
    def get_intervals(cls, quality: ChordQualityType) -> List[int]:
        """Get the intervals for a given chord quality.
        
        Args:
            quality: The chord quality
            
        Returns:
            List[int]: List of semitone intervals from the root
        """
        intervals_map = {
            cls.MAJOR: [0, 4, 7],
            cls.MINOR: [0, 3, 7],
            cls.DIMINISHED: [0, 3, 6],
            cls.AUGMENTED: [0, 4, 8],
            cls.DOMINANT: [0, 4, 7],
            cls.DOMINANT_SEVENTH: [0, 4, 7, 10],
            cls.MAJOR_SEVENTH: [0, 4, 7, 11],
            cls.MINOR_SEVENTH: [0, 3, 7, 10],
            cls.HALF_DIMINISHED: [0, 3, 6, 10],
            cls.FULLY_DIMINISHED: [0, 3, 6, 9]
        }
        return intervals_map[quality]
    
    @classmethod
    def from_string(cls, quality_str: str) -> ChordQualityType:
        """Convert a string representation to a ChordQualityType.
        
        Args:
            quality_str: String representation of the chord quality
            
        Returns:
            ChordQualityType: The corresponding chord quality type
            
        Raises:
            ValueError: If the string does not match any known chord quality
        """
        if quality_str is None:
            raise ValueError("Chord quality cannot be None")
        quality_map = {
            "M": cls.MAJOR,
            "maj": cls.MAJOR,
            "major": cls.MAJOR,
            "m": cls.MINOR,
            "min": cls.MINOR,
            "minor": cls.MINOR,
            "dim": cls.DIMINISHED,
            "diminished": cls.DIMINISHED,
            "aug": cls.AUGMENTED,
            "augmented": cls.AUGMENTED,
            "7": cls.DOMINANT_SEVENTH,
            "dom7": cls.DOMINANT_SEVENTH,
            "dominant7": cls.DOMINANT_SEVENTH,
            "dom": cls.DOMINANT,
            "maj7": cls.MAJOR_SEVENTH,
            "M7": cls.MAJOR_SEVENTH,
            "m7": cls.MINOR_SEVENTH,
            "min7": cls.MINOR_SEVENTH,
            "ø": cls.HALF_DIMINISHED,
            "half-dim": cls.HALF_DIMINISHED,
            "o": cls.FULLY_DIMINISHED,
            "dim7": cls.FULLY_DIMINISHED,
            "dominant": cls.DOMINANT
        }
        
        quality_str = quality_str.lower()
        if quality_str not in quality_map:
            raise ValueError(f"Unknown chord quality: {quality_str}")
        
        return quality_map[quality_str]

class ChordQuality(BaseModel):
    """A class representing chord quality with methods for interval calculation."""
    
    quality_type: ChordQualityType = Field(default=ChordQualityType.MAJOR)
    
    @classmethod
    def from_string(cls, quality_str: str) -> ChordQuality:
        """Create a ChordQuality from a string representation."""
        quality_type = ChordQualityType.from_string(quality_str)
        return cls(**{"quality_type": quality_type})
    
    def get_intervals(self) -> List[int]:
        """Get the intervals for this chord quality."""
        return ChordQualityType.get_intervals(self.quality_type)
    
    def __str__(self) -> str:
        """Get the string representation of the chord quality."""
        return self.quality_type.value
