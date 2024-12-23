import pytest
from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale, ScaleInfo
from src.note_gen.models.presets import Presets, get_default_chord_progression, get_default_note_pattern, get_default_rhythm_pattern

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
    scale = Scale(
        scale=ScaleInfo(root=root_note),
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
    assert get_default_chord_progression(scale) == COMMON_PROGRESSIONS['I-IV-V-I']  # Ensure the test logic matches the expected output


def test_get_default_note_pattern() -> None:
    assert get_default_note_pattern() == DEFAULT_NOTE_PATTERN


def test_get_default_rhythm_pattern() -> None:
    assert get_default_rhythm_pattern() == DEFAULT_RHYTHM_PATTERN

# Address the Pydantic validation error related to RhythmNote
