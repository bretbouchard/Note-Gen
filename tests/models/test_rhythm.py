import pytest
import math
from pydantic import ValidationError
from src.note_gen.models.rhythm import RhythmPattern, RhythmNote

class TestRhythmNote:
    def test_basic_properties(self):  # Remove the @ symbol
        """Test basic RhythmNote properties and validation."""
        note = RhythmNote(
            position=1.0,
            duration=0.5,
            velocity=64,
            accent=True
        )
        assert note.position == 1.0
        assert note.duration == 0.5
        assert note.velocity == 64
        assert note.accent is True
        assert note.tuplet_ratio == (1, 1)
        assert note.groove_offset == 0.0
        assert note.groove_velocity == 1.0

    def test_invalid_values(self):
        """Test validation of invalid values."""
        with pytest.raises(ValidationError):
            RhythmNote(position=-1.0)  # Invalid negative position

        with pytest.raises(ValidationError):
            RhythmNote(duration=0.0)  # Invalid zero duration

        with pytest.raises(ValidationError):
            RhythmNote(velocity=128)  # Invalid velocity > 127

        with pytest.raises(ValidationError):
            RhythmNote(groove_offset=1.5)  # Invalid groove offset > 1.0

        with pytest.raises(ValidationError):
            RhythmNote(groove_velocity=2.1)  # Invalid groove velocity > 2.0

    @pytest.mark.parametrize("tuplet,expected_duration", [
        ((3, 2), 0.6667),  # Triplet
        ((5, 4), 0.8000),  # Quintuplet
        ((7, 4), 0.5714),  # Septuplet
        ((1, 1), 1.0000),  # Normal note
    ])
    def test_tuplet_durations(self, tuplet, expected_duration):
        """Test actual duration calculations for different tuplets."""
        note = RhythmNote(
            position=0.0,
            duration=1.0,
            velocity=64,
            tuplet_ratio=tuplet
        )
        assert math.isclose(note.get_actual_duration(), expected_duration, rel_tol=1e-3)

    def test_invalid_tuplets(self):
        """Test validation of invalid tuplet ratios."""
        invalid_tuplets = [
            (0, 1),    # Zero in ratio
            (2, 3),    # First number smaller than second
            (-1, 2),   # Negative number
            (3, 0),    # Zero denominator
        ]
        
        for tuplet in invalid_tuplets:
            with pytest.raises(ValidationError):
                RhythmNote(
                    position=0.0,
                    duration=1.0,
                    tuplet_ratio=tuplet
                )

    def test_groove_calculations(self):
        """Test groove modifications to timing and velocity."""
        note = RhythmNote(
            position=1.0,
            duration=1.0,
            velocity=64,
            groove_offset=0.1,
            groove_velocity=1.2
        )
        
        # Test position modification
        assert note.get_actual_position() == 1.1
        
        # Test velocity modification (64 * 1.2 = 76.8, rounded to 77)
        assert note.get_actual_velocity() == 77

    def test_accent_velocity(self):
        """Test velocity modifications with accents."""
        note = RhythmNote(
            position=0.0,
            duration=1.0,
            velocity=64,
            accent=True,
            groove_velocity=1.0
        )
        
        # Accented notes should be 20% louder (64 * 1.2 = 76.8, rounded to 77)
        assert note.get_actual_velocity() == 77

class TestRhythmPattern:
    def test_simple_meter_validation(self):
        """Test pattern validation in simple meters."""
        # Valid 4/4 pattern
        pattern = RhythmPattern(
            name="Simple 4/4",
            pattern=[
                {
                    "position": 0.0,
                    "duration": 1.0,
                    "accent": True,
                    "velocity": 64,
                    "groove_offset": 0.0,
                    "groove_velocity": 1.0
                },
                {
                    "position": 1.0,
                    "duration": 1.0,
                    "accent": False,
                    "velocity": 64,
                    "groove_offset": 0.0,
                    "groove_velocity": 1.0
                },
                {
                    "position": 2.0,
                    "duration": 1.0,
                    "accent": True,
                    "velocity": 64,
                    "groove_offset": 0.0,
                    "groove_velocity": 1.0
                },
                {
                    "position": 3.0,
                    "duration": 1.0,
                    "accent": False,
                    "velocity": 64,
                    "groove_offset": 0.0,
                    "groove_velocity": 1.0
                }
            ],
            time_signature="4/4"
        )
        assert len(pattern.pattern) == 4

    def test_compound_meter_validation(self):
        """Test pattern validation in compound meters."""
        # Valid 6/8 pattern
        pattern = RhythmPattern(
            name="Compound 6/8",
            pattern=[
                RhythmNote(position=0.0, duration=0.5, accent=True),    # First group start - accented
                RhythmNote(position=1.0, duration=0.5, accent=False),
                RhythmNote(position=2.0, duration=0.5, accent=False),
                RhythmNote(position=3.0, duration=0.5, accent=True),    # Second group start - accented
                RhythmNote(position=4.0, duration=0.5, accent=False),
                RhythmNote(position=5.0, duration=0.5, accent=False)
            ],
            time_signature="6/8"
        )
        assert len(pattern.pattern) == 6

        # Valid 9/8 pattern
        pattern = RhythmPattern(
            name="Compound 9/8",
            pattern=[
                RhythmNote(position=0.0, duration=0.5, accent=True),   # First group
                RhythmNote(position=1.0, duration=0.5),
                RhythmNote(position=2.0, duration=0.5),
                RhythmNote(position=3.0, duration=0.5, accent=True),   # Second group
                RhythmNote(position=4.0, duration=0.5),
                RhythmNote(position=5.0, duration=0.5),
                RhythmNote(position=6.0, duration=0.5, accent=True),   # Third group
                RhythmNote(position=7.0, duration=0.5),
                RhythmNote(position=8.0, duration=0.5),
            ],
            time_signature="9/8"
        )
        assert len(pattern.pattern) == 9

        # Valid 12/8 pattern
        pattern = RhythmPattern(
            name="Compound 12/8",
            pattern=[
                RhythmNote(position=0.0, duration=0.5, accent=True),   # First group
                RhythmNote(position=1.0, duration=0.5),
                RhythmNote(position=2.0, duration=0.5),
                RhythmNote(position=3.0, duration=0.5, accent=True),   # Second group
                RhythmNote(position=4.0, duration=0.5),
                RhythmNote(position=5.0, duration=0.5),
                RhythmNote(position=6.0, duration=0.5, accent=True),   # Third group
                RhythmNote(position=7.0, duration=0.5),
                RhythmNote(position=8.0, duration=0.5),
                RhythmNote(position=9.0, duration=0.5, accent=True),   # Fourth group
                RhythmNote(position=10.0, duration=0.5),
                RhythmNote(position=11.0, duration=0.5),
            ],
            time_signature="12/8"
        )
        assert len(pattern.pattern) == 12

    def test_invalid_compound_meter_patterns(self):
        """Test validation of invalid compound meter patterns."""
        # 6/8 pattern without proper accents
        with pytest.raises(ValidationError, match="Missing expected accent"):
            RhythmPattern(
                name="Invalid 6/8",
                pattern=[
                    RhythmNote(position=0.0, duration=0.5, accent=False),  # Should be accented
                    RhythmNote(position=1.0, duration=0.5),
                    RhythmNote(position=2.0, duration=0.5),
                    RhythmNote(position=3.0, duration=0.5, accent=True),
                    RhythmNote(position=4.0, duration=0.5),
                    RhythmNote(position=5.0, duration=0.5),
                ],
                time_signature="6/8"
            )

    def test_groove_template_application(self):
        """Test application of groove templates."""
        base_pattern = RhythmPattern(
            name="Base Pattern",
            pattern=[
                RhythmNote(position=0.0, duration=1.0, velocity=64),
                RhythmNote(position=1.0, duration=1.0, velocity=64),
                RhythmNote(position=2.0, duration=1.0, velocity=64),
                RhythmNote(position=3.0, duration=1.0, velocity=64),
            ],
            time_signature="4/4"
        )

        swing_groove = {
            "timing": [0.0, 0.1, 0.0, 0.1],
            "velocity": [1.2, 0.8, 1.1, 0.9]
        }

        grooved = base_pattern.apply_groove_template(swing_groove)
        
        # Check if groove was applied correctly
        assert grooved.pattern[0].groove_offset == 0.0
        assert grooved.pattern[1].groove_offset == 0.1
        assert grooved.pattern[0].groove_velocity == 1.2
        assert grooved.pattern[1].groove_velocity == 0.8
        assert grooved.groove_template == swing_groove

        # Test invalid groove template
        with pytest.raises(ValueError, match="Timing and velocity lists must have the same length"):
            base_pattern.apply_groove_template({
                "timing": [0.0, 0.1],
                "velocity": [1.2, 0.8, 1.0]
            })

    @pytest.mark.parametrize("time_sig,expected_error", [
        ("3/3", "Denominator must be 2, 4, 8, or 16"),
        ("0/4", "Time signature components must be positive"),
        ("4/0", "Time signature components must be positive"),
        ("5/8", "Numerator must be 2, 3, 4, 6, 9, or 12 for simple and compound meters"),
        ("7/4", "Numerator must be 2, 3, 4, 6, 9, or 12 for simple and compound meters"),
        ("13/8", "Numerator must be 2, 3, 4, 6, 9, or 12 for simple and compound meters"),
    ])
    def test_invalid_time_signatures(self, time_sig, expected_error):
        """Test validation of invalid time signatures."""
        pattern_dict = {
            "position": 0.0,
            "duration": 1.0,
            "velocity": 64,
            "accent": False
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RhythmPattern(
                name="Invalid Pattern",
                pattern=[pattern_dict],
                time_signature=time_sig,
                description="Invalid time signature",
                complexity=0.5,
                data={}
            )
        assert expected_error in str(exc_info.value)

    def test_pattern_duration_validation(self):
        """Test validation of total pattern duration."""
        # Pattern too short for time signature
        with pytest.raises(ValidationError) as exc_info:
            RhythmPattern(
                name="Short Pattern",
                pattern=[
                    {"position": 0.0, "duration": 1.0},
                    {"position": 1.0, "duration": 1.0},
                ],
                time_signature="4/4"  # Needs 4 beats
            )
        assert "Pattern duration" in str(exc_info.value)
