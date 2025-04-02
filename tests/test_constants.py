import pytest
from unittest.mock import patch
from src.note_gen.core.constants import validate_constants
from src.note_gen.core.enums import (
    ScaleType,
    ChordQuality,
    PatternDirection
)
# Remove duplicate imports
from src.note_gen.models.chord import ChordQuality

def test_validate_scale_intervals_wrong_type():
    """Test validation with wrong type for scale intervals (line 200)."""
    invalid_intervals = {
        ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11]  # List instead of tuple
    }
    with patch('src.note_gen.core.constants.SCALE_INTERVALS', invalid_intervals):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be a tuple" in str(exc_info.value)

def test_validate_scale_intervals_non_integers():
    """Test validation with non-integer intervals (line 217)."""
    invalid_intervals = {
        ScaleType.MAJOR: (0, 2.5, 4, 5, 7, 9, 11)  # Float instead of int
    }
    with patch('src.note_gen.core.constants.SCALE_INTERVALS', invalid_intervals):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be integers" in str(exc_info.value)

def test_validate_scale_intervals_out_of_range():
    """Test validation with out-of-range intervals (line 220)."""
    invalid_intervals = {
        ScaleType.MAJOR: (0, 2, 4, 5, 7, 9, 13)  # 13 is out of range
    }
    with patch('src.note_gen.core.constants.SCALE_INTERVALS', invalid_intervals):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be between 0 and 11" in str(exc_info.value)

def test_validate_chromatic_scale_wrong_length():
    """Test validation of chromatic scale length (line 225)."""
    invalid_intervals = {
        ScaleType.CHROMATIC: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)  # Missing 11
    }
    with patch('src.note_gen.core.constants.SCALE_INTERVALS', invalid_intervals):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "Chromatic scale must have 12 notes" in str(exc_info.value)

def test_validate_diatonic_scale_wrong_length():
    """Test validation of diatonic scale length (line 228)."""
    invalid_intervals = {
        ScaleType.MAJOR: (0, 2, 4, 5, 7, 9)  # Only 6 notes
    }
    with patch('src.note_gen.core.constants.SCALE_INTERVALS', invalid_intervals):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "Diatonic scale ScaleType.MAJOR must have 7 notes" in str(exc_info.value)

def test_validate_progression_wrong_type():
    """Test validation of progression type (line 235)."""
    invalid_progressions = {
        "I-IV-V": ["not", "a", "dict"]  # List instead of dict
    }
    with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', invalid_progressions):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be a dictionary" in str(exc_info.value)

def test_validate_progression_invalid_chord_format():
    """Test validation of chord format in progression (line 249)."""
    invalid_progressions = {
        "I-IV-V": {
            "name": "Test",
            "description": "Test progression",
            "chords": [
                {"root": 1},  # Missing quality
                {"quality": ChordQuality.MAJOR}  # Missing root
            ]
        }
    }
    with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', invalid_progressions):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "Invalid chord format in progression" in str(exc_info.value)

def test_validate_progression_missing_required_keys():
    """Test validation of progression with missing required keys (lines 233, 235, 237)."""
    # Test case 1: Missing all required keys
    invalid_progressions_1 = {
        "I-IV-V": {}  # Empty dict missing all required keys
    }
    with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', invalid_progressions_1):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "missing required keys" in str(exc_info.value)

    # Test case 2: Missing some required keys
    invalid_progressions_2 = {
        "I-IV-V": {
            "name": "Test",
            # Missing 'description' and 'chords'
        }
    }
    with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', invalid_progressions_2):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "missing required keys" in str(exc_info.value)

    # Test case 3: Missing only one required key
    invalid_progressions_3 = {
        "I-IV-V": {
            "name": "Test",
            "description": "Test progression",
            # Missing 'chords'
        }
    }
    with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', invalid_progressions_3):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "missing required keys" in str(exc_info.value)

def test_validate_progression_invalid_chords_type():
    """Test validation of progression with invalid chords type (line 246)."""
    invalid_progressions = {
        "I-IV-V": {
            "name": "Test",
            "description": "Test progression",
            "chords": "not_a_list"  # Should be a list
        }
    }
    with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', invalid_progressions):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "Chords in progression I-IV-V must be a list" in str(exc_info.value)

def test_validate_progression_invalid_chord_dict():
    """Test validation of progression with invalid chord dictionary (line 249)."""
    invalid_progressions = {
        "I-IV-V": {
            "name": "Test",
            "description": "Test progression",
            "chords": [
                "not_a_dict"  # Should be a dictionary
            ]
        }
    }
    with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', invalid_progressions):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "Each chord must be a dictionary" in str(exc_info.value)

def test_validate_constants_valid_data():
    """Test validation with valid data to ensure no false positives."""
    valid_data = {
        "scale_intervals": {
            ScaleType.MAJOR: (0, 2, 4, 5, 7, 9, 11),
            ScaleType.CHROMATIC: tuple(range(12))
        },
        "progressions": {
            "I-IV-V": {
                "name": "Test",
                "description": "Test progression",
                "chords": [
                    {"root": 1, "quality": ChordQuality.MAJOR},
                    {"root": 4, "quality": ChordQuality.MAJOR},
                    {"root": 5, "quality": ChordQuality.MAJOR}
                ]
            }
        }
    }
    
    with patch('src.note_gen.core.constants.SCALE_INTERVALS', valid_data["scale_intervals"]):
        with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', valid_data["progressions"]):
            validate_constants()  # Should not raise any exceptions

def test_validate_constants_with_invalid_note_pattern():
    """Test validation with invalid note pattern structure."""
    invalid_pattern = {
        "invalid_pattern": "not_a_dict"  # Should be a dictionary
    }
    with patch('src.note_gen.core.constants.NOTE_PATTERNS', invalid_pattern):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be a dictionary" in str(exc_info.value)

def test_validate_constants_with_missing_note_pattern_keys():
    """Test validation with missing required keys in note pattern."""
    invalid_pattern = {
        "test_pattern": {
            "direction": PatternDirection.UP,
            # Missing 'intervals' and 'description'
        }
    }
    with patch('src.note_gen.core.constants.NOTE_PATTERNS', invalid_pattern):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "missing required keys" in str(exc_info.value)

def test_validate_constants_with_invalid_rhythm_pattern():
    """Test validation with invalid rhythm pattern structure."""
    invalid_pattern = {
        "invalid_rhythm": "not_a_dict"  # Should be a dictionary
    }
    with patch('src.note_gen.core.constants.RHYTHM_PATTERNS', invalid_pattern):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be a dictionary" in str(exc_info.value)

def test_validate_constants_with_missing_rhythm_pattern_keys():
    """Test validation with missing required keys in rhythm pattern."""
    invalid_pattern = {
        "test_rhythm": {
            "notes": [(0, 1.0)],
            # Missing 'total_duration' and 'description'
        }
    }
    with patch('src.note_gen.core.constants.RHYTHM_PATTERNS', invalid_pattern):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "missing required keys" in str(exc_info.value)

def test_validate_constants_with_invalid_chord_progression_chords():
    """Test validation with invalid chord format in progression."""
    invalid_progression = {
        "test_prog": {
            "name": "Test",
            "description": "Test progression",
            "chords": [
                {"root": 1}  # Missing 'quality'
            ]
        }
    }
    with patch('src.note_gen.core.constants.COMMON_PROGRESSIONS', invalid_progression):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "Invalid chord format" in str(exc_info.value)

def test_validate_chord_intervals_tuple():
    """Test validation of chord intervals requiring tuple type."""
    invalid_intervals = {
        ChordQuality.MAJOR: [0, 4, 7]  # List instead of tuple
    }
    with patch('src.note_gen.core.constants.CHORD_INTERVALS', invalid_intervals):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be a tuple" in str(exc_info.value)

def test_validate_chord_intervals_integers():
    """Test validation of chord intervals requiring integers."""
    invalid_intervals = {
        ChordQuality.MAJOR: (0, "4", 7)  # String instead of int
    }
    with patch('src.note_gen.core.constants.CHORD_INTERVALS', invalid_intervals):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be integers" in str(exc_info.value)

def test_validate_chord_intervals_range():
    """Test validation of chord intervals range."""
    invalid_intervals = {
        ChordQuality.MAJOR: (0, 4, 12)  # 12 is out of range
    }
    with patch('src.note_gen.core.constants.CHORD_INTERVALS', invalid_intervals):
        with pytest.raises(AssertionError) as exc_info:
            validate_constants()
        assert "must be between 0 and 11" in str(exc_info.value)
