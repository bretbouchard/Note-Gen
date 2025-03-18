import pytest
from src.note_gen.models.enums import ScaleType

class TestEnums:
    def test_major_scale_intervals(self):
        """Test that major scale intervals are correct"""
        assert ScaleType.MAJOR.get_intervals() == [0, 2, 4, 5, 7, 9, 11]

    def test_minor_scale_intervals(self):
        """Test that minor scale intervals are correct"""
        assert ScaleType.MINOR.get_intervals() == [0, 2, 3, 5, 7, 8, 10]

    def test_pentatonic_aliases(self):
        """Test that pentatonic scale aliases work correctly"""
        major_pent = ScaleType.MAJOR_PENTATONIC.get_intervals()
        minor_pent = ScaleType.MINOR_PENTATONIC.get_intervals()
        assert major_pent == [0, 2, 4, 7, 9]
        assert minor_pent == [0, 3, 5, 7, 10]

    def test_chromatic_scale(self):
        """Test chromatic scale has all 12 intervals"""
        intervals = ScaleType.CHROMATIC.get_intervals()
        assert intervals == list(range(12))
        assert len(intervals) == 12

    def test_modes(self):
        """Test that all modes have correct intervals"""
        assert len(ScaleType.DORIAN.get_intervals()) == 7
        assert len(ScaleType.PHRYGIAN.get_intervals()) == 7
        assert len(ScaleType.LYDIAN.get_intervals()) == 7
        assert len(ScaleType.MIXOLYDIAN.get_intervals()) == 7
        assert len(ScaleType.LOCRIAN.get_intervals()) == 7

    def test_special_scales(self):
        """Test special scale types"""
        assert len(ScaleType.BLUES.get_intervals()) == 6
        assert len(ScaleType.HARMONIC_MAJOR.get_intervals()) == 7
        assert len(ScaleType.MELODIC_MAJOR.get_intervals()) == 7
        assert len(ScaleType.DOUBLE_HARMONIC_MAJOR.get_intervals()) == 7

    def test_invalid_scale_type(self):
        """Test that invalid scale type raises ValueError"""
        with pytest.raises(ValueError):
            # We can't actually create an invalid ScaleType through the enum
            # Instead, test the get_intervals() with an invalid name
            invalid_scale = "INVALID_SCALE"
            ScaleType(invalid_scale).get_intervals()