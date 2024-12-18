from src.models.note import Note
from src.models.chord_base import ChordBase
from src.models.roman_numeral import RomanNumeral
from src.models.chord_quality import ChordQuality
from src.models.chord import Chord
import logging

__all__ = ['get_roman_numeral_from_chord', 'get_chord_from_roman_numeral']

# rest of the file...

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

# Add this to chord_roman_utils.py
def get_chord_from_roman_numeral(roman: RomanNumeral, root_note: Note) -> Chord:
    """Convert a roman numeral to a chord."""
    if not isinstance(root_note, Note):
        logger.error("root_note must be a Note object.")
        raise ValueError("root_note must be a Note object.")
    chord = Chord.from_roman_numeral(roman_str=str(roman), root_note=root_note)
    return chord