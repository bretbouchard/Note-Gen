"""Tests for RomanNumeral model."""
import unittest
from typing import List, Optional
from note_gen.models.roman_numeral import RomanNumeral
from note_gen.core.enums import ChordQuality, ValidationLevel
from note_gen.core.constants import (
    ROMAN_TO_INT,
    INT_TO_ROMAN,
    ROMAN_QUALITY_MAP,
    DEFAULT_SCALE_DEGREE_QUALITIES
)
from note_gen.core.accessors import ScaleDegreeAccessor
from note_gen.validation.roman_numeral_validation import validate_roman_numeral_data

class TestRomanNumeral(unittest.TestCase):
    """Test cases for RomanNumeral class."""

    def setUp(self):
        """Set up test cases."""
        self.valid_roman = RomanNumeral.model_validate({
            "numeral": "V",
            "quality": ChordQuality.MAJOR,
            "accidental": None,
            "inversion": None,
            "secondary": None
        })
        
    def test_basic_creation(self):
        """Test basic roman numeral creation."""
        roman = RomanNumeral.model_validate({
            "numeral": "V",
            "quality": ChordQuality.MAJOR,
            "accidental": None,
            "inversion": None,
            "secondary": None
        })
        self.assertEqual(roman.numeral, "V")
        self.assertEqual(roman.quality, ChordQuality.MAJOR)
        self.assertIsNone(roman.inversion)
        self.assertIsNone(roman.accidental)

    def test_from_scale_degree(self):
        """Test creation from scale degree."""
        test_cases = [
            (1, ChordQuality.MAJOR),      # I
            (2, ChordQuality.MINOR),      # ii
            (3, ChordQuality.MINOR),      # iii
            (4, ChordQuality.MAJOR),      # IV
            (5, ChordQuality.MAJOR),      # V
            (6, ChordQuality.MINOR),      # vi
            (7, ChordQuality.DIMINISHED)  # vii°
        ]
        
        for degree, expected_quality in test_cases:
            roman = RomanNumeral.from_scale_degree(degree)
            self.assertEqual(roman.numeral, INT_TO_ROMAN[degree])
            self.assertEqual(
                roman.quality, 
                expected_quality,
                f"Scale degree {degree} should have quality {expected_quality}"
            )
            
            # Also test explicit quality override
            override_quality = ChordQuality.MAJOR
            roman_override = RomanNumeral.from_scale_degree(degree, override_quality)
            self.assertEqual(roman_override.quality, override_quality)

    def test_validation(self):
        """Test roman numeral validation."""
        # Test valid cases
        valid_data = {
            "numeral": "V",
            "quality": ChordQuality.MAJOR,
            "inversion": None,
            "accidental": None,
            "secondary": None
        }
        result = validate_roman_numeral_data(valid_data, ValidationLevel.STRICT)
        self.assertTrue(result.is_valid)

        # Test invalid cases
        invalid_data = {
            "numeral": "VIII",  # Invalid roman numeral
            "quality": ChordQuality.MAJOR,
            "inversion": None,
            "accidental": None,
            "secondary": None
        }
        result = validate_roman_numeral_data(invalid_data, ValidationLevel.STRICT)
        self.assertFalse(result.is_valid)

    def test_to_scale_degree(self):
        """Test conversion to scale degree."""
        roman = RomanNumeral.model_validate({
            "numeral": "V",
            "quality": ChordQuality.MAJOR,
            "accidental": None,
            "inversion": None,
            "secondary": None
        })
        scale_degree = roman.to_scale_degree()
        self.assertEqual(scale_degree.value, 5)
        self.assertEqual(scale_degree.quality, ChordQuality.MAJOR)

    def test_secondary_dominants(self):
        """Test secondary dominant functionality."""
        secondary = RomanNumeral.model_validate({
            "numeral": "V",
            "quality": ChordQuality.DOMINANT_SEVENTH,
            "accidental": None,
            "inversion": None,
            "secondary": None
        })
        
        primary = RomanNumeral.model_validate({
            "numeral": "V",
            "quality": ChordQuality.MAJOR,
            "accidental": None,
            "inversion": None,
            "secondary": secondary
        })
        
        # Validate the structure
        result = validate_roman_numeral_data(
            primary.model_dump(),
            ValidationLevel.STRICT
        )
        self.assertTrue(result.is_valid)
        
        # Check secondary relationship
        self.assertEqual(primary.secondary, secondary)

    def test_validation_levels(self):
        """Test validation at different levels."""
        roman = RomanNumeral.model_validate({
            "numeral": "V",
            "quality": ChordQuality.MAJOR,
            "inversion": 2,
            "accidental": None,
            "secondary": None
        })
        
        # Test LENIENT validation
        result = validate_roman_numeral_data(
            roman.model_dump(),
            ValidationLevel.LENIENT
        )
        self.assertTrue(result.is_valid)
        
        # Test STRICT validation
        result = validate_roman_numeral_data(
            roman.model_dump(),
            ValidationLevel.STRICT
        )
        self.assertTrue(result.is_valid)

if __name__ == '__main__':
    unittest.main()
