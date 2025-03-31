"""Core constants for the application."""

# Note Constants
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
VALID_KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FULL_NOTE_REGEX = r'^[A-G][#b]?$'  # Changed to match just the note without octave
NOTE_WITH_OCTAVE_REGEX = r'^[A-G][#b]?\d$'  # For when we need to match notes with octaves

# Note to Semitone mapping
NOTE_TO_SEMITONE = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11
}

# Semitone to Note mapping (using sharps by default)
SEMITONE_TO_NOTE = {
    0: 'C',
    1: 'C#',
    2: 'D',
    3: 'D#',
    4: 'E',
    5: 'F',
    6: 'F#',
    7: 'G',
    8: 'G#',
    9: 'A',
    10: 'A#',
    11: 'B'
}

# Scale Degree Qualities
SCALE_DEGREE_QUALITIES = {
    1: 'maj',  # I
    2: 'min',  # ii
    3: 'min',  # iii
    4: 'maj',  # IV
    5: 'maj',  # V
    6: 'min',  # vi
    7: 'dim'   # vii°
}

from .enums import ChordQuality

# Default chord qualities for scale degrees in major scale
DEFAULT_SCALE_DEGREE_QUALITIES = {
    1: ChordQuality.MAJOR,
    2: ChordQuality.MINOR,
    3: ChordQuality.MINOR,
    4: ChordQuality.MAJOR,
    5: ChordQuality.MAJOR,
    6: ChordQuality.MINOR,
    7: ChordQuality.DIMINISHED
}

# MIDI Constants
MIDI_MIN = 0
MIDI_MAX = 127
MIDI_MIDDLE_C = 60

# Duration and Pattern Validation Limits
DURATION_LIMITS = {
    'MIN': 0.0625,  # 1/16th note
    'MAX': 8.0,     # 8 whole notes
    'DEFAULT': 1.0  # quarter note
}

PATTERN_VALIDATION_LIMITS = {
    'MIN_OCTAVE': -1,
    'MAX_OCTAVE': 9,
    'DEFAULT_OCTAVE_RANGE': (4, 5),
    'MAX_INTERVAL_JUMP': 12,
    'MIN_DURATION': DURATION_LIMITS['MIN'],
    'MAX_DURATION': DURATION_LIMITS['MAX']
}

# Scale and Chord Constants
ROMAN_QUALITY_MAP = {
    'maj': '',      # Major
    'min': 'm',     # Minor
    'dim': '°',     # Diminished
    'aug': '+',     # Augmented
    'dom7': '7',    # Dominant 7th
    'maj7': 'M7',   # Major 7th
    'min7': 'm7',   # Minor 7th
    'dim7': '°7',   # Diminished 7th
    'hdim7': 'ø7'   # Half-diminished 7th
}

# Roman Numeral Constants
ROMAN_TO_INT = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
    'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7
}

INT_TO_ROMAN = {
    1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'
}

# Regular expression pattern for Roman numerals with optional quality modifiers
ROMAN_NUMERAL_PATTERN = r'^(b?)([iv]+|[IV]+)(°|\+|[Mm])?[0-9]?$'

# Default Values
DEFAULTS = {
    "key": "C",
    "scale_type": "major",
    "bpm": 120,
    "time_signature": "4/4",
    "octave": 4,
    "velocity": 64,
    "duration": 1.0,
    "pattern_length": 4,
    "chord_progression": "I-IV-V",
    "note_pattern": "Simple Triad",
    "rhythm_pattern": "basic_4_4"
}

from ..core.enums import ScaleType

# Scale Intervals - Complete mapping for all scale types
SCALE_INTERVALS = {
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

# Database Configuration
DATABASE = {
    "host": "localhost",
    "port": 27017,
    "name": "note_gen",
    "username": "",
    "password": "",
    "auth_source": "admin",
    "mechanism": "SCRAM-SHA-256",
    "uri": "mongodb://localhost:27017",
    "timeout_ms": 5000,
    "pool": {
        "max_size": 10,
        "min_size": 1
    }
}

# Use this instead of DEFAULT_DB_NAME
DB_NAME = DATABASE["name"]
DEFAULT_DB_NAME = DB_NAME  # For backward compatibility

# Collection Names
COLLECTION_NAMES = {
    "patterns": "patterns",
    "users": "users",
    "chord_progressions": "chord_progressions"
}

# Rate Limiting
RATE_LIMIT = {
    "times": 100,
    "seconds": 60
}

# Common Chord Progressions
COMMON_PROGRESSIONS = [
    ['I', 'IV', 'V'],
    ['I', 'V', 'vi', 'IV'],
    ['ii', 'V', 'I'],
    ['I', 'vi', 'IV', 'V']
]

# Pattern Constants
NOTE_PATTERNS = {
    "basic_scale": {
        "intervals": [0, 2, 4, 5, 7, 9, 11, 12],
        "pattern": [1, 2, 3, 4, 5, 6, 7, 8],
        "description": "Basic ascending scale pattern",
        "tags": ["scale", "basic"],
        "complexity": 0.3,
        "index": 0
    },
    "simple_triad": {
        "intervals": [0, 4, 7],
        "pattern": [1, 3, 5],
        "description": "Simple triad arpeggio",
        "tags": ["arpeggio", "basic"],
        "complexity": 0.2,
        "index": 1
    }
}

RHYTHM_PATTERNS = {
    "default": ["4n", "8n", "16n"],
    "basic_4_4": ["4n", "4n", "4n", "4n"],
    "basic_waltz": ["2n", "4n", "4n"],
    "syncopated": ["8n", "8n", "4n", "8n", "8n"]
}

def validate_constants():
    """Validate that all required constants are present and properly formatted."""
    required_constants = [
        'DATABASE', 'DB_NAME', 'COLLECTION_NAMES', 'RATE_LIMIT',
        'ROMAN_TO_INT', 'INT_TO_ROMAN', 'SCALE_DEGREE_QUALITIES',
        'COMMON_PROGRESSIONS', 'NOTE_PATTERNS', 'RHYTHM_PATTERNS'
    ]
    
    for const in required_constants:
        if not globals().get(const):
            raise ValueError(f"Missing required constant: {const}")
    
    return True

def validate_scale_intervals():
    """Validate that all scale types have corresponding intervals."""
    missing_scales = [scale for scale in ScaleType if scale not in SCALE_INTERVALS]
    if missing_scales:
        raise ValueError(f"Missing intervals for scale types: {missing_scales}")
    return True
