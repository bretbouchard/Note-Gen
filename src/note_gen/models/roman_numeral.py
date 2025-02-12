from typing import Optional, Dict, ClassVar
from pydantic import BaseModel, ConfigDict, field_validator
import re

from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale import Scale
from src.note_gen.models.note import Note


class RomanNumeral(BaseModel):
    """A roman numeral representation of a scale degree and chord quality."""
    scale_degree: int
    quality: ChordQualityType = ChordQualityType.MAJOR
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

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

    ROMAN_TO_INT: ClassVar[Dict[str, int]] = {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
        "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
        "I7": 1, "II7": 2, "III7": 3, "IV7": 4, "V7": 5, "VI7": 6, "VII7": 7,
        "Imaj7": 1, "IImaj7": 2, "IIImaj7": 3, "IVmaj7": 4, "Vmaj7": 5, "VImaj7": 6, "VIImaj7": 7,
        "i7": 1, "ii7": 2, "iii7": 3, "iv7": 4, "v7": 5, "vi7": 6, "vii7": 7,
        "vii°7": 7,
        "Dm7": 2,
        "G7": 5,
        "Cmaj7": 1,
        "Am": 6,
        "Am7": 6,
        "D7": 4,
        "Gmaj7": 5,
        "F": 4,
        "F7": 4,
        "Fmaj7": 4,
        "Bb7": 2,
        "B": 3,
        "G": 5,
        "Eb": 4,
        "F#7": 4,
        "ii°7": 2,
        "V7alt": 5,
        "im7": 1,
        "iv7": 4,
        "v7": 5,
        "C7": 1,
        "bIII": 3,
        "bVII": 7,
        "ii♭5": 2,
        "V♭5": 5,
        "ii": 2,
        "ii7": 2,
        "IV": 4,
        "IV7": 4,
        "vi": 6,
        "vi7": 6,
        "iii": 3,
        "iii7": 3,
        "V7": 5,
        "I": 1,
        "I7": 1,
        "I♭7": 1,
        "VI♭7": 6,
        "ii♭7": 2,
        "V♭7": 5,
        "I/V": 1,
        "IV/V": 4,
        "V/V": 5,
        "VI/V": 6,
        "VII/V": 7,
        "Ebm7": 3,
        "E": 3
    }

    @field_validator('scale_degree')
    @classmethod
    def validate_scale_degree(cls, value: int) -> int:
        """Validate that scale_degree is between 1 and 7."""
        if not (1 <= value <= 7):
            raise ValueError("Scale degree must be between 1 and 7")
        return value

    @classmethod
    def from_scale_degree(cls, degree: int, quality: ChordQualityType) -> str:
        """Convert a scale degree and quality to a roman numeral string."""
        if not (1 <= degree <= 7):
            raise ValueError("Scale degree must be between 1 and 7")

        # Get the base roman numeral
        roman = cls.INT_TO_ROMAN[degree]
        
        # Apply quality modifications
        if quality == ChordQualityType.MINOR:
            roman = roman.lower()
        elif quality == ChordQualityType.DIMINISHED:
            roman = roman.lower() + "o"
        elif quality == ChordQualityType.AUGMENTED:
            roman = roman + "+"
        elif quality == ChordQualityType.MINOR7:
            roman = roman.lower() + "7"
        elif quality == ChordQualityType.MAJOR7:
            roman = roman + "Δ"
        elif quality == ChordQualityType.DOMINANT7:
            roman = roman + "7"

        return roman

    @classmethod
    def to_scale_degree(cls, numeral: str) -> int:
        """Convert a roman numeral string to a scale degree."""
        if not numeral:
            raise ValueError("Roman numeral cannot be empty")

        # Remove any quality modifiers (o, +, 7, Δ)
        base_numeral = re.match(r"^[IiVv]+", numeral)
        if not base_numeral:
            raise ValueError(f"Invalid roman numeral: {numeral}")
        
        base = base_numeral.group().upper()
        if base not in cls.ROMAN_TO_INT:
            raise ValueError(f"Invalid roman numeral: {numeral}")
        
        # Check if there are any invalid characters after the base numeral
        valid_suffixes = ["o", "+", "7", "Δ", "maj7", "°7"]
        suffix = numeral[len(base_numeral.group()):]
        if suffix and not any(suffix == s for s in valid_suffixes):
            raise ValueError(f"Invalid roman numeral: {numeral}")
        
        return cls.ROMAN_TO_INT[base]

    @classmethod
    def get_roman_numeral_from_chord(cls, chord: Chord, scale: Scale) -> str:
        """Get the roman numeral representation of a chord in a scale."""
        try:
            degree = scale.get_degree_of_note(chord.root)
            if chord.quality is None:
                raise ValueError("Chord quality cannot be None.")
            return cls.from_scale_degree(degree, chord.quality)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {str(e)}")

    @classmethod
    def from_string(cls, numeral: str) -> 'RomanNumeral':
        if numeral not in cls.ROMAN_TO_INT:
            raise ValueError(f"Invalid Roman numeral: {numeral}")
        scale_degree = cls.ROMAN_TO_INT[numeral]
        quality = ChordQualityType.MAJOR  # Default quality
        if numeral.islower():
            quality = ChordQualityType.MINOR
        return cls(scale_degree=scale_degree, quality=quality)

    def __str__(self) -> str:
        return f"RomanNumeral(scale_degree={self.scale_degree}, quality={self.quality})"

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