import pytest
from src.note_gen.models.pattern_type import PatternType
from src.note_gen.models.scale_type import ScaleType  # Import ScaleType


def test_pattern_type() -> None:
    pattern_type = ScaleType()  # Initialize ScaleType object correctly
    assert pattern_type == ScaleType()  # Replace with actual test logic
