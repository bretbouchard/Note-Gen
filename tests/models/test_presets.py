import pytest
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.scale import Scale, ScaleInfo, ScaleDegree
from src.note_gen.models.presets import get_default_chord_progression, get_default_note_pattern, get_default_rhythm_pattern, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern

# Define the necessary constants
COMMON_PROGRESSIONS = {
    "I-IV-V-I": ["I", "IV", "V", "I"],
    "default": ["I", "V", "vi", "IV"],
    "alternative": ["I", "vi", "IV", "V"]
}
DEFAULT_CHORD_PROGRESSION = "I-IV-V-I"
DEFAULT_NOTE_PATTERN = [1, 2, 3, 5, 6, 8]
DEFAULT_RHYTHM_PATTERN = [1, 1, 1, 1, 1, 1]

@pytest.fixture
def scale(root_note) -> Scale:
    scale_degree = ScaleDegree(degree=1, note=root_note)  # Example scale degree
    scale = Scale(
        scale=ScaleInfo(root=root_note, scale_degrees=[scale_degree, ScaleDegree(degree=2, note=Note(name='D', accidental='', octave=4))]),  # Include scale degrees
        numeral='I',
        numeral_str='I',
        scale_degree=1,
        quality='major',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )
    return scale

@pytest.fixture
def root_note():
    return Note(name='C', accidental='', octave=4)

def test_get_default_chord_progression(scale: Scale) -> None:
    progression = get_default_chord_progression(scale.root, scale)
    assert progression.get_chord_names() == ['I', 'IV', 'V', 'I'], f"Expected ['I', 'IV', 'V', 'I'], but got {progression.get_chord_names()}"  # Adjusted to check chord names

def test_get_default_note_pattern() -> None:
    expected_pattern = NotePattern(name='Simple Triad', data=NOTE_PATTERNS['Simple Triad'])
    assert get_default_note_pattern() == expected_pattern


def test_get_default_rhythm_pattern() -> None:
    expected_rhythm_pattern = RhythmPattern(name='quarter_notes', data=RHYTHM_PATTERNS['quarter_notes'])
    assert get_default_rhythm_pattern() == expected_rhythm_pattern

# Address the Pydantic validation error related to RhythmNote
