from pydantic import BaseModel, Field
from typing import Dict, Optional, ClassVar, Pattern
import re
from .chord_quality import ChordQuality
from .scale import Scale

class RomanNumeral(BaseModel):
    numeral: str = Field(...)
    quality: ChordQuality = Field(default=ChordQuality.MAJOR)
    inversion: int = Field(default=0)

    # Class variables 
    ROMAN_PATTERN: ClassVar[str] = r'^(b|#)?([ivIV]+)(°|\+|dim|aug|ø7|°7|maj7|m7|7|m)?(\d)?$'
    ROMAN_TO_INT: ClassVar[Dict[str, int]] = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7}
    INT_TO_ROMAN: ClassVar[Dict[int, str]] = {v: k for k, v in ROMAN_TO_INT.items()}
    
    @classmethod
    def from_scale_degree(cls, degree: int, quality: ChordQuality = ChordQuality.MAJOR, 
                         inversion: int = 0) -> 'RomanNumeral':
        """Create a Roman numeral from a scale degree."""
        if not 1 <= degree <= 7:
            raise ValueError(f"Scale degree must be between 1 and 7, got {degree}")
            
        numeral = cls.INT_TO_ROMAN[degree]
        # Uppercase for major-based qualities
        if quality in [ChordQuality.MAJOR, ChordQuality.DOMINANT_SEVENTH, 
                      ChordQuality.MAJOR_SEVENTH, ChordQuality.AUGMENTED]:
            numeral = numeral.upper()
        
        # Modify the quality symbol handling
        symbol = ""
        if quality == ChordQuality.DIMINISHED:
            symbol = "°"
        elif quality == ChordQuality.AUGMENTED:
            symbol = "+"
        elif quality == ChordQuality.MINOR_SEVENTH:
            symbol = "7"  # Changed from "m7" to "7" for minor seventh chords
        elif quality == ChordQuality.MAJOR_SEVENTH:
            symbol = "maj7"
        elif quality == ChordQuality.DOMINANT_SEVENTH:
            symbol = "7"
        
        final_numeral = f"{numeral}{symbol}"
        
        return cls(
            numeral=final_numeral,
            quality=quality,
            inversion=inversion
        )

    @classmethod
    def from_roman_numeral(cls, numeral: str) -> 'RomanNumeral':
        """Parse a Roman numeral string."""
        match = re.match(cls.ROMAN_PATTERN, numeral, re.IGNORECASE)
        if not match:
            raise ValueError(f"Invalid Roman numeral: {numeral}")
        
        accidental, base, quality_str, inversion = match.groups()
        is_major = base.isupper()
        
        quality = ChordQuality.MAJOR if is_major else ChordQuality.MINOR
        if quality_str:
            quality = ChordQuality.from_string(quality_str)
            
        inv = int(inversion) if inversion else 0
        
        return cls(numeral=numeral, quality=quality, inversion=inv)

    @classmethod
    def from_string(cls, numeral: str) -> "RomanNumeral":
        """Convert string representation to RomanNumeral."""
        match = re.match(cls.ROMAN_PATTERN, numeral, re.IGNORECASE)
        if not match:
            raise ValueError(f"Invalid Roman numeral: {numeral}")
        
        accidental, base, quality_str, inversion = match.groups()
        is_major = base.isupper()
        quality = ChordQuality.MAJOR if is_major else ChordQuality.MINOR
        
        if quality_str:
            try:
                quality = ChordQuality.from_string(quality_str)
            except ValueError:
                pass  # Keep default quality if conversion fails
                
        inv = int(inversion) if inversion else 0
        
        return cls(
            numeral=numeral,
            quality=quality,
            inversion=inv
        )

    def to_scale_degree(self) -> int:
        """Convert Roman numeral to scale degree."""
        # First validate the entire numeral matches our pattern
        if not re.match(self.ROMAN_PATTERN, self.numeral, re.IGNORECASE):
            raise ValueError(f"Invalid Roman numeral format: {self.numeral}")
        
        # Extract just the roman numeral part (i, ii, iii, etc.)
        base = ''.join(c for c in self.numeral.lower() if c in 'iv')
        
        # Validate the base numeral is a valid Roman numeral pattern
        valid_numerals = {'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'}
        if not base or base not in valid_numerals:
            raise ValueError(f"Invalid Roman numeral: {self.numeral}")
        
        # Ensure the base is in our mapping
        if base not in self.ROMAN_TO_INT:
            raise ValueError(f"Unsupported Roman numeral: {self.numeral}")
        
        return self.ROMAN_TO_INT[base]

    @classmethod
    def get_roman_numeral_from_chord(cls, chord, scale) -> 'RomanNumeral':
        """Get Roman numeral representation of a chord in a given scale."""
        try:
            # Get the scale degree of the chord's root note
            if not hasattr(scale, 'get_degree_of_note'):
                raise ValueError("Scale must implement get_degree_of_note method")
            
            degree = scale.get_degree_of_note(chord.root)
            if degree is None:
                raise ValueError(f"Note {chord.root.note_name} not in scale")
            
            # Convert degree to int if it's a string
            if isinstance(degree, str):
                degree = int(degree)
            
            return cls.from_scale_degree(degree, chord.quality, chord.inversion)
        except Exception as e:
            raise ValueError(f"Unexpected error processing chord: {str(e)}") from e
