from typing import Optional, Dict, ClassVar
from pydantic import BaseModel, ConfigDict, field_validator
import re

from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale import Scale


class RomanNumeral(BaseModel):
    """A roman numeral representation of a scale degree and chord quality."""
    scale_degree: int
    quality: Optional[ChordQualityType] = ChordQualityType.MAJOR

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
        "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7
    }

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        validate_assignment=True
    )

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
        valid_suffixes = ["o", "+", "7", "Δ"]
        suffix = numeral[len(base_numeral.group()):]
        if suffix and not any(suffix == s for s in valid_suffixes):
            raise ValueError(f"Invalid roman numeral: {numeral}")
        
        return cls.ROMAN_TO_INT[base]

    @classmethod
    def get_roman_numeral_from_chord(cls, chord: Chord, scale: Scale) -> str:
        """Get the roman numeral representation of a chord in a scale."""
        try:
            degree = scale.get_degree_of_note(chord.root)
            return cls.from_scale_degree(degree, chord.quality)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {str(e)}")

    def __str__(self) -> str:
        return f"RomanNumeral(scale_degree={self.scale_degree}, quality={self.quality})"