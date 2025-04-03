import pytest
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.chord import Chord
from note_gen.models.chord_progression import ChordProgression, ChordProgressionItem
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.note import Note
from note_gen.generators.note_sequence_generator import NoteSequenceGenerator
from note_gen.core.enums import ScaleType, ChordQuality, PatternDirection

@pytest.fixture
def scale_info():
    return ScaleInfo(key="C", scale_type=ScaleType.MAJOR)

@pytest.mark.asyncio
async def test_generate_sequence(scale_info):
    """Test generating a note sequence."""
    # Create a chord first
    chord = Chord(
        root="C",
        quality=ChordQuality.MAJOR,
        duration=1.0,
        velocity=64
    )

    # Create test instances
    chord_progression = ChordProgression(
        name="Test Progression",
        key="C",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info,
        items=[
            ChordProgressionItem(
                chord_symbol="C",
                chord=chord,
                duration=1.0,
                position=0.0
            )
        ],
        chords=[chord],  # Add the chords list
        total_duration=1.0  # Add total duration
    )

    pattern_data = NotePatternData(
        key="C",
        root_note="C",
        scale_type=ScaleType.MAJOR,
        direction=PatternDirection.UP,
        octave=4
    )

    note_pattern = NotePattern(
        name="Test Pattern",
        pattern=[Note.from_name("C4"), Note.from_name("E4"), Note.from_name("G4")],
        data=pattern_data,
        scale_info=scale_info,
        skip_validation=True
    )

    rhythm_pattern = RhythmPattern(
        pattern=[
            RhythmNote(position=0.0, duration=1.0, velocity=64),
            RhythmNote(position=1.0, duration=0.5, velocity=64),
            RhythmNote(position=1.5, duration=0.5, velocity=64),
            RhythmNote(position=2.0, duration=1.0, velocity=64)
        ],
        time_signature=(4, 4),
        swing_enabled=False
    )

    # Create the generator with all required parameters
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        note_pattern=note_pattern,
        rhythm_pattern=rhythm_pattern
    )

    # Generate the sequence
    sequence = await generator.generate(scale_info=scale_info)

    # Add assertions
    assert sequence is not None
    assert len(sequence.notes) > 0
    assert sequence.scale_info is not None
    assert "key" in sequence.scale_info
    assert sequence.scale_info["key"] == scale_info.key
    assert sequence.progression_name == "Test Progression"
    assert sequence.note_pattern_name == "Test Pattern"
