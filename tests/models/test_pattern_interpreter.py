"""Test pattern interpreter."""

import pytest
from typing import Sequence
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.pattern_interpreter import PatternInterpreter
from src.note_gen.models.scale import Scale
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.scale_degree import ScaleDegree

@pytest.fixture
def scale() -> Scale:
    root_note = Note.from_name("C4")
    scale_degree = ScaleDegree(degree=1, quality="major")  # Use a ScaleDegree instance for scale degree
    return Scale(
        root=root_note,
        quality="major",
        scale_degree=scale_degree,
        numeral="I",
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )  # Create a Scale instance

@pytest.fixture
def pattern() -> Sequence[str]:
    return ["C", "D", "E"]  # Example pattern as a list of note names

def test_pattern_interpreter(scale: Scale, pattern: Sequence[str]) -> None:
    interpreter = PatternInterpreter(scale, pattern)
    expected_value = [
        Note.from_name('C4'),
        Note.from_name('D4'),
        Note.from_name('E4')
    ]
    assert interpreter.process() == expected_value
