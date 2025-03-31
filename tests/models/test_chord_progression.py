"""Test suite for chord progression model."""
import pytest
from pydantic import ValidationError
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord_progression_item import ChordProgressionItem
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.core.enums import ScaleType, ChordQuality

@pytest.fixture
def basic_chord_item() -> ChordProgressionItem:
    """Fixture for basic chord progression item."""
    return ChordProgressionItem.create(
        chord_symbol="C",
        duration=1.0
    )

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
            ChordProgressionItem.create(chord_symbol="C", duration=1.0, position=0.0),
            ChordProgressionItem.create(chord_symbol="G", duration=1.0, position=1.0)
        ],
        pattern=["I", "V"]
    )
    
    # Add your assertions here
    assert len(prog.items) == 2
    assert prog.items[0].chord_symbol == "C"
    assert prog.items[1].chord_symbol == "G"

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
            ChordProgressionItem.create(
                chord_symbol="C",
                duration=1.0
            )
        ]
    )
    
    assert prog.key == "C"
    assert prog.items[0].chord_symbol == "C"




if __name__ == "__main__":
    pytest.main()
