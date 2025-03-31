"""MIDI validation and conversion utilities."""
from typing import Tuple

def validate_midi_number(midi_number: int) -> bool:
    """Validate if a MIDI number is within the valid range (0-127)."""
    return 0 <= midi_number <= 127

def midi_to_octave_pitch(midi_number: int) -> Tuple[int, int]:
    """
    Convert MIDI number to octave and pitch class.
    Returns tuple of (octave, pitch_class).
    Follows standard MIDI mapping where:
    - MIDI 60 = Middle C (C4)
    - Each octave starts at C
    """
    if not validate_midi_number(midi_number):
        raise ValueError(f"Invalid MIDI number: {midi_number}")
    
    # Adjust calculation to make MIDI 60 correspond to C4
    octave = (midi_number - 12) // 12
    pitch_class = midi_number % 12
    
    return octave, pitch_class

def pitch_to_midi_number(pitch: str, octave: int) -> int:
    """
    Convert pitch and octave to MIDI number.
    Example: ("C", 4) -> 60 (Middle C)
    """
    base_notes = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11
    }
    
    if pitch not in base_notes:
        raise ValueError(f"Invalid pitch: {pitch}")
    
    midi_number = base_notes[pitch] + (octave + 1) * 12
    
    if not validate_midi_number(midi_number):
        raise ValueError(f"Resulting MIDI number {midi_number} is out of range")
    
    return midi_number