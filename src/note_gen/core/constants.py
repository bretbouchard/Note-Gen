"""Core constants for the application."""

from .enums import ScaleType, ChordQuality, PatternDirection

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
COMMON_PROGRESSIONS = {
    "pop": {
        "name": "Pop Progression",
        "description": "Common pop progression I-vi-IV-V",
        "chords": [
            {"root": "C", "quality": "MAJOR"},
            {"root": "Am", "quality": "MINOR"},
            {"root": "F", "quality": "MAJOR"},
            {"root": "G", "quality": "MAJOR"}
        ]
    }
    # Add other progressions as needed
}

# Pattern Constants
NOTE_PATTERNS = {
    "basic_scale": {
        "intervals": [0, 2, 4, 5, 7, 9, 11, 12],
        "pattern": [1, 2, 3, 4, 5, 6, 7, 8],
        "description": "Basic ascending scale pattern",
        "direction": PatternDirection.UP,
        "tags": ["scale", "basic"],
        "complexity": 0.3,
        "index": 0
    },
    "simple_triad": {
        "intervals": [0, 4, 7],
        "pattern": [1, 3, 5],
        "description": "Simple triad arpeggio",
        "direction": PatternDirection.UP,
        "tags": ["arpeggio", "basic"],
        "complexity": 0.2,
        "index": 1
    }
}

RHYTHM_PATTERNS = {
    "default": {
        "notes": ["4n", "8n", "16n"],
        "total_duration": 1.75,  # 1.0 + 0.5 + 0.25
        "description": "Default rhythm pattern with quarter, eighth, and sixteenth notes"
    },
    "basic_4_4": {
        "notes": ["4n", "4n", "4n", "4n"],
        "total_duration": 4.0,
        "description": "Basic 4/4 rhythm with quarter notes"
    },
    "basic_waltz": {
        "notes": ["2n", "4n", "4n"],
        "total_duration": 3.0,
        "description": "Basic 3/4 waltz rhythm"
    },
    "syncopated": {
        "notes": ["8n", "8n", "4n", "8n", "8n"],
        "total_duration": 2.0,
        "description": "Syncopated rhythm pattern"
    }
}

# Chord Intervals
CHORD_INTERVALS = {
    ChordQuality.MAJOR: (0, 4, 7),
    ChordQuality.MINOR: (0, 3, 7),
    ChordQuality.DIMINISHED: (0, 3, 6),
    ChordQuality.AUGMENTED: (0, 4, 8),
    ChordQuality.MAJOR_SEVENTH: (0, 4, 7, 11),
    ChordQuality.MINOR_SEVENTH: (0, 3, 7, 10),
    ChordQuality.DOMINANT_SEVENTH: (0, 4, 7, 10),
    ChordQuality.DIMINISHED_SEVENTH: (0, 3, 6, 9),
    ChordQuality.HALF_DIMINISHED_SEVENTH: (0, 3, 6, 10)
}

def validate_constants():
    """Validate that all required constants are present and properly formatted."""
    # Validate scale intervals
    for scale_type, intervals in SCALE_INTERVALS.items():
        # Check type is tuple
        assert isinstance(intervals, tuple), f"Scale intervals for {scale_type} must be a tuple"
        
        # Check all elements are integers
        assert all(isinstance(i, int) for i in intervals), f"Scale intervals for {scale_type} must be integers"
        
        # Check range
        assert all(0 <= i <= 11 for i in intervals), f"Scale intervals for {scale_type} must be between 0 and 11"
        
        # Check length
        if scale_type == ScaleType.CHROMATIC:
            assert len(intervals) == 12, "Chromatic scale must have 12 notes"
        else:
            assert len(intervals) == 7, f"Diatonic scale {scale_type} must have 7 notes"

    # Validate common progressions
    for prog_name, prog_data in COMMON_PROGRESSIONS.items():
        assert isinstance(prog_data, dict), f"Progression {prog_name} must be a dictionary"
        
        # Check required keys
        required_keys = {'name', 'description', 'chords'}
        assert all(key in prog_data for key in required_keys), f"Progression {prog_name} missing required keys: {required_keys}"
        
        # Validate chords list
        assert isinstance(prog_data['chords'], list), f"Progression {prog_name} chords must be a list"
        
        # Validate each chord
        for chord in prog_data['chords']:
            assert isinstance(chord, dict), f"Invalid chord format in progression {prog_name}"
            assert 'root' in chord and 'quality' in chord, f"Invalid chord format in progression {prog_name}"

    # Validate note patterns
    for pattern_name, pattern_data in NOTE_PATTERNS.items():
        assert isinstance(pattern_data, dict), f"Note pattern {pattern_name} must be a dictionary"
        required_keys = {'direction', 'intervals', 'description'}
        assert all(key in pattern_data for key in required_keys), f"Note pattern {pattern_name} missing required keys"

    # Validate rhythm patterns
    for pattern_name, pattern_data in RHYTHM_PATTERNS.items():
        assert isinstance(pattern_data, dict), f"Rhythm pattern {pattern_name} must be a dictionary"
        required_keys = {'notes', 'total_duration', 'description'}
        assert all(key in pattern_data for key in required_keys), f"Rhythm pattern {pattern_name} missing required keys"

    # Validate chord intervals
    for quality, intervals in CHORD_INTERVALS.items():
        assert isinstance(intervals, tuple), f"Chord intervals for {quality} must be a tuple"
        assert all(isinstance(i, int) for i in intervals), f"Chord intervals for {quality} must be integers"
        assert all(0 <= i <= 11 for i in intervals), f"Chord intervals for {quality} must be between 0 and 11"

    return True

def validate_scale_intervals():
    """Validate that all scale types have corresponding intervals."""
    missing_scales = [scale for scale in ScaleType if scale not in SCALE_INTERVALS]
    if missing_scales:
        raise ValueError(f"Missing intervals for scale types: {missing_scales}")
    return True

MIDI_NOTE_NUMBERS = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
