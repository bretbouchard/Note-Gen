"""
Module for handling Roman numeral analysis in music theory.

This module provides functionality for analyzing and representing chords and chord progressions using Roman numerals. It includes classes and functions for converting between chord representations and their corresponding Roman numeral notations.

Roman Numeral Analysis
----------------------

The `RomanNumeral` class encapsulates the representation of a chord using Roman numerals, allowing for easy conversion between chord and Roman numeral formats.

Classes:
--------

- `RomanNumeral`: Represents a Roman numeral for a chord, including its quality and methods for conversion.

Usage:
------

To create a Roman numeral representation of a chord, instantiate the `RomanNumeral` class and use its methods to convert to a chord representation:

```python
roman_numeral = RomanNumeral("I", "major")
chord = roman_numeral.to_chord()
print(chord)
```

This module is designed to be extensible, allowing for the addition of new functionalities related to Roman numeral analysis as needed.
"""

from __future__ import annotations
import re
import logging
import typing as t
from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.scale_type import ScaleType
from src.note_gen.models.enums import ChordQualityType  # Add ScaleType back
from src.note_gen.models.scale import Scale

if t.TYPE_CHECKING:
    from src.note_gen.models.scale import Scale

logger = logging.getLogger(__name__)


class RomanNumeral(BaseModel):
    scale: Scale  # Assuming Scale is defined elsewhere
    numeral_str: str = Field(
        ..., pattern="^[IiVv]+|[1-7]|(?:one|two|three|four|five|six|seven)$"
    )
    scale_degree: int = Field(..., ge=1, le=7)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("numeral_str")
    def validate_numeral(cls, value: str) -> str:
        if value not in ["I", "II", "III", "IV", "V", "VI", "VII"]:
            raise ValueError(f"Invalid numeral: {value}")
        return value

    # Update the class variable mapping to use ChordQualityType
    class_var_chord_quality_mapping: t.ClassVar[t.Dict[str, ChordQualityType]] = {
        "I": ChordQualityType.MAJOR,
        "IV": ChordQualityType.MAJOR,
        "V": ChordQualityType.MAJOR,
        "ii": ChordQualityType.MINOR,
        "iii": ChordQualityType.MINOR,
        "vi": ChordQualityType.MINOR,
        # Add more mappings as needed
    }

    WORD_TO_ROMAN: t.ClassVar[t.Dict[str, str]] = {
        "one": "I",
        "two": "II",
        "three": "III",
        "four": "IV",
        "five": "V",
        "six": "VI",
        "seven": "VII",
    }

    INT_TO_ROMAN: t.ClassVar[t.Dict[int, str]] = {
        1: "I",
        2: "II",
        3: "III",
        4: "IV",
        5: "V",
        6: "VI",
        7: "VII",
    }

    ROMAN_TO_INT: t.ClassVar[t.Dict[str, int]] = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
    }

    def __init_subclass__(cls) -> None:
        if cls.scale is None:
            raise ValueError("Scale cannot be None")
        super().__init_subclass__()
        cls.numeral_str = cls.numeral_str
        cls.numeral = cls.numeral_str
        cls.is_major = False
        cls.is_diminished = False
        cls.is_augmented = False
        cls.is_half_diminished = False
        cls.has_seventh = False
        cls.has_ninth = False
        cls.has_eleventh = False
        cls.inversion = 0
        cls.chord_notes: t.List[Note] = []

    def get_note(self) -> Note:
        note = self.scale.get_note_by_degree(self.scale_degree)
        if note is None:
            raise ValueError(
                f"Could not find note for scale degree {self.scale_degree}"
            )
        return note

    def get_notes(self) -> t.List[Note]:
        """Get the notes in this chord.

        Returns:
            t.List[Note]: The list of notes in this chord.
        """
        return self.chord_notes

    def __getattr__(self, item: str) -> Any:
        if item == "scale":
            raise AttributeError("'Note' object has no attribute 'scale'")
        return super().__getattr__(item)

    @classmethod
    def determine_root_note_from_numeral(cls, numeral_str: str) -> Note:
        """Determine the root note based on the Roman numeral string."""
        roman_to_midi = {
            "I": 60,  # C4
            "II": 62,  # D4
            "III": 64,  # E4
            "IV": 65,  # F4
            "V": 67,  # G4
            "VI": 69,  # A4
            "VII": 71,  # B4
        }

        base = numeral_str.strip().upper()
        if base in roman_to_midi:
            midi_number = roman_to_midi[base]
            return Note.from_midi(midi_number)  # Call from_midi with MIDI number only
        else:
            raise ValueError(f"Invalid Roman numeral for root note: {numeral_str}")

    @classmethod
    def from_str(
        cls, numeral_str: str, scale_type: t.Optional[ScaleType] = None
    ) -> "RomanNumeral":

        if scale_type is None:
            raise ValueError("Invalid scale provided.")

        root: Note = cls.determine_root_note_from_numeral(numeral_str)

        # Create ScaleInfo without the quality parameter
        scale_info = ScaleInfo(scale_type=str(scale_type), root=root)

        # Create the Scale using the root note and scale information
        scale = Scale(root=root, quality=scale_info.quality)

        base_match = re.match(
            r"(b?)([IiVv]+|[1-7]|(?:one|two|three|four|five|six|seven))(.*)",
            numeral_str,
        )
        if not base_match:
            raise ValueError(f"Invalid Roman numeral: {numeral_str}")

        flat, base, modifiers = base_match.groups()
        scale_degree = cls.get_scale_degree(base)

        # Get the chord quality type from mapping
        quality_type = cls.class_var_chord_quality_mapping.get(
            base, ChordQualityType.MAJOR
        )

        # Initialize chord_notes before using
        chord_notes: t.List[Note] = []

        # Define bass as the next note in the scale

        # Return the necessary parameters for chord creation
        return cls(
            scale=scale,
            numeral_str=numeral_str,
            scale_degree=scale_degree,
            numeral=base,
            is_major=quality_type == ChordQualityType.MAJOR,
            is_diminished=quality_type == ChordQualityType.DIMINISHED,
            is_augmented=quality_type == ChordQualityType.AUGMENTED,
            is_half_diminished=quality_type == ChordQualityType.HALF_DIMINISHED_7,
            has_seventh=False,
            has_ninth=False,
            has_eleventh=False,
            inversion=0,
        )

    @classmethod
    def get_scale_degree(cls, base: str) -> int:
        roman_to_degree = {
            "I": 1,
            "II": 2,
            "III": 3,
            "IV": 4,
            "V": 5,
            "VI": 6,
            "VII": 7,
        }
        return roman_to_degree.get(base.upper(), 0)

    def to_int(self) -> int:
        """Convert the Roman numeral to its integer value."""
        # Implement the logic to convert the Roman numeral to an integer
        # Use the ROMAN_TO_INT class variable to map the Roman numeral to its integer value
        return self.ROMAN_TO_INT.get(self.numeral, 0)

    def __str__(self) -> str:
        """Return the string representation of the Roman numeral.

        Returns:
            str: The Roman numeral representation.
        """
        return f"{self.numeral} ({self.get_quality()})"

    def get_quality(self) -> str:
        """Get the quality of the Roman numeral.

        Returns:
            str: The quality of the Roman numeral.
        """
        if self.is_major:
            return "major"
        elif self.is_diminished:
            return "diminished"
        elif self.is_augmented:
            return "augmented"
        elif self.is_half_diminished:
            return "half-diminished7"
        else:
            return "minor"

    def get_intervals(self) -> t.List[int]:
        """Get the intervals for this roman numeral."""
        # Implement the logic to return intervals based on the roman numeral
        return [0, 4, 7]  # Example for major chord

    @classmethod
    def some_function_that_uses_get_roman_numeral_from_chord(cls) -> None:
        pass  # Placeholder for future implementation
