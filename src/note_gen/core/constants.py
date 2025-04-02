"""Constants for note generation."""
from typing import Dict, Any
from src.note_gen.core.enums import ScaleType, ChordQuality, PatternDirection

# Note-related constants
FULL_NOTE_REGEX = r'^[A-G][#b]?[0-9]$'  # Matches notes like 'C4', 'F#5', 'Bb3'
NOTE_REGEX = r'^[A-G][#b]?$'  # Matches notes like 'C', 'F#', 'Bb'

# MIDI-specific constants
MIDI_MIN = 0
MIDI_MAX = 127
MIDI_MIDDLE_C = 60
MIDI_VELOCITY_MIN = 0
MIDI_VELOCITY_MAX = 127
MIDI_DEFAULT_VELOCITY = 64

# Note to semitone mapping (C = 0)
NOTE_TO_SEMITONE = {
    'C': 0,
    'C#': 1, 'Db': 1,
    'D': 2,
    'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5,
    'F#': 6, 'Gb': 6,
    'G': 7,
    'G#': 8, 'Ab': 8,
    'A': 9,
    'A#': 10, 'Bb': 10,
    'B': 11
}

# Semitone to note mapping (preferring sharps)
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

# Default scale degree qualities (based on major scale)
DEFAULT_SCALE_DEGREE_QUALITIES = {
    1: ChordQuality.MAJOR,      # I
    2: ChordQuality.MINOR,      # ii
    3: ChordQuality.MINOR,      # iii
    4: ChordQuality.MAJOR,      # IV
    5: ChordQuality.MAJOR,      # V
    6: ChordQuality.MINOR,      # vi
    7: ChordQuality.DIMINISHED  # vii°
}

# Scale intervals
SCALE_INTERVALS = {
    "MAJOR": (0, 2, 4, 5, 7, 9, 11),
    "MINOR": (0, 2, 3, 5, 7, 8, 10),
    "HARMONIC_MINOR": (0, 2, 3, 5, 7, 8, 11),
    "MELODIC_MINOR": (0, 2, 3, 5, 7, 9, 11),
    "DORIAN": (0, 2, 3, 5, 7, 9, 10),
    "PHRYGIAN": (0, 1, 3, 5, 7, 8, 10),
    "LYDIAN": (0, 2, 4, 6, 7, 9, 11),
    "MIXOLYDIAN": (0, 2, 4, 5, 7, 9, 10),
    "LOCRIAN": (0, 1, 3, 5, 6, 8, 10),
    "CHROMATIC": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
}

# Roman numeral pattern for validation
ROMAN_NUMERAL_PATTERN = r'^(i{1,3}|iv|v?i{0,3}|I{1,3}|IV|V?I{0,3})$'

# Roman numeral conversions
INT_TO_ROMAN = {
    1: 'I',
    2: 'II',
    3: 'III',
    4: 'IV',
    5: 'V',
    6: 'VI',
    7: 'VII'
}

ROMAN_TO_INT = {
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4,
    'V': 5,
    'VI': 6,
    'VII': 7,
    'i': 1,
    'ii': 2,
    'iii': 3,
    'iv': 4,
    'v': 5,
    'vi': 6,
    'vii': 7
}

# Basic musical notes
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Alternative representation with flats
NOTES_WITH_FLATS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Roman numeral quality mappings
ROMAN_QUALITY_MAP = {
    'MAJOR': {
        'I': 'maj',
        'II': 'min',
        'III': 'min',
        'IV': 'maj',
        'V': 'maj',
        'VI': 'min',
        'VII': 'dim',
        'i': 'min',
        'ii': 'min',
        'iii': 'min',
        'iv': 'min',
        'v': 'min',
        'vi': 'min',
        'vii': 'dim'
    },
    'MINOR': {
        'I': 'min',
        'II': 'dim',
        'III': 'maj',
        'IV': 'min',
        'V': 'min',
        'VI': 'maj',
        'VII': 'maj',
        'i': 'min',
        'ii': 'dim',
        'iii': 'maj',
        'iv': 'min',
        'v': 'min',
        'vi': 'maj',
        'vii': 'maj'
    }
}

# Define the missing constants
CHORD_INTERVALS = {
    ChordQuality.MAJOR: (0, 4, 7),
    # Add other chord qualities as needed
}

RHYTHM_PATTERNS = {
    # Add your rhythm patterns here
}

def validate_constants() -> None:
    """Validate all constant definitions."""
    # Validate chord intervals
    for quality, intervals in CHORD_INTERVALS.items():
        assert isinstance(intervals, tuple), f"Chord intervals for {quality} must be a tuple"
        assert all(isinstance(i, int) for i in intervals), "Chord intervals must be integers"
        assert all(0 <= i <= 11 for i in intervals), "Chord intervals must be between 0 and 11"

    # Validate scale intervals
    for scale_type, intervals in SCALE_INTERVALS.items():
        assert isinstance(intervals, tuple), f"Scale intervals for {scale_type} must be a tuple"
        assert all(isinstance(i, int) for i in intervals), "Scale intervals must be integers"
        assert all(0 <= i <= 11 for i in intervals), "Scale intervals must be between 0 and 11"
        
        if scale_type == ScaleType.CHROMATIC:
            assert len(intervals) == 12, "Chromatic scale must have 12 notes"
        elif scale_type in {ScaleType.MAJOR, ScaleType.MINOR}:
            assert len(intervals) == 7, f"Diatonic scale {scale_type} must have 7 notes"

    # Validate note patterns
    for pattern_name, pattern_data in NOTE_PATTERNS.items():
        assert isinstance(pattern_data, dict), f"Pattern data for {pattern_name} must be a dictionary"
        required_keys = {'intervals', 'description', 'direction'}
        missing_keys = required_keys - set(pattern_data.keys())
        assert not missing_keys, f"Pattern {pattern_name} missing required keys: {missing_keys}"

    # Validate rhythm patterns
    for pattern_name, pattern_data in RHYTHM_PATTERNS.items():
        assert isinstance(pattern_data, dict), f"Rhythm pattern data for {pattern_name} must be a dictionary"
        required_keys = {'notes', 'total_duration', 'description'}
        missing_keys = required_keys - set(pattern_data.keys())
        assert not missing_keys, f"Rhythm pattern {pattern_name} missing required keys: {missing_keys}"

    # Validate progressions
    for prog_name, prog_data in COMMON_PROGRESSIONS.items():
        assert isinstance(prog_data, dict), f"Progression {prog_name} data must be a dictionary"
        required_keys = {'name', 'description', 'chords'}
        missing_keys = required_keys - set(prog_data.keys())
        assert not missing_keys, f"Progression {prog_name} missing required keys: {missing_keys}"
        
        assert isinstance(prog_data['chords'], list), f"Chords in progression {prog_name} must be a list"
        for chord in prog_data['chords']:
            assert isinstance(chord, dict), "Each chord must be a dictionary"
            assert all(key in chord for key in ['root', 'quality']), \
                f"Invalid chord format in progression {prog_name}"

# Scale degree qualities
SCALE_DEGREE_QUALITIES = {
    'MAJOR': {
        1: 'maj',
        2: 'min',
        3: 'min',
        4: 'maj',
        5: 'maj',
        6: 'min',
        7: 'dim'
    },
    'MINOR': {
        1: 'min',
        2: 'dim',
        3: 'maj',
        4: 'min',
        5: 'min',
        6: 'maj',
        7: 'maj'
    }
}

# Common chord progressions
COMMON_PROGRESSIONS = {
    'I_IV_V': ['I', 'IV', 'V'],
    'I_V_vi_IV': ['I', 'V', 'vi', 'IV'],
    'ii_V_I': ['ii', 'V', 'I'],
    'I_vi_IV_V': ['I', 'vi', 'IV', 'V'],
    'I_IV_vi_V': ['I', 'IV', 'vi', 'V']
}

# Pattern presets
PATTERN_PRESETS = {
    "basic": {
        "name": "Basic Pattern",
        "notes": ["C4", "E4", "G4", "C5"],
        "durations": [1.0, 1.0, 1.0, 1.0],
        "description": "Simple C major arpeggio"
    },
    "walking_bass": {
        "name": "Walking Bass",
        "notes": ["C3", "E3", "G3", "A3"],
        "durations": [1.0, 1.0, 1.0, 1.0],
        "description": "Basic walking bass pattern"
    },
    "melody_1": {
        "name": "Simple Melody",
        "notes": ["C4", "D4", "E4", "F4", "G4"],
        "durations": [1.0, 1.0, 1.0, 1.0, 1.0],
        "description": "Simple ascending melody"
    }
}

# Chord progression presets
PROGRESSION_PRESETS = {
    "basic": {
        "name": "Basic Progression",
        "chords": ["C", "F", "G", "C"],
        "durations": [4.0, 4.0, 4.0, 4.0],
        "description": "Simple I-IV-V-I progression"
    },
    "pop": {
        "name": "Pop Progression",
        "chords": ["C", "G", "Am", "F"],
        "durations": [4.0, 4.0, 4.0, 4.0],
        "description": "Common pop progression (I-V-vi-IV)"
    },
    "jazz": {
        "name": "Jazz Progression",
        "chords": ["Cmaj7", "Dm7", "G7", "Cmaj7"],
        "durations": [4.0, 4.0, 4.0, 4.0],
        "description": "Basic jazz progression (Imaj7-ii7-V7-Imaj7)"
    }
}

# Duration limits
DURATION_LIMITS = {
    'MIN': 0.125,  # 32nd note
    'MAX': 8.0,    # Double whole note
    'DEFAULT': 1.0  # Quarter note
}

# Database constants
DEFAULT_DB_NAME = "note_gen"
DB_NAME = "note_gen"  # Keep existing DB_NAME
DATABASE = {
    "uri": "mongodb://localhost:27017",
    "host": "localhost",
    "port": 27017,
    "name": DB_NAME,
    "database": DB_NAME,
    "user": "postgres",
    "password": "postgres",
    "pool": {
        "max_size": 10,
        "min_size": 1
    },
    "timeout_ms": 5000
}

# Default values
DEFAULTS = {
    "duration": 4.0,
    "bpm": 120,
    "time_signature": (4, 4),
    "key": "C",
    "velocity": 64,
    "octave": 4
}

# Note pattern presets
NOTE_PATTERNS = {
    "minor_triad": {
        "intervals": [0, 3, 7],
        "direction": "up",
        "description": "Minor triad pattern"
    },
    "ascending_scale": {
        "intervals": [0, 2, 4, 5, 7, 9, 11, 12],
        "direction": "up",
        "description": "Basic ascending scale pattern"
    },
    "descending_scale": {
        "intervals": [12, 11, 9, 7, 5, 4, 2, 0],
        "direction": "down",
        "description": "Basic descending scale pattern"
    },
    "triad_arpeggio": {
        "intervals": [0, 4, 7, 12],
        "direction": "up",
        "description": "Major triad arpeggio"
    },
    "pentatonic": {
        "intervals": [0, 2, 4, 7, 9],
        "direction": "up",
        "description": "Pentatonic scale pattern"
    }
}

# Pattern validation limits
PATTERN_VALIDATION_LIMITS = {
    'MAX_PATTERN_LENGTH': 64,
    'MIN_PATTERN_LENGTH': 1,
    'MAX_INTERVAL_JUMP': 12,
    'DEFAULT_OCTAVE_RANGE': (2, 6),
    'MAX_OCTAVE': 8,
    'MIN_OCTAVE': 0,
    'MAX_VELOCITY': 127,
    'MIN_VELOCITY': 0,
    'DEFAULT_VELOCITY': 64,
    'MAX_DURATION': 8.0,
    'MIN_DURATION': 0.125
}

# MongoDB Collection Names
COLLECTION_NAMES = {
    "patterns": "patterns",
    "sequences": "sequences",
    "chord_progressions": "chord_progressions",
    "scales": "scales",
    "presets": "presets",
    "users": "users"
}

# API Rate Limiting
RATE_LIMIT = {
    "requests_per_minute": 60,
    "burst_size": 10
}
