import pytest
from typing import Sequence
from src.note_gen.models.pattern_interpreter import PatternInterpreter
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.scale_degree import ScaleDegree

@pytest.fixture
def scale() -> Scale:
    root_note = Note(name="C", accidental="", octave=4)
    scale_degree = ScaleDegree(degree=1, note=root_note)  # Create a ScaleDegree instance
    scale_info = ScaleInfo(root=root_note, scale_type="major", scale_degrees=[scale_degree])  # Create a ScaleInfo instance
    return Scale(scale=scale_info, numeral="C", numeral_str="C", scale_degree=1, quality="major", is_major=True, is_diminished=False, is_augmented=False, is_half_diminished=False, has_seventh=False, has_ninth=False, has_eleventh=False, inversion=0)  # Create a Scale instance

@pytest.fixture
def pattern() -> Sequence[str]:
    return ["C", "D", "E"]  # Example pattern as a list of note names

def test_pattern_interpreter(scale: Scale, pattern: Sequence[str]) -> None:
    interpreter = PatternInterpreter(scale, pattern)
    expected_value = [
        Note(name='C', accidental='', octave=4, duration=1.0, velocity=64, midi_number=60),
        Note(name='D', accidental='', octave=4, duration=1.0, velocity=64, midi_number=62),
        Note(name='E', accidental='', octave=4, duration=1.0, velocity=64, midi_number=64)
    ]
    assert interpreter.process() == expected_value
