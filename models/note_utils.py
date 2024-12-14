"""Utility functions for working with musical notes."""
from typing import Dict, Tuple

from .accidental_type import AccidentalType

# Mapping of note names to MIDI note numbers (C4 = 60)
NOTE_TO_NUMBER: Dict[str, int] = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}

# Mapping of MIDI note numbers to note names
NUMBER_TO_NOTE: Dict[int, str] = {
    0: 'C',
    2: 'D',
    4: 'E',
    5: 'F',
    7: 'G',
    9: 'A',
    11: 'B'
}

def calculate_midi_note(note_name: str, accidental: AccidentalType, octave: int) -> int:
    """
    Calculate the MIDI note number for a given note name, accidental, and octave.
    
    Args:
        note_name (str): The note name (e.g., 'C', 'D', etc.)
        accidental (AccidentalType): The accidental (natural, sharp, flat)
        octave (int): The octave number (e.g., 4 for middle C)
        
    Returns:
        int: The MIDI note number
    """
    if note_name not in NOTE_TO_NUMBER:
        raise ValueError(f"Invalid note name: {note_name}")
        
    base_note = NOTE_TO_NUMBER[note_name]
    accidental_offset = {
        AccidentalType.NATURAL: 0,
        AccidentalType.SHARP: 1,
        AccidentalType.FLAT: -1
    }[accidental]
    
    return base_note + accidental_offset + (octave * 12)

def midi_to_note(midi_number: int) -> Tuple[str, AccidentalType, int]:
    """
    Convert a MIDI note number to a note name, accidental, and octave.
    
    Args:
        midi_number (int): The MIDI note number
        
    Returns:
        Tuple[str, AccidentalType, int]: A tuple of (note_name, accidental, octave)
    """
    octave = midi_number // 12
    note_value = midi_number % 12
    
    # Find the closest natural note
    for base_value, note_name in NUMBER_TO_NOTE.items():
        if base_value == note_value:
            return note_name, AccidentalType.NATURAL, octave
        elif base_value + 1 == note_value:
            return note_name, AccidentalType.SHARP, octave
        elif base_value - 1 == note_value:
            return note_name, AccidentalType.FLAT, octave
            
    # If we get here, something went wrong
    raise ValueError(f"Could not convert MIDI number {midi_number} to note")
