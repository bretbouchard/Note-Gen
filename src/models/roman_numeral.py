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
from pydantic import BaseModel, ConfigDict

from src.models.note import Note
from src.models.scale_info import ScaleInfo
from src.models.scale_type import ScaleType
from src.models.enums import ChordQualityType  # Add ScaleType back


if t.TYPE_CHECKING:
    from src.models.scale import Scale
    from src.models.chord import Chord

logger = logging.getLogger(__name__)

class RomanNumeral(BaseModel):
    scale: Scale  # Assuming Scale is defined elsewhere
    numeral_str: str
    scale_degree: int

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Update the class variable mapping to use ChordQualityType
    class_var_chord_quality_mapping: t.ClassVar[t.Dict[str, ChordQualityType]] = {
        'I': ChordQualityType.MAJOR,
        'IV': ChordQualityType.MAJOR,
        'V': ChordQualityType.MAJOR,
        'ii': ChordQualityType.MINOR,
        'iii': ChordQualityType.MINOR,
        'vi': ChordQualityType.MINOR,
        # Add more mappings as needed
    }

    WORD_TO_ROMAN: t.ClassVar[t.Dict[str, str]] = {
        'one': 'I',
        'two': 'II',
        'three': 'III',
        'four': 'IV',
        'five': 'V',
        'six': 'VI',
        'seven': 'VII'
    }

    INT_TO_ROMAN: t.ClassVar[t.Dict[int, str]] = {
        1: 'I',
        2: 'II',
        3: 'III',
        4: 'IV',
        5: 'V',
        6: 'VI',
        7: 'VII'
    }

    ROMAN_TO_INT: t.ClassVar[t.Dict[str, int]] = {
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
        self.chord_notes: t.List[Note] = []

    def get_note(self) -> Note:
        note = self.scale.get_note_by_degree(self.scale_degree)
        if note is None:
            raise ValueError(f"Could not find note for scale degree {self.scale_degree}")
        return note
    
    def get_notes(self) -> t.List[Note]:
        """Get the notes in this chord.
        
        Returns:
            t.List[Note]: The list of notes in this chord.
        """
        return self.chord_notes

    @classmethod
    def validate_numeral(cls, value: str) -> str:
        if value not in cls.class_var_chord_quality_mapping:
            raise ValueError(f"Invalid Roman numeral: {value}. Must be one of: {', '.join(cls.class_var_chord_quality_mapping.keys())}.")
        return value

    @classmethod
    def determine_root_note_from_numeral(cls, numeral_str: str) -> Note:
        """Determine the root note based on the Roman numeral string."""
        roman_to_midi = {
            'I': 60,  # C4
            'II': 62,  # D4
            'III': 64,  # E4
            'IV': 65,  # F4
            'V': 67,  # G4
            'VI': 69,  # A4
            'VII': 71,  # B4
        }

        base = numeral_str.strip().upper()
        if base in roman_to_midi:
            midi_number = roman_to_midi[base]
            return Note.from_midi(midi_number)  # Call from_midi with MIDI number only
        else:
            raise ValueError(f"Invalid Roman numeral for root note: {numeral_str}")

    @classmethod
    def from_str(cls, numeral_str: str, scale_type: t.Optional[ScaleType] = None) -> "RomanNumeral":
        from src.models.chord import Chord, ChordQuality  # Add imports
        from src.models.chord_roman_utils import get_roman_numeral_from_chord
    
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
        
        # Get the chord quality type from mapping
        quality_type = cls.class_var_chord_quality_mapping.get(base, ChordQualityType.MAJOR)
        
        # Initialize chord_notes before using
        chord_notes: t.List[Note] = []
        
        # Define bass as the next note in the scale
        bass: Note = Note.from_midi(root.midi_number + 2)  # Removed name argument
        
        # Create chord with proper ChordQuality
        chord = Chord(
            root=root,
            quality = ChordQuality(quality=quality_type),
            notes=chord_notes,
            bass=bass
        )
        
        # Create and return the RomanNumeral instance
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
            inversion=0
        )

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

    def get_intervals(self) -> t.List[int]:
        """Get the intervals for this roman numeral."""
        # Implement the logic to return intervals based on the roman numeral
        return [0, 4, 7]  # Example for major chord

    @classmethod
    def some_function_that_uses_get_roman_numeral_from_chord(cls) -> None:
        pass  # Placeholder for future implementation