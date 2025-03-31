"""Roman numeral model definition."""
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from src.note_gen.models.chord import ChordQuality
from src.note_gen.core.constants import (
    INT_TO_ROMAN,
    ROMAN_TO_INT,
    SCALE_DEGREE_QUALITIES,
    DEFAULT_SCALE_DEGREE_QUALITIES
)
from src.note_gen.models.chord import Chord

ROMAN_NUMERAL_PATTERN = r'^[IViv]+$'

class RomanNumeral(BaseModel):
    """Model representing a Roman numeral chord symbol."""
    model_config = ConfigDict(
        extra='allow'
    )

    numeral: str = Field(..., pattern=ROMAN_NUMERAL_PATTERN)
    quality: Optional[ChordQuality] = None
    inversion: Optional[int] = Field(default=None, ge=0, le=3)
    accidental: Optional[str] = Field(default=None, pattern=r'^[b#]?$')
    secondary: Optional['RomanNumeral'] = None

    @classmethod
    def from_scale_degree(cls, degree: int, is_minor: bool | ChordQuality = False) -> 'RomanNumeral':
        """
        Create a RomanNumeral from a scale degree.
        
        Args:
            degree: Scale degree (1-7)
            is_minor: Either a boolean indicating if the chord is minor,
                     or a ChordQuality enum value specifying the exact quality
        
        Returns:
            RomanNumeral instance
        
        Raises:
            ValueError: If degree is not between 1 and 7
        """
        if not 1 <= degree <= 7:
            raise ValueError(f"Scale degree must be between 1 and 7, got {degree}")
        
        numeral = INT_TO_ROMAN[degree]
        
        # Handle quality
        if isinstance(is_minor, ChordQuality):
            # If explicit ChordQuality is provided, use it directly
            quality = is_minor
        else:
            # Handle boolean is_minor parameter
            quality = ChordQuality.MINOR if is_minor else ChordQuality.MAJOR
            # Only apply default qualities if no explicit quality was provided
            if degree in DEFAULT_SCALE_DEGREE_QUALITIES:
                quality = DEFAULT_SCALE_DEGREE_QUALITIES[degree]
        
        return cls(
            numeral=numeral,
            quality=quality,
            accidental=None,
            inversion=None,
            secondary=None
        )

    def to_scale_degree(self) -> 'ScaleDegree':
        """Convert to scale degree."""
        from src.note_gen.core.constants import ROMAN_TO_INT
        from src.note_gen.models.scale_degree import ScaleDegree
        
        base_degree = ROMAN_TO_INT[self.numeral.upper()]
        return ScaleDegree(
            value=base_degree,
            quality=self.quality
        )

    @classmethod
    def from_string(cls, value: str) -> 'RomanNumeral':
        """Create a RomanNumeral from a string representation."""
        import re
        
        match = re.match(ROMAN_NUMERAL_PATTERN, value)
        if not match:
            raise ValueError(f"Invalid Roman numeral format: {value}")
            
        accidental, numeral, quality_str, *_ = match.groups()
        
        # Create base instance
        instance = cls(
            numeral=numeral,
            accidental=accidental if accidental else None
        )
        
        # Add quality if present
        if quality_str:
            try:
                instance.quality = ChordQuality.from_string(quality_str)
            except ValueError:
                pass  # Keep default quality if string conversion fails
                
        return instance

    def __str__(self) -> str:
        """String representation of the Roman numeral."""
        parts = []
        if self.accidental:
            parts.append(self.accidental)
        parts.append(self.numeral)
        if self.quality:
            parts.append(str(self.quality))
        if self.inversion is not None and self.inversion > 0:
            parts.append(f"/{self.inversion}")
        if self.secondary is not None:
            parts.append(f"/{str(self.secondary)}")
        return "".join(parts)

    def to_chord(self) -> Chord:
        """Convert Roman numeral to a Chord object."""
        # Implementation...
        pass

    @property
    def is_minor(self) -> bool:
        """Check if the Roman numeral represents a minor chord."""
        return self.quality == ChordQuality.MINOR if self.quality else False
