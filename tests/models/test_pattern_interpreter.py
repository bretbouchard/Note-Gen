import pytest
from src.note_gen.models.pattern_interpreter import PatternInterpreter


def test_pattern_interpreter(scale: str, pattern: str) -> None:
    interpreter = PatternInterpreter(scale, pattern)
    assert interpreter.process() == expected_value
