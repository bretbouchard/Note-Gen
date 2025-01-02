import logging

from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.key import Key

__all__ = ["get_roman_numeral_from_chord", "get_chord_from_roman_numeral", "get_root_note_from_roman_numeral"]

logger = logging.getLogger(__name__)


def get_roman_numeral_from_chord(chord: Chord, key_note: Note) -> str:
    """Get a roman numeral from a chord in a given key."""
    # Calculate the interval between the key note and chord root
    interval = (chord.root.midi_number - key_note.midi_number) % 12
    # Convert interval to scale degree
    scale_degree = interval + 1
    # Ensure scale degree is valid
    if scale_degree < 1 or scale_degree > 7:
        raise ValueError(f"Calculated scale degree {scale_degree} is out of valid range (1-7).")
    # Convert scale degree to roman numeral
    numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    if 1 <= scale_degree <= 7:
        return numerals[scale_degree - 1]
    else:
        raise ValueError(f"Calculated scale degree {scale_degree} is out of valid range (1-7).")


def get_chord_from_roman_numeral(numeral: str, key_note: Note) -> Chord:
    """Get a chord from a roman numeral in a given key."""
    # Create a RomanNumeral object from the string
    roman = RomanNumeral.from_str(numeral)
    # Get the scale degree
    scale_degree = roman.to_int()
    # Calculate the interval
    interval = scale_degree - 1
    # Create the root note
    root_midi = key_note.midi_number + interval
    root = Note.from_midi(root_midi)
    # Create and return the chord
    return Chord(root=root)


def get_root_note_from_roman_numeral(roman_numeral: str, key: Key) -> Note:
    """Get the root note from a roman numeral in a given key."""
    # Convert roman numeral to scale degree (1-based index)
    roman_to_degree = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
        "i": 1,
        "ii": 2,
        "iii": 3,
        "iv": 4,
        "v": 5,
        "vi": 6,
        "vii": 7,
    }

    # Extract the base roman numeral (without any modifiers)
    base_roman = "".join(c for c in roman_numeral.upper() if c in "IVXL")

    if base_roman not in roman_to_degree:
        raise ValueError(f"Invalid roman numeral: {roman_numeral}")

    scale_degree = roman_to_degree[base_roman]
    scale_notes = key.get_scale_notes()

    if not scale_notes or len(scale_notes) < 7:
        raise ValueError("Invalid key or scale")

    return scale_notes[scale_degree - 1]
