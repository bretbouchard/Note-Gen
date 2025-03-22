"""Constants for the Note Generator application."""
from typing import Dict, List, Tuple
from .enums import ScaleType, PatternDirection, ChordQuality
import re

# MIDI Constants
MIDI_MIN = 0
MIDI_MAX = 127

# Note Validation Constants
FULL_NOTE_REGEX = re.compile(r'^([A-G][b#]?)(\d+)?$')
NOTE_LETTER_REGEX = re.compile(r'^[A-G]$')
ACCIDENTAL_REGEX = re.compile(r'^[b#]$')

# Default Values
DEFAULT_KEY = "C"
DEFAULT_SCALE_TYPE = "MAJOR"
DEFAULT_OCTAVE = 4
DEFAULT_VELOCITY = 64
DEFAULT_DURATION = 1.0
DEFAULT_BPM = 120
DEFAULT_TIME_SIGNATURE = "4/4"

# MIDI Constants
MIDI_MIN = 0
MIDI_MAX = 127
MIDI_MIDDLE_C = 60

# Duration Constants
DURATION_WHOLE = 4.0
DURATION_HALF = 2.0
DURATION_QUARTER = 1.0
DURATION_EIGHTH = 0.5
DURATION_SIXTEENTH = 0.25
DURATION_THIRTYSECOND = 0.125

DURATION_NAMES = {
    4.0: "whole",
    2.0: "half",
    1.0: "quarter",
    0.5: "eighth",
    0.25: "sixteenth",
    0.125: "thirty-second"
}

MIN_DURATION = DURATION_THIRTYSECOND
MAX_DURATION = 32.0

# Range Constants
MIN_OCTAVE = 0
MAX_OCTAVE = 8
MIN_VELOCITY = 0
MAX_VELOCITY = 127
MAX_CHORDS = 16

# Time Signature Constants
COMMON_TIME_SIGNATURES = [
    "4/4", "3/4", "2/4", "6/8", "9/8", "12/8"
]

# Valid Musical Keys
VALID_KEYS = [
    "C", "G", "D", "A", "E", "B", "F#", "C#",
    "F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"
]

# Chord Constants
CHORD_QUALITIES = [
    "major",
    "minor",
    "diminished",
    "augmented",
    "dominant7",
    "major7",
    "minor7",
    "half-diminished7",
    "diminished7"
]

CHORD_INTERVALS = {
    ChordQuality.MAJOR: (0, 4, 7),
    ChordQuality.MINOR: (0, 3, 7),
    ChordQuality.DIMINISHED: (0, 3, 6),
    ChordQuality.AUGMENTED: (0, 4, 8),
    ChordQuality.MAJOR7: (0, 4, 7, 11),
    ChordQuality.MINOR7: (0, 3, 7, 10),
    ChordQuality.DOMINANT7: (0, 4, 7, 10),
    ChordQuality.DIMINISHED7: (0, 3, 6, 9),
    ChordQuality.HALF_DIMINISHED7: (0, 3, 6, 10),
    ChordQuality.MAJOR9: (0, 4, 7, 11, 2),
    ChordQuality.MINOR9: (0, 3, 7, 10, 2),
    ChordQuality.MAJOR_SEVENTH: (0, 4, 7, 11),
    ChordQuality.MINOR_SEVENTH: (0, 3, 7, 10),
    ChordQuality.DOMINANT_SEVENTH: (0, 4, 7, 10),
}

ENHARMONIC_EQUIVALENTS = {
    "C#": ("C#", "Db"),
    "D#": ("D#", "Eb"),
    "F#": ("F#", "Gb"),
    "G#": ("G#", "Ab"),
    "A#": ("A#", "Bb")
}

# Pattern Constants
NOTE_PATTERNS = {
    "ascending": {
        "direction": PatternDirection.UP,
        "intervals": [0, 2, 4, 5, 7, 9, 11],
        "description": "Basic ascending scale pattern"
    },
    "descending": {
        "direction": PatternDirection.DOWN,
        "intervals": [11, 9, 7, 5, 4, 2, 0],
        "description": "Basic descending scale pattern"
    },
    "arpeggiated": {
        "direction": PatternDirection.UP,
        "intervals": [0, 4, 7],
        "description": "Basic triad arpeggio"
    }
}

RHYTHM_PATTERNS = {
    "basic_quarter": {
        "notes": [(0, 1.0), (1, 1.0), (2, 1.0), (3, 1.0)],
        "total_duration": 4.0,
        "description": "Simple quarter note pattern"
    },
    "basic_eighth": {
        "notes": [(i * 0.5, 0.5) for i in range(8)],
        "total_duration": 4.0,
        "description": "Simple eighth note pattern"
    },
    "syncopated": {
        "notes": [(0, 1.5), (1.5, 0.5), (2, 1.5), (3.5, 0.5)],
        "total_duration": 4.0,
        "description": "Basic syncopated pattern"
    }
}

# Common chord progressions
COMMON_PROGRESSIONS = {
    "I-IV-V": {
        "name": "I-IV-V",
        "description": "Basic major progression",
        "chords": [
            {"root": 1, "quality": ChordQuality.MAJOR},
            {"root": 4, "quality": ChordQuality.MAJOR},
            {"root": 5, "quality": ChordQuality.MAJOR}
        ],
        "tags": ["basic", "major"]
    },
    "ii-V-I": {
        "name": "ii-V-I",
        "description": "Common jazz progression",
        "chords": [
            {"root": 2, "quality": ChordQuality.MINOR},
            {"root": 5, "quality": ChordQuality.MAJOR},
            {"root": 1, "quality": ChordQuality.MAJOR}
        ],
        "tags": ["jazz", "major"]
    },
    "I-vi-IV-V": {
        "name": "I-vi-IV-V",
        "description": "50s progression",
        "chords": [
            {"root": 1, "quality": ChordQuality.MAJOR},
            {"root": 6, "quality": ChordQuality.MINOR},
            {"root": 4, "quality": ChordQuality.MAJOR},
            {"root": 5, "quality": ChordQuality.MAJOR}
        ],
        "tags": ["pop", "major"]
    }
}

# Add SCALE_INTERVALS constant
SCALE_INTERVALS: Dict[ScaleType, Tuple[int, ...]] = {
    ScaleType.MAJOR: (0, 2, 4, 5, 7, 9, 11),
    ScaleType.MINOR: (0, 2, 3, 5, 7, 8, 10),
    ScaleType.HARMONIC_MINOR: (0, 2, 3, 5, 7, 8, 11),
    ScaleType.MELODIC_MINOR: (0, 2, 3, 5, 7, 9, 11),
    ScaleType.DORIAN: (0, 2, 3, 5, 7, 9, 10),
    ScaleType.PHRYGIAN: (0, 1, 3, 5, 7, 8, 10),
    ScaleType.LYDIAN: (0, 2, 4, 6, 7, 9, 11),
    ScaleType.MIXOLYDIAN: (0, 2, 4, 5, 7, 9, 10),
    ScaleType.LOCRIAN: (0, 1, 3, 5, 6, 8, 10),
    ScaleType.CHROMATIC: tuple(range(12))
}

# Database Constants
DEFAULT_MONGODB_URI = "mongodb://localhost:27017"
DEFAULT_DB_NAME = "note_gen"
DEFAULT_CONNECTION_TIMEOUT_MS = 5000
MAX_POOL_SIZE = 100
MIN_POOL_SIZE = 10

# Collection Names
COLLECTION_NAMES = {
    'chord_progressions': 'chord_progressions',
    'rhythm_patterns': 'rhythm_patterns',
    'note_patterns': 'note_patterns'
}

# Basic music notes (without accidentals)
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Roman numerals for chord degrees (both uppercase and lowercase)
ROMAN_NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII", 
                 "i", "ii", "iii", "iv", "v", "vi", "vii"]

# Mapping from shorthand chord symbols to chord qualities
QUALITY_MAPPING = {
    "": ChordQuality.MAJOR,
    "M": ChordQuality.MAJOR,
    "maj": ChordQuality.MAJOR,
    "m": ChordQuality.MINOR,
    "min": ChordQuality.MINOR,
    "-": ChordQuality.MINOR,
    "dim": ChordQuality.DIMINISHED,
    "°": ChordQuality.DIMINISHED,
    "aug": ChordQuality.AUGMENTED,
    "+": ChordQuality.AUGMENTED,
    "7": ChordQuality.DOMINANT7,
    "dom7": ChordQuality.DOMINANT7,
    "maj7": ChordQuality.MAJOR7,
    "M7": ChordQuality.MAJOR7,
    "m7": ChordQuality.MINOR7,
    "min7": ChordQuality.MINOR7,
    "-7": ChordQuality.MINOR7,
    "dim7": ChordQuality.DIMINISHED7,
    "°7": ChordQuality.DIMINISHED7,
    "m7b5": ChordQuality.HALF_DIMINISHED7,
    "ø": ChordQuality.HALF_DIMINISHED7,
    "ø7": ChordQuality.HALF_DIMINISHED7,
    "maj9": ChordQuality.MAJOR9,
    "M9": ChordQuality.MAJOR9,
    "m9": ChordQuality.MINOR9,
    "min9": ChordQuality.MINOR9,
}

# API Constants
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
RATE_LIMIT = 100  # requests per minute

# Other Constants
DEFAULT_KEY = "C"
DEFAULT_SCALE_TYPE = "MAJOR"

def validate_constants():
    """Validate all constant values."""
    # Validate scale intervals
    for scale_type, intervals in SCALE_INTERVALS.items():
        if not isinstance(intervals, tuple):
            raise AssertionError(f"Intervals for {scale_type} must be a tuple")
        
        if not all(isinstance(i, int) for i in intervals):
            raise AssertionError(f"All intervals for {scale_type} must be integers")
        
        if not all(0 <= i <= 11 for i in intervals):
            raise AssertionError("Scale intervals must be between 0 and 11")
        
        if scale_type == ScaleType.CHROMATIC:
            if len(intervals) != 12:
                raise AssertionError("Chromatic scale must have 12 notes")
        elif len(intervals) != 7:
            raise AssertionError(f"Diatonic scale {scale_type} must have 7 notes")

    # Validate note patterns
    for pattern_name, pattern in NOTE_PATTERNS.items():
        if not isinstance(pattern, dict):
            raise AssertionError(f"Pattern {pattern_name} must be a dictionary")
        required_keys = {"direction", "intervals", "description"}
        if not all(key in pattern for key in required_keys):
            raise AssertionError(f"Pattern {pattern_name} missing required keys")

    # Validate rhythm patterns
    for pattern_name, pattern in RHYTHM_PATTERNS.items():
        if not isinstance(pattern, dict):
            raise AssertionError(f"Rhythm pattern {pattern_name} must be a dictionary")
        required_keys = {"notes", "total_duration", "description"}
        if not all(key in pattern for key in required_keys):
            raise AssertionError(f"Rhythm pattern {pattern_name} missing required keys")

    # Validate chord intervals
    for quality, intervals in CHORD_INTERVALS.items():
        if not isinstance(intervals, tuple):
            raise AssertionError(f"Chord intervals for {quality} must be a tuple")
        if not all(isinstance(i, int) for i in intervals):
            raise AssertionError(f"All chord intervals for {quality} must be integers")
        if not all(0 <= i <= 11 for i in intervals):
            raise AssertionError(f"Chord intervals for {quality} must be between 0 and 11")

    # Validate chord progressions
    for name, progression in COMMON_PROGRESSIONS.items():
        if not isinstance(progression, dict):
            raise AssertionError(f"Progression {name} must be a dictionary")
        
        required_keys = {"name", "description", "chords"}
        if not all(key in progression for key in required_keys):
            raise AssertionError(f"Progression {name} missing required keys")
        
        if not isinstance(progression["chords"], list):
            raise AssertionError(f"Progression {name} chords must be a list")
            
        for chord in progression["chords"]:
            if not isinstance(chord, dict) or "root" not in chord or "quality" not in chord:
                raise AssertionError(f"Invalid chord format in progression {name}")
