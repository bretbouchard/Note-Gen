import pytest
from unittest.mock import MagicMock, patch

from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord_progression_generator import ChordProgressionGenerator, ProgressionPattern
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.chord_progression import ChordProgression
from pydantic import ValidationError


@pytest.fixture
def setup_scale_info() -> ScaleInfo:
    scale_info = MagicMock(spec=ScaleInfo)
    scale_info.get_scale_degree = MagicMock(side_effect=lambda degree: 
        Note(name='C', octave=4) if degree == 1 
        else Note(name='F', octave=4) if degree == 4 
        else Note(name='G', octave=4) if degree == 5 
        else None
    )
    scale_info.scale_degrees = [1, 2, 3, 4, 5, 6, 7]
    return scale_info


@pytest.fixture
def setup_chord_progression_generator(setup_scale_info) -> ChordProgressionGenerator:
    return ChordProgressionGenerator(scale_info=setup_scale_info)


@pytest.mark.parametrize("pattern, raises_error", [
    (ProgressionPattern.BASIC_I_IV_V_I, False),
    (None, True),
    ('invalid_pattern', True)
])
def test_generate_progression_patterns(setup_chord_progression_generator: ChordProgressionGenerator, pattern, raises_error) -> None:
    generator = setup_chord_progression_generator
    if raises_error:
        with pytest.raises(ValueError):
            generator.generate(pattern=pattern)
    else:
        progression = generator.generate(pattern=pattern)
        assert progression is not None
        assert len(progression.chords) > 0


def test_generate_with_invalid_scale_degree(setup_chord_progression_generator: ChordProgressionGenerator) -> None:
    generator = setup_chord_progression_generator
    with patch.object(generator.scale_info, 'get_scale_degree', return_value=None):  # Mock to return None for any degree
        with pytest.raises(ValueError):
            generator.generate(pattern=ProgressionPattern.BASIC_I_IV_V_I)


def test_invalid_progression_length(setup_scale_info: ScaleInfo) -> None:
    with pytest.raises(ValueError):
        ChordProgressionGenerator(scale_info=setup_scale_info, progression_length=-1)


def test_chord_with_empty_notes() -> None:
    with pytest.raises(ValueError, match="Chord notes cannot be empty"):
        Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[])


def test_progression_with_empty_chords() -> None:
    scale_info = ScaleInfo(root=Note(name='C', octave=4))
    with pytest.raises(ValueError, match="Chords cannot be empty"):
        ChordProgression(scale_info=scale_info, chords=[])


def test_generate_valid_progression(setup_chord_progression_generator: ChordProgressionGenerator) -> None:
    generator = setup_chord_progression_generator
    progression = generator.generate(pattern=ProgressionPattern.BASIC_I_IV_V_I)
    assert progression is not None
    assert len(progression.chords) == 4
    assert all(isinstance(chord, Chord) for chord in progression.chords)


def test_scale_info_validation() -> None:
    with pytest.raises(ValidationError):
        ChordProgressionGenerator(scale_info=None)


def test_generate_progression_with_valid_patterns() -> None:
    scale_info: ScaleInfo = ScaleInfo(root=Note(name='C', octave=4))
    generator: ChordProgressionGenerator = ChordProgressionGenerator(scale_info=scale_info, progression_length=4, pattern=ProgressionPattern.BASIC_I_IV_V_I)
    progression: ChordProgression = generator.generate(pattern=ProgressionPattern.BASIC_I_IV_V_I)
    assert progression is not None
    assert len(progression.chords) == 4
    assert all(isinstance(chord, Chord) for chord in progression.chords)


def test_generate_progression_with_invalid_patterns() -> None:
    scale_info: ScaleInfo = ScaleInfo(root=Note(name='C', octave=4))
    generator: ChordProgressionGenerator = ChordProgressionGenerator(scale_info=scale_info, progression_length=4, pattern=None)
    with pytest.raises(ValueError):
        generator.generate(pattern=None)

    # Check for invalid pattern type
    with pytest.raises(ValueError):
        generator = ChordProgressionGenerator(scale_info=scale_info, progression_length=4, pattern='invalid_pattern')
        generator.generate()