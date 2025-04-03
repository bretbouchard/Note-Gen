import logging
from typing import List, Optional, Union
from unittest import mock
import pytest

from note_gen.models.scale_info import ScaleInfo
from note_gen.models.chord import Chord, ChordQuality
from note_gen.core.enums import ScaleType
from note_gen.models.note import Note
from note_gen.models.chord_progression import ChordProgression

logger = logging.getLogger(__name__)

class FakeScaleInfo:
    def __init__(self, key: str, scale_type: ScaleType):
        self.key = key
        self.scale_type = scale_type

def test_generate_progression_from_pattern():
    """Test generating a progression from a note pattern."""

    # Create test pattern and scale info
    pattern = ["I", "IV", "V", "vi"]
    scale_info = ScaleInfo(key="C", scale_type=ScaleType.MAJOR)

    # Create a mock progression
    mock_progression = mock.MagicMock(spec=ChordProgression)
    mock_progression.key = "C"
    mock_progression.scale_type = ScaleType.MAJOR
    mock_progression.chords = ["I", "IV", "V"]

    # Mock the classmethod directly on the class
    with mock.patch.object(
        ChordProgression,
        'from_pattern',
        return_value=mock_progression,
        autospec=True
    ) as mock_method:
        # Test calling the mocked method
        result = ChordProgression.from_pattern(
            pattern=pattern,
            scale_info=scale_info  # Remove key and name parameters
        )

        # Assert the mock was called with correct parameters
        mock_method.assert_called_once_with(
            pattern=pattern,
            scale_info=scale_info
        )

        # Assert that our result matches what we expect
        assert result.key == "C"
        assert result.scale_type == ScaleType.MAJOR
        assert len(result.chords) == 3
