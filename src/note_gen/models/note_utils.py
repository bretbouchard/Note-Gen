"""Module for utility functions related to musical notes."""

from typing import Dict, Optional, Union
from src.note_gen.models.enums import AccidentalType
from src.note_gen.models.note import Note

# Mapping of note names to MIDI note numbers (C4 = 60)
NOTE_TO_NUMBER: Dict[str, int] = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

# Mapping of MIDI note numbers to note names
NUMBER_TO_NOTE: Dict[int, str] = {
    0: "C",
    2: "D",
    4: "E",
    5: "F",
    7: "G",
    9: "A",
    11: "B",
}

def get_note(midi_number: int) -> Note:
    """Get a note by MIDI number."""
    return Note.from_midi(midi_number)

def create_note(name: str, octave: int = 4) -> Note:
    """Create a note from name and octave."""
    return Note.from_name(f"{name}{octave}")

def update_note(note: Note, name: Optional[str] = None, octave: Optional[int] = None) -> Note:
    """Update a note's properties."""
    if name is None:
        name = note.base_name
    if octave is None:
        octave = note.octave
    return Note.from_name(f"{name}{octave}", velocity=note.velocity, duration=note.duration)

def delete_note(note: Note) -> None:
    """Delete a note."""
    pass  # No-op since notes are immutable

def midi_to_note(midi: int) -> str:
    """Convert MIDI note number to note name with octave."""
    octave = (midi // 12) - 1
    note_num = midi % 12
    
    for note_name, base_num in NOTE_TO_NUMBER.items():
        if base_num == note_num:
            return f"{note_name}{octave}"
    return None

def validate_note_name(note_name: str) -> None:
    """Validate a musical note name."""
    base_name = note_name[:-1] if note_name[-1].isdigit() else note_name
    if len(note_name) > 1 and note_name[1] in ['#', 'b']:
        base_name = note_name[:2]
    if base_name not in Note.NOTE_NAMES:
        raise ValueError(f"Invalid note name: {note_name}")

def calculate_midi_note(note_name: str, accidental: AccidentalType, octave: int) -> int:
    """Calculate MIDI note number."""
    base_num = NOTE_TO_NUMBER.get(note_name.upper(), 0)
    accidental_value = 0
    if accidental == AccidentalType.SHARP:
        accidental_value = 1
    elif accidental == AccidentalType.FLAT:
        accidental_value = -1
    elif accidental == AccidentalType.DOUBLE_SHARP:
        accidental_value = 2
    elif accidental == AccidentalType.DOUBLE_FLAT:
        accidental_value = -2
    
    return (octave + 1) * 12 + base_num + accidental_value

def note_name_to_midi(note_name: str) -> int:
    """Convert note name to MIDI number."""
    if not validate_note_name(note_name):
        raise ValueError(f"Invalid note name: {note_name}")
    
    note = note_name[0].upper()
    octave = int(note_name[-1])
    accidental = AccidentalType.NATURAL
    
    if len(note_name) > 2:
        acc = note_name[1]
        if acc == '#':
            accidental = AccidentalType.SHARP
        elif acc == 'b':
            accidental = AccidentalType.FLAT
    
    return calculate_midi_note(note, accidental, octave)

def midi_to_note_name(midi: int) -> str:
    """Convert MIDI number to note name."""
    if not 0 <= midi <= 127:
        raise ValueError(f"MIDI number {midi} out of range (0-127)")
    
    octave = (midi // 12) - 1
    note_num = midi % 12
    
    for note_name, base_num in NOTE_TO_NUMBER.items():
        if base_num == note_num:
            return f"{note_name}{octave}"
    
    # Handle sharps
    for note_name, base_num in NOTE_TO_NUMBER.items():
        if (base_num + 1) % 12 == note_num:
            return f"{note_name}#{octave}"
    
    return None
