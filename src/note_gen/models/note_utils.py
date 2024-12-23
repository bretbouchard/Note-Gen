"""Module for utility functions related to musical notes.

This module provides various utility functions that assist in the manipulation 
and processing of musical notes, including functions for note conversion, 
validation, and other common operations.

The functions in this module are designed to be used in a variety of musical 
applications, such as music composition, analysis, and playback. They provide 
a convenient and efficient way to work with musical notes, and can be used to 
perform tasks such as converting between different note representations, 
validating note names, and generating musical patterns.

Note Conversion Functions
------------------------

The note conversion functions in this module allow you to convert between 
different note representations, such as note names, MIDI note numbers, and note 
frequencies. These functions are useful for tasks such as converting a musical 
composition from one format to another, or for generating musical patterns 
based on a set of note frequencies.

Validation Functions
--------------------

The validation functions in this module allow you to check whether a note name 
or MIDI note number is valid. These functions are useful for tasks such as 
checking the validity of user input, or for ensuring that a musical composition 
is well-formed.

Additional Utility Functions
---------------------------

In addition to the note conversion and validation functions, this module also 
provides a number of additional utility functions that can be used to perform 
tasks such as generating musical patterns, calculating note frequencies, and 
more. These functions are designed to be flexible and reusable, and can be 
used in a variety of musical applications.

"""

from typing import Dict, Tuple
from pydantic import BaseModel, ConfigDict

from src.note_gen.models.enums import AccidentalType
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord

class NoteUtils(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

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

    Raises:
        ValueError: If the note name is invalid
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

    Raises:
        ValueError: If the MIDI number cannot be converted to a note
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

def note_name_to_midi(note_name: str) -> int:
    """Convert a note name to its corresponding MIDI note number.

    Args:
        note_name (str): The name of the note (e.g., 'C4', 'D#5').

    Returns:
        int: The corresponding MIDI note number.
    """
    note_to_midi = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7,
        'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    }
    # Extract the note and octave
    note, octave = note_name[:-1], int(note_name[-1])
    return note_to_midi[note] + (octave + 1) * 12

def validate_note_name(note_name: str) -> bool:
    """Validate a musical note name.

    Args:
        note_name (str): The name of the note to validate.

    Returns:
        bool: True if the note name is valid, False otherwise.
    """
    valid_notes = {'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'}
    return note_name in valid_notes

def midi_to_note_name(midi: int) -> str:
    """Convert a MIDI note number to its corresponding note name.

    Args:
        midi (int): The MIDI note number.

    Returns:
        str: The corresponding note name (e.g., 'C4', 'D#5').

    Raises:
        ValueError: If the MIDI number is out of range
    """
    if midi < 0 or midi > 127:
        raise ValueError("MIDI number must be between 0 and 127")
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = midi // 12 - 1
    note = note_names[midi % 12]
    return f'{note}{octave}'

# Additional utility functions can be added as needed...
