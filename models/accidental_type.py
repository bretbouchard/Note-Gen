"""Module for handling musical accidentals."""
from enum import Enum

class AccidentalType(str, Enum):
    """Enum for musical accidentals."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

    @classmethod
    def combine(cls, acc1: 'AccidentalType', acc2: 'AccidentalType') -> 'AccidentalType':
        """Combine two accidentals."""
        if acc1 == cls.NATURAL:
            return acc2
        if acc2 == cls.NATURAL:
            return acc1
            
        # Handle sharps
        if acc1 == cls.SHARP and acc2 == cls.SHARP:
            return cls.DOUBLE_SHARP
        if acc1 == cls.SHARP and acc2 == cls.FLAT:
            return cls.NATURAL
            
        # Handle flats
        if acc1 == cls.FLAT and acc2 == cls.FLAT:
            return cls.DOUBLE_FLAT
        if acc1 == cls.FLAT and acc2 == cls.SHARP:
            return cls.NATURAL
            
        # Handle double accidentals
        if acc1 == cls.DOUBLE_SHARP or acc2 == cls.DOUBLE_SHARP:
            return cls.DOUBLE_SHARP
        if acc1 == cls.DOUBLE_FLAT or acc2 == cls.DOUBLE_FLAT:
            return cls.DOUBLE_FLAT
            
        return acc1  # Default case
