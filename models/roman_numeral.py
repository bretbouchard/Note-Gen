"""Module for handling roman numerals in music theory."""
from __future__ import annotations

from typing import ClassVar, Dict, Optional, Union, Any
from pydantic import BaseModel

from .note import Note
from .scale import Scale
from .scale_info import ScaleInfo
from .chord_base import ROMAN_TO_INT, QUALITY_INTERVALS, INT_TO_ROMAN, WORD_TO_ROMAN
import re

class RomanNumeral(BaseModel):
    """A class for representing Roman numerals in music theory."""
    numeral: str
    scale_degree: int
    is_major: bool = True
    is_diminished: bool = False
    is_augmented: bool = False
    is_half_diminished: bool = False
    has_seventh: bool = False
    has_ninth: bool = False
    has_eleventh: bool = False
    inversion: int = 0
    pedal_bass: Optional[str] = None
    scale: Optional[Union[Scale, ScaleInfo]] = None

    @property
    def is_flattened(self) -> bool:
        """Return whether the numeral is flattened."""
        return self.numeral.startswith('b')

    @classmethod
    def from_str(cls, numeral_str: str, scale: Optional[Union[Scale, ScaleInfo]] = None) -> 'RomanNumeral':
        """Create a RomanNumeral from a string."""
        # Store original numeral for flattened check
        original_numeral = numeral_str.strip()

        # Handle flattened numerals
        is_flattened = original_numeral.startswith('b')
        if is_flattened:
            numeral_str = original_numeral[1:].strip()
        else:
            numeral_str = original_numeral

        # Extract the base numeral (I, II, III, etc.)
        base_match = re.match(r"([IiVv]+|[1-7]|(?:one|two|three|four|five|six|seven))(.*)", numeral_str)
        if not base_match:
            raise ValueError(f"Invalid Roman numeral: {numeral_str}")

        base, modifiers = base_match.groups()
        
        # Convert numeric or word representation to Roman numeral
        if base.isdigit():
            base = INT_TO_ROMAN[int(base)]
        elif base.lower() in WORD_TO_ROMAN:
            base = WORD_TO_ROMAN[base.lower()]
        
        # Determine if major/minor from base numeral case
        is_major = base.isupper()
        
        # Get scale degree
        try:
            scale_degree = ROMAN_TO_INT[base.upper()]
        except KeyError:
            raise ValueError(f"Invalid Roman numeral: {numeral_str}")
        
        # Parse modifiers
        is_diminished = 'o' in modifiers or '°' in modifiers
        is_augmented = '+' in modifiers
        is_half_diminished = 'ø' in modifiers
        has_seventh = '7' in modifiers
        has_ninth = '9' in modifiers
        has_eleventh = '11' in modifiers

        # Handle inversions
        inversion = 0
        if '/' in modifiers:
            try:
                inversion_part = modifiers.split('/')[-1]
                if inversion_part.isdigit():
                    inversion = int(inversion_part)
            except (ValueError, IndexError):
                pass

        return cls(
            numeral=original_numeral,
            scale_degree=scale_degree,
            is_major=is_major,
            is_diminished=is_diminished,
            is_augmented=is_augmented,
            is_half_diminished=is_half_diminished,
            has_seventh=has_seventh,
            has_ninth=has_ninth,
            has_eleventh=has_eleventh,
            inversion=inversion,
            scale=scale
        )

    def get_note(self) -> Note:
        """Get the root note of this Roman numeral."""
        if not self.scale:
            raise ValueError("Scale must be set to get note")
        
        # Get the scale notes
        scale_notes = self.scale.get_scale_notes()
        
        # Get the note at the scale degree
        if self.scale_degree < 1 or self.scale_degree > len(scale_notes):
            raise ValueError(f"Invalid scale degree: {self.scale_degree}")
        
        # Get the base note
        note = scale_notes[self.scale_degree - 1].copy()
        
        # Handle flattened numerals by lowering the note by a semitone
        if self.is_flattened:
            note = note.transpose(-1)
        
        return note

    @property
    def chord_quality(self) -> str:
        """Get the chord quality."""
        # Check for specific chord qualities in order of precedence
        if self.is_diminished:
            if self.has_seventh:
                return 'diminished7'
            return 'diminished'
        if self.is_half_diminished:
            if self.has_seventh:
                return 'half-diminished7'
            return 'half-diminished'
        if self.is_augmented:
            if self.has_seventh:
                return 'augmented7'
            return 'augmented'
        
        # Handle extended chords
        if self.has_eleventh:
            return 'minor11' if not self.is_major else 'major11'
        if self.has_ninth:
            return 'minor9' if not self.is_major else 'major9'
        
        # Handle seventh chords
        if 'maj7' in self.numeral:
            return 'major7'
        if self.has_seventh:
            return 'dominant7' if self.is_major else 'minor7'
        
        # Handle suspended chords
        if 'sus' in self.numeral:
            if '4' in self.numeral:
                return '7sus4' if self.has_seventh else 'sus4'
            return '7sus2' if self.has_seventh else 'sus2'
        
        # Basic triads
        return 'major' if self.is_major else 'minor'

    def to_note(self) -> Note:
        """Convert to a note."""
        return self.get_note()

    def dict(self, *, include: Optional[Any] = None, exclude: Optional[Any] = None, 
             by_alias: bool = False, exclude_unset: bool = False, 
             exclude_defaults: bool = False, exclude_none: bool = False) -> dict[str, Any]:
        """Convert the RomanNumeral to a dictionary representation."""
        base_dict = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none
        )
        return base_dict
