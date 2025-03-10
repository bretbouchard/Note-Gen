from typing import Optional, Dict, ClassVar, Union
from pydantic import BaseModel, ConfigDict, field_validator
import re
import logging
from enum import Enum

from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.scale import Scale
from src.note_gen.models.note import Note

logger = logging.getLogger(__name__)

class RomanNumeral(BaseModel):
    """A roman numeral representation of a scale degree and chord quality."""
    scale_degree: int
    quality: ChordQuality

    @field_validator('scale_degree')
    def validate_scale_degree(cls, v: int) -> int:
        if not 1 <= v <= 7:
            raise ValueError('Scale degree must be between 1 and 7')
        return v

    @field_validator('quality')
    def validate_quality(cls, v: ChordQuality) -> ChordQuality:
        if v not in ChordQuality:
            raise ValueError(f'Invalid chord quality: {v}')
        return v

    # Class constants
    INT_TO_ROMAN: ClassVar[Dict[int, str]] = {
        1: "I",
        2: "II",
        3: "III",
        4: "IV",
        5: "V",
        6: "VI",
        7: "VII"
    }

    # Updated mapping with better organization and validation support
    ROMAN_TO_INT: ClassVar[Dict[str, int]] = {
        # Basic numerals
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
        "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,       
        # Seventh chords
        "I7": 1, "II7": 2, "III7": 3, "IV7": 4, "V7": 5, "VI7": 6, "VII7": 7,
        "i7": 1, "ii7": 2, "iii7": 3, "iv7": 4, "v7": 5, "vi7": 6, "vii7": 7,
        "Imaj7": 1, "IImaj7": 2, "IIImaj7": 3, "IVmaj7": 4, "Vmaj7": 5, "VImaj7": 6, "VIImaj7": 7,
        
        # Diminished and half-diminished
        "vii°": 7, "vii°7": 7, "iiø": 2, "iiø7": 2,
        "ii°": 2, "ii°7": 2, "iii°": 3, "iii°7": 3,
        
        # Augmented
        "I+": 1, "II+": 2, "III+": 3, "IV+": 4, "V+": 5, "VI+": 6, "VII+": 7,
        
        # Common alterations
        "bII": 2, "bIII": 3, "bVI": 6, "bVII": 7,
        "II♭5": 2, "V♭5": 5, "II♭7": 2, "V♭7": 5,
        
        # Secondary dominants
        "V7/V": 5, "V7/IV": 4, "V7/II": 2, "V7/vi": 6,
        
        # Common jazz notation
        "V7alt": 5, "Valt": 5,
        
        # Slash chords
        "I/V": 1, "IV/V": 4, "V/V": 5, "VI/V": 6, "VII/V": 7
    }

    ROMAN_NUMERAL_MAP: ClassVar[Dict[str, int]] = ROMAN_TO_INT

    # Quality modifiers and their corresponding ChordQuality values
    QUALITY_MODIFIERS: ClassVar[Dict[str, ChordQuality]] = {
        "": ChordQuality.MAJOR,
        "7": ChordQuality.DOMINANT_SEVENTH,
        "maj7": ChordQuality.MAJOR_SEVENTH,
        "Δ": ChordQuality.MAJOR_SEVENTH,
        "m": ChordQuality.MINOR,
        "m7": ChordQuality.MINOR_SEVENTH,
        "°": ChordQuality.DIMINISHED,
        "°7": ChordQuality.DIMINISHED_SEVENTH,
        "ø": ChordQuality.HALF_DIMINISHED,
        "ø7": ChordQuality.HALF_DIMINISHED,
        "+": ChordQuality.AUGMENTED,
        "aug": ChordQuality.AUGMENTED
    }

    def __init__(self, scale_degree: int, quality: ChordQuality, **kwargs):
        super().__init__(scale_degree=scale_degree, quality=quality, **kwargs)

    def __str__(self) -> str:
        numeral = RomanNumeral.INT_TO_ROMAN[self.scale_degree]

        if self.quality == ChordQuality.MINOR:
            numeral = numeral.lower()
        elif self.quality == ChordQuality.DIMINISHED:
            numeral = numeral.lower() + 'o'
        elif self.quality == ChordQuality.AUGMENTED:
            numeral = numeral + '+'
        elif self.quality == ChordQuality.MAJOR_SEVENTH:
            numeral = numeral + 'Δ'
        elif self.quality == ChordQuality.MINOR_SEVENTH:
            numeral = numeral.lower() + '7'
        elif self.quality == ChordQuality.DOMINANT_SEVENTH:
            numeral = numeral + '7'
        return numeral

    @classmethod
    def from_string(cls, numeral: str) -> 'RomanNumeral':
        """Create a RomanNumeral instance from a string representation."""
        if not numeral:
            raise ValueError("Roman numeral cannot be empty")

        # Extract base numeral and any modifiers
        match = re.match(r"^(b?)([IiVv]+)(.*?)(/[IiVv]+)?$", numeral)
        if not match:
            raise ValueError(f"Invalid roman numeral format: {numeral}")

        flat_prefix, base, quality_suffix, slash = match.groups()
        base_upper = base.upper()

        # Validate base numeral
        if base_upper not in cls.INT_TO_ROMAN.values():
            raise ValueError(f"Invalid base roman numeral: {base}")

        # Get scale degree
        scale_degree = cls.ROMAN_TO_INT.get(base)
        if scale_degree is None:
            raise ValueError(f"Unknown roman numeral: {base}")

        # Determine quality
        is_minor = base.islower()
        quality = ChordQuality.MINOR if is_minor else ChordQuality.MAJOR

        # Apply quality modifiers
        if quality_suffix:
            clean_suffix = quality_suffix.strip()
            if clean_suffix in cls.QUALITY_MODIFIERS:
                quality = cls.QUALITY_MODIFIERS[clean_suffix]
            else:
                logger.warning(f"Unknown quality modifier: {clean_suffix}")

        return cls(scale_degree=scale_degree, quality=quality)

    @classmethod
    def from_roman_numeral(cls, numeral: str) -> 'RomanNumeral':
        if numeral not in cls.ROMAN_TO_INT:
            raise ValueError(f'Invalid roman numeral: {numeral}')
        return cls(scale_degree=cls.ROMAN_TO_INT[numeral], quality=ChordQuality.MAJOR)

    @classmethod
    def from_scale_degree(cls, degree: int, quality: Union[str, ChordQuality] = ChordQuality.MAJOR) -> 'RomanNumeral':
        """Create a RomanNumeral instance from a scale degree and quality."""
        if not (1 <= degree <= 7):
            raise ValueError("Scale degree must be between 1 and 7")

        # Convert string quality to ChordQuality enum if needed
        if isinstance(quality, str):
            try:
                quality = ChordQuality.from_string(quality)
            except ValueError:
                raise ValueError(f"Invalid quality string: {quality}")

        return cls(scale_degree=degree, quality=quality)

    def to_string(self) -> str:
        """Convert to string representation."""
        roman = self.INT_TO_ROMAN[self.scale_degree]

        if self.quality == ChordQuality.MINOR:
            roman = roman.lower()
        elif self.quality == ChordQuality.DIMINISHED:
            roman = roman.lower() + "°"
        elif self.quality == ChordQuality.DIMINISHED_SEVENTH:
            roman = roman.lower() + "°7"
        elif self.quality == ChordQuality.HALF_DIMINISHED:
            roman = roman.lower() + "ø"
        elif self.quality == ChordQuality.AUGMENTED:
            roman = roman + "+"
        elif self.quality == ChordQuality.MAJOR_SEVENTH:
            roman = roman + "Δ"
        elif self.quality == ChordQuality.DOMINANT_SEVENTH:
            roman = roman + "7"
        elif self.quality == ChordQuality.MINOR_SEVENTH:
            roman = roman.lower() + "7"

        return roman

    @classmethod
    def _get_roman_numeral(cls, degree: int, quality: ChordQuality) -> str:
        roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
        
        if degree < 1 or degree > 7:
            raise ValueError(f"Invalid degree: {degree}. Must be between 1 and 7")
        
        numeral = roman_numerals[degree - 1]
        
        # Handle different qualities
        if quality == ChordQuality.MINOR:
            numeral = numeral.lower()
        elif quality == ChordQuality.DIMINISHED:
            numeral = numeral.lower() + '°'
        elif quality == ChordQuality.AUGMENTED:
            numeral = numeral + '+'
        
        return numeral

    @classmethod
    def get_roman_numeral_from_chord(cls, chord: Chord, scale: Scale) -> 'RomanNumeral':
        logger.debug(f"Converting chord to roman numeral - chord: {chord}, scale: {scale}")
        try:
            degree = scale.get_degree_of_note(chord.root)
            logger.debug(f"Calculated degree: {degree}")
            if degree is None:
                logger.error(f"Note {chord.root.note_name} not found in scale")
                raise ValueError(f"Note {chord.root.note_name} not found in scale")
            result = cls._get_roman_numeral(degree, chord.quality)
            logger.debug(f"Generated roman numeral: {result}")
            return cls(scale_degree=degree, quality=chord.quality)
        except TypeError as e:
            raise ValueError(f"Unexpected error processing chord: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error processing chord: {str(e)}")
            raise

    @classmethod
    def to_scale_degree(cls, numeral: Union[str, 'RomanNumeral']) -> int:
        if numeral is None:
            raise ValueError('Roman numeral cannot be None')
        if isinstance(numeral, str):
            try:
                numeral = cls.from_string(numeral)
            except ValueError as e:
                raise ValueError(f'Invalid Roman numeral string: {numeral}') from e
        if not isinstance(numeral, cls):
            raise TypeError(f'Expected RomanNumeral or str, got {type(numeral)}')
        return numeral.scale_degree

    @classmethod
    def convert_to_note(cls, numeral: str, scale: Scale) -> Note:
        degree = cls.to_scale_degree(numeral)
        # Logic to get the note based on the scale and degree
        return scale.get_note_by_degree(degree)  # Assuming this method exists

    def get_note_name(self, key: str = 'C') -> str:
        """Convert the scale degree to a note name based on the key."""
        major_scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        degree = self.scale_degree - 1  # Adjust for 0-indexing
        return major_scale[degree % 7]  # Wrap around for degrees greater than 7