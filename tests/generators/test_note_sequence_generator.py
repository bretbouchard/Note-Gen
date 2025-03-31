import pytest
from src.note_gen.core.enums import ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.patterns import NotePattern, RhythmPattern
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator

@pytest.mark.asyncio
async def test_generate_sequence(scale_info):
    # Create test instances
    chord_progression = ChordProgression(
        name="Test Progression",
        key="C",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info,
        chords=[Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=64, position=0.0))]
    )
    note_pattern = Patterns(pattern=[0, 2, 4])
    rhythm_pattern = RhythmPattern(pattern=[1, 0, 1, 0])
    
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        note_pattern=note_pattern,
        rhythm_pattern=rhythm_pattern
    )
    
    sequence = await generator.generate_sequence(
        chord_progression=chord_progression,
        note_pattern=note_pattern,
        rhythm_pattern=rhythm_pattern,
        scale_info=scale_info
    )
    
    assert sequence is not None
    assert len(sequence.notes) > 0
