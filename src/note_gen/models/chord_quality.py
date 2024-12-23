from pydantic import BaseModel
from src.note_gen.models.enums import ChordQualityType
import logging

class ChordQuality(BaseModel):
    quality: ChordQualityType

    @classmethod
    def from_string(cls, quality_str: str) -> "ChordQuality":
        """Convert a string representation of a chord quality to a ChordQuality instance."""
        quality_dict = {
            "major": ChordQualityType.MAJOR,
            "minor": ChordQualityType.MINOR,
            "diminished": ChordQualityType.DIMINISHED,
            "augmented": ChordQualityType.AUGMENTED,
            "dominant": ChordQualityType.DOMINANT,
            "dominant7": ChordQualityType.DOMINANT_7,
            "maj7": ChordQualityType.MAJOR_SEVENTH,
            "min7": ChordQualityType.MINOR_SEVENTH,
            "dim7": ChordQualityType.DIMINISHED_SEVENTH,
            "half_diminished": ChordQualityType.HALF_DIMINISHED,
            "half_diminished7": ChordQualityType.HALF_DIMINISHED_SEVENTH,
            "aug7": ChordQualityType.AUGMENTED_SEVENTH,
            "major9": ChordQualityType.MAJOR_9,
            "minor9": ChordQualityType.MINOR_9,
            "dominant9": ChordQualityType.DOMINANT_9,
            "major11": ChordQualityType.MAJOR_11,
            "minor11": ChordQualityType.MINOR_11,
            "sus2": ChordQualityType.SUS2,
            "sus4": ChordQualityType.SUS4,
            "seven_sus4": ChordQualityType.SEVEN_SUS4,
        }
        
        quality = quality_dict.get(quality_str.lower())
        if quality is None:
            logging.warning(f"Unknown chord quality '{quality_str}' provided. Defaulting to MAJOR.")
            quality = ChordQualityType.MAJOR  # Default to MAJOR if not found
            
        return cls(quality=quality)