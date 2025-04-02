"""Core music theory utilities and functions."""
from typing import Dict
from .constants import NOTES

# Define valid keys (all possible keys in music)
VALID_KEYS = [f"{note}{quality}" for note in NOTES for quality in ['', 'm']]

# Dictionary mapping notes to their enharmonic equivalents
ENHARMONIC_EQUIVALENTS: Dict[str, str] = {
    'C#': 'Db', 'Db': 'C#',
    'D#': 'Eb', 'Eb': 'D#',
    'F#': 'Gb', 'Gb': 'F#',
    'G#': 'Ab', 'Ab': 'G#',
    'A#': 'Bb', 'Bb': 'A#'
}

def get_note_pitch_class(note: str) -> str:
    """Extract the pitch class from a note (removing octave if present)."""
    # Remove any octave number (e.g., 'C4' -> 'C')
    return ''.join(c for c in note if not c.isdigit())
