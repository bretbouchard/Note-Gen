import pytest
import logging
from pydantic import ValidationError
from src.note_gen.models.patterns import NotePattern, NotePatternValidationError, ScaleType, NotePatternData
from src.note_gen.models.note import Note

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@pytest.fixture
def valid_pattern_data():
    """Fixture for valid pattern data."""
    return {
        "name": "Test Pattern",
        "pattern": [
            Note(note_name="C", octave=4),
            Note(note_name="E", octave=4),
            Note(note_name="G", octave=4)
        ],
        "data": {
            "scale_type": ScaleType.MAJOR,
            "intervals": [0, 4, 7],
            "root_note": "C",
            "max_interval_jump": 12,
            "allow_chromatic": False
        }
    }

class TestNotePatternValidation:
    def test_valid_pattern(self, valid_pattern_data):
        """Test creation of valid pattern."""
        note_pattern = NotePattern(
            name=valid_pattern_data['name'],
            pattern=valid_pattern_data['pattern'],
            data=NotePatternData(**valid_pattern_data['data'])
        )
        assert note_pattern.name == valid_pattern_data['name']
        assert note_pattern.pattern == valid_pattern_data['pattern']
        assert note_pattern.data.scale_type == valid_pattern_data['data']['scale_type']
        assert note_pattern.data.allow_chromatic == valid_pattern_data['data']['allow_chromatic']
        assert note_pattern.data.intervals == valid_pattern_data['data']['intervals']
        assert note_pattern.data.root_note == valid_pattern_data['data']['root_note']
        assert note_pattern.data.max_interval_jump == valid_pattern_data['data']['max_interval_jump']

    def test_pattern_structure(self, valid_pattern_data):
        """Test pattern structure validation."""
        invalid_data = valid_pattern_data.copy()
        invalid_data['pattern'] = [Note(note_name="C", octave=4), 2, 3, 4]
        invalid_data['data'] = {
            "scale_type": ScaleType.MAJOR,
            "intervals": [0, 2, 3, 4],
            "root_note": "C",
            "allow_chromatic": False,
            "max_interval_jump": 12
        }
        with pytest.raises(ValidationError, match="Pattern must contain only Note objects"):
            NotePattern(
                name=invalid_data['name'],
                pattern=invalid_data['pattern'],
                data=NotePatternData(**invalid_data['data'])
            )

    def test_scale_compatibility(self, valid_pattern_data):
        """Test scale compatibility."""
        invalid_data = valid_pattern_data.copy()
        invalid_data['pattern'] = [Note(note_name="C", octave=4), Note(note_name="C#", octave=4)]
        invalid_data['data'] = {
            "scale_type": ScaleType.MAJOR,
            "intervals": [0, 1],
            "root_note": "C",
            "allow_chromatic": False,
            "max_interval_jump": 12
        }
        with pytest.raises(ValidationError, match="Note C# is not in scale"):
            NotePattern(
                name=invalid_data['name'],
                pattern=invalid_data['pattern'],
                data=NotePatternData(**invalid_data['data'])
            )

    def test_voice_leading(self):
        """Test voice leading rules."""
        pattern = NotePattern(
            name="Test Pattern",
            pattern=[
                Note(note_name="C", octave=4, duration=1.0),
                Note(note_name="C", octave=5, duration=1.0)  # Jump of 12 semitones
            ],
            data=NotePatternData(
                scale_type=ScaleType.MAJOR,
                intervals=[0, 12],
                root_note="C",
                allow_chromatic=False,
                max_interval_jump=11
            )
        )
        with pytest.raises(ValidationError, match="Interval jump of 12 semitones exceeds maximum allowed"):
            pattern.validate_all()

    def test_parallel_motion(self):
        """Test parallel perfect intervals."""
        pattern = NotePattern(
            name="Test Pattern",
            pattern=[
                Note(note_name="C", octave=4, duration=1.0),
                Note(note_name="C", octave=5, duration=1.0)  # Same note in different octaves
            ],
            data=NotePatternData(
                scale_type=ScaleType.MAJOR,
                intervals=[0, 12],
                root_note="C",
                allow_chromatic=False,
                max_interval_jump=12
            )
        )
        with pytest.raises(ValidationError, match="Parallel perfect intervals are not allowed"):
            pattern.validate_all()

    def test_consonance(self):
        """Test dissonant intervals."""
        pattern = NotePattern(
            name="Test Pattern",
            pattern=[
                Note(note_name="C", octave=4, duration=1.0),
                Note(note_name="C#", octave=4, duration=1.0)
            ],
            data=NotePatternData(
                scale_type=ScaleType.MAJOR,
                intervals=[0, 1],
                root_note="C",
                allow_chromatic=True,  # Allow chromatic notes for this test
                max_interval_jump=12
            )
        )
        with pytest.raises(ValidationError, match="Dissonant interval of 1 semitones"):
            pattern.validate_all()

    def test_missing_scale_type(self, valid_pattern_data):
        """Test that missing scale_type raises a validation error."""
        invalid_data = valid_pattern_data.copy()
        invalid_data['data'] = {
            "intervals": [0, 2, 4],
            "root_note": "C",
            "allow_chromatic": False,
            "max_interval_jump": 12
        }
        with pytest.raises(ValidationError, match="Field required"):
            NotePattern(
                name=invalid_data['name'],
                pattern=invalid_data['pattern'],
                data=NotePatternData(**invalid_data['data'])
            )

    def test_invalid_scale_type(self, valid_pattern_data):
        """Test that invalid scale_type raises a validation error."""
        invalid_data = valid_pattern_data.copy()
        invalid_data['data'] = {
            "scale_type": "invalid_scale",
            "intervals": [0, 2, 4],
            "root_note": "C",
            "allow_chromatic": False,
            "max_interval_jump": 12
        }
        with pytest.raises(ValidationError, match="Input should be"):
            NotePattern(
                name=invalid_data['name'],
                pattern=invalid_data['pattern'],
                data=NotePatternData(**invalid_data['data'])
            )

    def test_empty_pattern(self, valid_pattern_data):
        """Test that empty pattern raises a validation error."""
        invalid_data = valid_pattern_data.copy()
        invalid_data['pattern'] = []
        invalid_data['data'] = {
            "scale_type": ScaleType.MAJOR,
            "intervals": [0, 2, 4],
            "root_note": "C",
            "allow_chromatic": False,
            "max_interval_jump": 12
        }
        with pytest.raises(ValidationError, match="Pattern cannot be empty"):
            NotePattern(
                name=invalid_data['name'],
                pattern=invalid_data['pattern'],
                data=NotePatternData(**invalid_data['data'])
            )

    @pytest.mark.parametrize("invalid_name", [
        "A",  # Too short
        "Test@Pattern",  # Invalid character
        "123",  # Too short and no letters
        "    ",  # Just spaces
    ])
    def test_invalid_names(self, valid_pattern_data, invalid_name):
        """Test name validation with various invalid names."""
        invalid_data = valid_pattern_data.copy()
        invalid_data['name'] = invalid_name
        invalid_data['data'] = {
            "scale_type": ScaleType.MAJOR,
            "intervals": [0, 2, 4],
            "root_note": "C",
            "allow_chromatic": False,
            "max_interval_jump": 12
        }
        with pytest.raises(ValidationError, match="Name.*"):
            NotePattern(
                name=invalid_data['name'],
                pattern=invalid_data['pattern'],
                data=NotePatternData(**invalid_data['data'])
            )
