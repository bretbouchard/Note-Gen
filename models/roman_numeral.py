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

from typing import Optional, Dict, ClassVar, List
from pydantic import BaseModel, field_validator
import re
import logging

from .chord import Chord, ChordQuality
from .note import Note
from .scale import Scale
from .scale_info import ScaleInfo
from .scale_type import ScaleType

logger = logging.getLogger(__name__)

class RomanNumeral(BaseModel):
    scale: Scale  # Assuming Scale is defined elsewhere
    numeral_str: str
    scale_degree: int

    class Config:
        arbitrary_types_allowed = True

    class_var_chord_quality_mapping: ClassVar[Dict[str, str]] = {
        'I': 'major',
        'IV': 'major',
        'V': 'major',
        'ii': 'minor',
        'iii': 'minor',
        'vi': 'minor',
        # Add more mappings as needed
    }

    WORD_TO_ROMAN: ClassVar[Dict[str, str]] = {
        'one': 'I',
        'two': 'II',
        'three': 'III',
        'four': 'IV',
        'five': 'V',
        'six': 'VI',
        'seven': 'VII'
    }

    INT_TO_ROMAN: ClassVar[Dict[int, str]] = {
        1: 'I',
        2: 'II',
        3: 'III',
        4: 'IV',
        5: 'V',
        6: 'VI',
        7: 'VII'
    }

    ROMAN_TO_INT: ClassVar[Dict[str, int]] = {
        'I': 1,
        'II': 2,
        'III': 3,
        'IV': 4,
        'V': 5,
        'VI': 6,
        'VII': 7
    }

    def __init__(self, scale: Scale, numeral: str, numeral_str: str, scale_degree: int, is_major: bool, 
                 is_diminished: bool, is_augmented: bool, is_half_diminished: bool, 
                 has_seventh: bool, has_ninth: bool, has_eleventh: bool, inversion: int):
        if scale is None:
            raise ValueError("Scale cannot be None")
        self.scale = scale
        self.numeral = numeral
        self.numeral_str = numeral_str
        self.scale_degree = scale_degree
        self.is_major = is_major
        self.is_diminished = is_diminished
        self.is_augmented = is_augmented
        self.is_half_diminished = is_half_diminished
        self.has_seventh = has_seventh
        self.has_ninth = has_ninth
        self.has_eleventh = has_eleventh
        self.inversion = inversion
        self.chord_notes: List[Note] = []

    def get_note(self) -> Optional[Note]:
        """Get the corresponding note based on the Roman numeral and scale."""
        if self.scale is None:
            logger.error("Scale is None, cannot get note.")
            return None
        note = self.scale.get_note_by_degree(self.scale_degree)
        return note  # Ensure this returns a Note type

    def get_notes(self) -> List[Note]:
        """Get the notes in this chord."""
        logger.debug("get_notes called")
        return self.chord_notes

    @field_validator('numeral')
    def validate_numeral(cls, value: str) -> str:
        if value not in cls.class_var_chord_quality_mapping:
            raise ValueError(f"Invalid Roman numeral: {value}. Must be one of: {', '.join(cls.class_var_chord_quality_mapping.keys())}.")
        return value

    @classmethod
    def determine_root_note_from_numeral(cls, numeral_str: str) -> Note:
        """Determine the root note based on the Roman numeral string.

        Args:
            numeral_str (str): The Roman numeral string.

        Returns:
            Note: The corresponding root note for the scale.
        """
        # Define a mapping from Roman numerals to root notes
        roman_to_note = {
            'I': 'C',
            'II': 'D',
            'III': 'E',
            'IV': 'F',
            'V': 'G',
            'VI': 'A',
            'VII': 'B',
            # Add more mappings as needed
        }

        # Normalize the numeral string
        base = numeral_str.strip().upper()

        # Get the corresponding note
        if base in roman_to_note:
            note_name = roman_to_note[base]
            return Note.from_name(note_name)  # Assuming Note has a method to create from name
        else:
            raise ValueError(f"Invalid Roman numeral for root note: {numeral_str}")

    @classmethod
    def from_str(cls, numeral_str: str, scale_type: Optional[ScaleType] = None) -> 'RomanNumeral':
        if scale_type is None:
            raise ValueError("Invalid scale provided.")

        root: Note = cls.determine_root_note_from_numeral(numeral_str)

        # Create ScaleInfo without the quality parameter
        scale_info = ScaleInfo(scale_type=str(scale_type), root=root)  

        # Create the Scale using the root note and scale information
        scale = Scale(root=root, quality=scale_info.quality)

        base_match = re.match(r"(b?)([IiVv]+|[1-7]|(?:one|two|three|four|five|six|seven))(.*)", numeral_str)
        if not base_match:
            raise ValueError(f"Invalid Roman numeral: {numeral_str}")

        flat, base, modifiers = base_match.groups()
        scale_degree = cls.get_scale_degree(base)

        # Determine chord quality based on the base
        chord_quality = ChordQuality(cls.class_var_chord_quality_mapping.get(base, ChordQuality.major))  

        # Define bass as the next note in the scale
        bass: Note = Note.from_midi(root.midi_number + 2)  # Example logic for bass

        # Create the corresponding Chord based on the scale and degree
        chord_notes: List[Note] = []  
        chord = Chord(root=root, quality=chord_quality, notes=chord_notes, bass=bass)

        # Create and return the RomanNumeral instance
        return cls(scale=scale, numeral_str=numeral_str, scale_degree=scale_degree, numeral=base, 
                   is_major=chord_quality == ChordQuality.major, 
                   is_diminished=chord_quality == ChordQuality.diminished, 
                   is_augmented=chord_quality == ChordQuality.augmented, 
                   is_half_diminished=chord_quality == ChordQuality.half_diminished7, 
                   has_seventh=False, has_ninth=False, has_eleventh=False, inversion=0)

    @classmethod
    def get_scale_degree(cls, base: str) -> int:
        roman_to_degree = {
            'I': 1,
            'II': 2,
            'III': 3,
            'IV': 4,
            'V': 5,
            'VI': 6,
            'VII': 7,
        }
        return roman_to_degree.get(base.upper(), 0)

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
