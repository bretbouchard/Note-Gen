import logging

from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.key import Key

__all__ = ["get_roman_numeral_from_chord", "get_chord_from_roman_numeral"]

logger = logging.getLogger(__name__)


def get_roman_numeral_from_chord(chord: Chord) -> str:
    """Convert a chord to a roman numeral."""
    if not chord:
        raise ValueError("Chord cannot be empty")

    # Basic implementation
    roman_numeral = "I"  # Default to I if no other logic

    # Add inversion if present
    if chord.inversion > 0 and chord.bass:
        roman_numeral += f"/{chord.bass.name}"

    return roman_numeral


def get_chord_from_roman_numeral(roman_numeral: str, key_note: Note) -> Chord:
    """Get a chord from a roman numeral in a given key."""
    # Create a RomanNumeral object from the string
    roman = RomanNumeral.from_str(roman_numeral)

    # Convert the RomanNumeral to a Chord
    chord = roman.to_chord(key_note)

    return chord


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
