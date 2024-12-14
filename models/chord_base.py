"""Base definitions for chord-related functionality."""
from typing import Dict, List, Optional
from pydantic import BaseModel
from .note import Note

# Mapping of Roman numerals to integer scale degrees
ROMAN_TO_INT = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7
}

# Mapping of integers to Roman numerals
INT_TO_ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"
}

# Mapping of words to Roman numerals
WORD_TO_ROMAN = {
    "one": "I", "two": "II", "three": "III", "four": "IV",
    "five": "V", "six": "VI", "seven": "VII"
}

# Mapping of chord qualities to their intervals
QUALITY_INTERVALS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented": [0, 4, 8],
    "dominant7": [0, 4, 7, 10],
    "major7": [0, 4, 7, 11],
    "minor7": [0, 3, 7, 10],
    "diminished7": [0, 3, 6, 9],
    "half-diminished7": [0, 3, 6, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7]
}

CHORD_INTERVALS: Dict[str, List[int]] = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'diminished': [0, 3, 6],
    'augmented': [0, 4, 8],
    'major7': [0, 4, 7, 11],
    'minor7': [0, 3, 7, 10],
    'dominant7': [0, 4, 7, 10],
    'diminished7': [0, 3, 6, 9],
    'half-diminished7': [0, 3, 6, 10],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'power': [0, 7],
    'major6': [0, 4, 7, 9],
    'minor6': [0, 3, 7, 9],
    'major9': [0, 4, 7, 11, 14],
    'minor9': [0, 3, 7, 10, 14],
    'dominant9': [0, 4, 7, 10, 14],
    'major11': [0, 4, 7, 11, 14, 17],
    'minor11': [0, 3, 7, 10, 14, 17],
    'dominant11': [0, 4, 7, 10, 14, 17]
}

CHORD_SYMBOLS: Dict[str, str] = {
    'major': '',
    'minor': 'm',
    'diminished': 'dim',
    'augmented': 'aug',
    'major7': 'maj7',
    'minor7': 'm7',
    'dominant7': '7',
    'diminished7': 'dim7',
    'half-diminished7': 'ø7',
    'sus2': 'sus2',
    'sus4': 'sus4',
    'power': '5',
    'major6': '6',
    'minor6': 'm6',
    'major9': 'maj9',
    'minor9': 'm9',
    'dominant9': '9',
    'major11': 'maj11',
    'minor11': 'm11',
    'dominant11': '11'
}

class ChordBase(BaseModel):
    notes: List[Note]
    duration: Optional[float] = None
    velocity: Optional[int] = None
