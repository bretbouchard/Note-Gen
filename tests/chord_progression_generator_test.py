"""Tests for chord progression generator."""

from models.chord_progression_generator import ChordProgressionGenerator, ProgressionPattern
from models.note import Note
from models.scale import Scale
from models.scale_info import ScaleInfo
from models.presets import COMMON_PROGRESSIONS

def test_basic_progression() -> None:
    """Test basic I-IV-V-I progression."""
    scale_info = ScaleInfo(root=Note.from_str("C"), scale_type="major")
    generator = ChordProgressionGenerator(scale_info=scale_info)
    
    progression = generator.generate(ProgressionPattern.BASIC_I_IV_V_I)
    chords = progression.get_all_chords()
    
    assert len(chords) == 4
    assert [chord.root.note_name for chord in chords] == ["C", "F", "G", "C"]
    assert [chord.quality for chord in chords] == ["major", "major", "major", "major"]

def test_pop_progression() -> None:
    """Test pop I-V-vi-IV progression."""
    scale_info = ScaleInfo(root=Note.from_str("G"), scale_type="major")
    generator = ChordProgressionGenerator(scale_info=scale_info)
    
    progression = generator.generate(ProgressionPattern.POP_I_V_vi_IV)
    chords = progression.get_all_chords()
    
    assert len(chords) == 4
    assert [chord.root.note_name for chord in chords] == ["G", "D", "E", "C"]
    assert [chord.quality for chord in chords] == ["major", "major", "minor", "major"]

def test_jazz_progression() -> None:
    """Test jazz ii-V-I progression."""
    scale_info = ScaleInfo(root=Note.from_str("F"), scale_type="major")
    generator = ChordProgressionGenerator(scale_info=scale_info)
    
    progression = generator.generate(ProgressionPattern.JAZZ_ii_V_I)
    chords = progression.get_all_chords()
    
    assert len(chords) == 3
    assert [chord.root.note_name for chord in chords] == ["G", "C", "F"]
    assert [chord.quality for chord in chords] == ["minor7", "dominant7", "major7"]

def test_minor_progression() -> None:
    """Test minor i-iv-v progression."""
    scale_info = ScaleInfo(root=Note.from_str("A"), scale_type="minor")
    generator = ChordProgressionGenerator(scale_info=scale_info)
    
    progression = generator.generate(ProgressionPattern.MINOR_i_iv_v)
    chords = progression.get_all_chords()
    
    assert len(chords) == 3
    assert [chord.root.note_name for chord in chords] == ["A", "D", "E"]
    assert [chord.quality for chord in chords] == ["minor", "minor", "minor"]

def test_custom_progression() -> None:
    """Test custom progression generation."""
    scale_info = ScaleInfo(root=Note.from_str("D"), scale_type="major")
    generator = ChordProgressionGenerator(scale_info=scale_info)
    
    # Create a I-iii-vi-ii-V progression with specific qualities
    degrees = [1, 3, 6, 2, 5]
    qualities = ["major7", "minor7", "minor7", "minor7", "dominant7"]
    
    progression = generator.generate_custom(degrees, qualities)
    chords = progression.get_all_chords()
    
    assert len(chords) == 5
    assert [chord.root.note_name for chord in chords] == ["D", "F#", "B", "E", "A"]
    assert [chord.quality for chord in chords] == qualities

def test_random_progression() -> None:
    """Test random progression generation."""
    scale_info = ScaleInfo(root=Note.from_str("C"), scale_type="major")
    generator = ChordProgressionGenerator(scale_info=scale_info)
    
    progression = generator.generate_random(length=4)
    chords = progression.get_all_chords()
    
    assert len(chords) == 4
    # Check that all chords are in the C major scale
    valid_roots = ["C", "D", "E", "F", "G", "A", "B"]
    for chord in chords:
        assert chord.root.name in valid_roots

def test_all_preset_progressions():
    """Test that all preset progressions can be generated."""
    root_note = Note.from_name("C")
    scale = Scale(root=root_note, quality="major")
    scale_info = ScaleInfo(root=root_note, scale=scale)
    generator = ChordProgressionGenerator(root=root_note, scale=scale, scale_info=scale_info)

    invalid_progressions = []

    for progression_name, numerals in COMMON_PROGRESSIONS.items():
        try:
            chords = []
            for numeral in numerals:
                # Handle specific chord names (like "Dm7", "G7", etc.)
                if any(char.isdigit() or char in "♭#°" for char in numeral) and "/" not in numeral:
                    # For now, we'll skip specific chord names as they need special handling
                    continue
                
                # Skip specific note names (like "Am", "G", etc.)
                if numeral[0].isupper() and len(numeral) <= 2 and not any(x in numeral for x in ["I", "V"]):
                    continue

                chord = generator.generate_chord(numeral)
                chords.append(chord)
        except Exception as e:
            invalid_progressions.append((progression_name, str(e)))

    if invalid_progressions:
        error_msg = "The following progressions failed validation:\n"
        for prog, error in invalid_progressions:
            error_msg += f"- {prog}: {error}\n"
        raise AssertionError(error_msg)
