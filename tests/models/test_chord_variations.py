import pytest
from pydantic import ValidationError
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.musical_elements import ChordQualityType
from src.note_gen.models.roman_numeral import RomanNumeral

def test_chord_quality_variations() -> None:
    root_note = Note.from_name("C4", duration=1.0, velocity=64)
    
    # Test various quality strings
    for quality_str in ['maj7', 'MAJOR7', 'major7', 'Maj7']:
        chord = Chord(root=root_note, quality=quality_str)
        assert chord.quality == ChordQualityType.MAJOR7
        assert len(chord.notes) == 4  # Major 7 chord should have 4 notes
        assert chord.notes[0].note_name == "C"
        assert chord.notes[1].note_name == "E"
        assert chord.notes[2].note_name == "G"
        assert chord.notes[3].note_name == "B"
        assert chord.notes[0].octave == 4
        assert chord.notes[1].octave == 4
        assert chord.notes[2].octave == 4
        assert chord.notes[3].octave == 4
        assert chord.notes[0].duration == 1.0
        assert chord.notes[1].duration == 1.0
        assert chord.notes[2].duration == 1.0
        assert chord.notes[3].duration == 1.0
        assert chord.notes[0].velocity == 64
        assert chord.notes[1].velocity == 64
        assert chord.notes[2].velocity == 64
        assert chord.notes[3].velocity == 64

    # Test an invalid quality string
    with pytest.raises(ValueError):
        Chord(root=root_note, quality='invalid_quality')

    # Test another invalid quality string
    with pytest.raises(ValueError):
        Chord(root=root_note, quality='another_invalid_quality')
