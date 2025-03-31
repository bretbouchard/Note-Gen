"""Test suite for chord progression model."""
import pytest
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionItem
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.core.enums import ScaleType, ChordQuality

@pytest.fixture
def basic_chord_item() -> ChordProgressionItem:
    """Fixture for basic chord progression item."""
    return ChordProgressionItem.create(
        root="C",
        quality=ChordQuality.MAJOR,
        duration=1.0
    )

@pytest.fixture
def scale_info() -> ScaleInfo:
    """Fixture for scale info."""
    return ScaleInfo(key="C", scale_type=ScaleType.MAJOR)

def test_create_chord_progression_valid_data(basic_chord_item: ChordProgressionItem) -> None:
    """Test creating a chord progression with valid data."""
    prog = ChordProgression(
        name="Test Progression",
        key="C",
        scale_type=ScaleType.MAJOR,
        items=[basic_chord_item]
    )
    assert prog.name == "Test Progression"
    assert prog.key == "C"
    assert len(prog.items) == 1

def test_generate_progression_from_pattern(scale_info: ScaleInfo) -> None:
    """Test generating a chord progression from a pattern."""
    pattern = ["I", "IV", "V", "vi"]
    result = ChordProgression.generate_progression_from_pattern(
        pattern=pattern,
        key="C",
        name="Test Pattern",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info
    )
    assert isinstance(result, ChordProgression)
    assert result.pattern == pattern
    assert result.key == "C"

def test_chord_progression_methods() -> None:
    """Test chord progression methods."""
    c_chord = Chord(root="C", quality=ChordQuality.MAJOR)
    g_chord = Chord(root="G", quality=ChordQuality.MAJOR)
    
    prog = ChordProgression(
        name="Test",
        key="C",
        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR),
        scale_type=ScaleType.MAJOR,
        items=[
            ChordProgressionItem(chord=c_chord, duration=1.0, position=0.0),
            ChordProgressionItem(chord=g_chord, duration=1.0, position=1.0)  # Set position to 1.0
        ],
        pattern=["I", "V"]
    )
    
    assert prog.get_chord_at_position(0.5) == c_chord
    assert prog.get_chord_at_position(1.5) == g_chord

def test_key_validation() -> None:
    """Test key validation rules."""
    prog = ChordProgression(
        name="Test",
        key="C",
        scale_info=ScaleInfo(
            key="C",
            scale_type=ScaleType.MAJOR
        ),
        scale_type=ScaleType.MAJOR,
        items=[
            ChordProgressionItem(
                chord=Chord(root="C", quality=ChordQuality.MAJOR),
                duration=1.0
            )
        ]
    )
    assert prog.key == "C"




if __name__ == "__main__":
    pytest.main()
