import pytest
from src.note_gen.core.enums import ScaleType, PatternDirection, ValidationLevel
from src.note_gen.factories.note_sequence_factory import NoteSequenceFactory
from src.note_gen.factories.chord_progression_factory import ChordProgressionFactory
from src.note_gen.factories.pattern_factory import PatternFactory
from src.note_gen.models.note import Note
from src.note_gen.models.rhythm import RhythmNote
from src.note_gen.models.scale_info import ScaleInfo

@pytest.mark.asyncio
async def test_create_from_preset():
    """Test creating a note sequence from preset."""
    sequence = await NoteSequenceFactory.create_from_preset(
        preset_name="basic_major",  # Use a simpler preset name
        key="C",
        scale_type=ScaleType.MAJOR,
        time_signature=(4, 4),
        tempo=120
    )
    assert sequence is not None
    assert sequence.chord_progression is not None
    assert len(sequence.chord_progression.items) > 0

@pytest.mark.asyncio
async def test_create_from_pattern():
    """Test creating a sequence from a pattern."""
    scale_info = ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    sequence = await NoteSequenceFactory.create_from_patterns(
        chord_progression=await ChordProgressionFactory.from_pattern(
            pattern=[(1, "MAJOR"), (4, "MAJOR"), (5, "MAJOR")],
            key="C",
            scale_type=ScaleType.MAJOR
        ),
        note_pattern=PatternFactory().create_note_pattern(
            root_note="C",
            scale_type=ScaleType.MAJOR,
            intervals=[0, 2, 4]
        ),
        rhythm_pattern=PatternFactory().create_rhythm_pattern(
            durations=[1.0, 1.0, 1.0, 1.0],
            time_signature=(4, 4)
        ),
        scale_info=scale_info  # Add scale_info
    )
    assert sequence is not None
    assert sequence.chord_progression is not None

@pytest.mark.asyncio
async def test_create_from_config():
    """Test creating a sequence from configuration."""
    notes = [Note.from_name(name) for name in ["C4", "E4", "G4"]]

    config = {
        "chord_progression": {
            "name": "Test Progression",
            "key": "C",
            "scale_type": ScaleType.MAJOR,
            "items": [
                {
                    "chord": {
                        "root": "C",
                        "quality": "MAJOR"
                    },
                    "chord_symbol": "C",
                    "duration": 1.0,
                    "position": 0.0
                },
                {
                    "chord": {
                        "root": "F",
                        "quality": "MAJOR"
                    },
                    "chord_symbol": "F",
                    "duration": 1.0,
                    "position": 1.0
                }
            ],
            "total_duration": 2.0,
            "chords": [
                {"root": "C", "quality": "MAJOR"},
                {"root": "F", "quality": "MAJOR"}
            ]
        },
        "note_pattern": {
            "name": "Test Pattern",
            "pattern": notes,
            "data": {
                "root_note": "C4",
                "scale_type": ScaleType.MAJOR,
                "direction": PatternDirection.UP,
                "intervals": [0, 2, 4],
                "octave_range": (4, 5)
            }
        },
        "rhythm_pattern": {
            "pattern": [
                RhythmNote(duration=1.0, velocity=64),
                RhythmNote(duration=1.0, velocity=64),
                RhythmNote(duration=1.0, velocity=64),
                RhythmNote(duration=1.0, velocity=64)
            ],
            "time_signature": (4, 4)
        },
        "scale_info": {
            "key": "C",
            "scale_type": ScaleType.MAJOR
        }
    }

    sequence = await NoteSequenceFactory.create_from_config(
        config,
        validation_level=ValidationLevel.NORMAL
    )
    assert sequence is not None
    assert sequence.chord_progression is not None
    assert sequence.note_pattern_name is not None
    assert sequence.note_pattern_name == "Test Pattern"
    assert sequence.rhythm_pattern_name is not None
    assert len(sequence.notes) > 0
    assert sequence.duration > 0
