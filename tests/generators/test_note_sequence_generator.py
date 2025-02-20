import pytest
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.enums import ChordQualityType

@pytest.fixture
def setup_note_sequence_generator() -> NoteSequenceGenerator:
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    chord1 = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
    chord2 = Chord(root=Note(note_name="F", octave=4), quality=ChordQualityType.MAJOR)
    chord_progression = ChordProgression(name="Test Progression", key="C", scale_type="MAJOR", scale_info=scale_info, chords=[chord1, chord2])
    note_pattern = NotePattern(name="Test Pattern", pattern=[0, 2, 4])  # Example intervals for a triad
    
    # Create a valid RhythmPattern instance
    rhythm_pattern = RhythmPattern(
        id="test_rhythm_pattern",
        name="Test Rhythm Pattern",
        description="A test rhythm pattern",
        tags=["test"],
        complexity=1.0,
        style="basic",
        data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0, velocity=100, is_rest=False)])
    )
    
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern,
        note_pattern=note_pattern
    )
    return generator

async def test_generate_sequence(setup_note_sequence_generator: NoteSequenceGenerator) -> None:
    generator = setup_note_sequence_generator
    note_sequence = await generator.generate_sequence()
    notes = note_sequence.notes
    
    # Check the number of notes generated
    assert len(notes) == 6, "Expected 6 notes to be generated"
    
    # Check the values and order of notes
    expected_notes = [
        Note(note_name="C", octave=4),
        Note(note_name="E", octave=4),
        Note(note_name="G", octave=4),
        Note(note_name="F", octave=4),
        Note(note_name="A", octave=4),
        Note(note_name="C", octave=5)  # C in the next octave
    ]
    
    for expected, actual in zip(expected_notes, notes):
        assert expected.note_name == actual.note_name, f"Expected note {expected.note_name}, got {actual.note_name}"
        assert expected.octave == actual.octave, f"Expected octave {expected.octave}, got {actual.octave}"
    
    # Additional tests can be added here for different pattern variables
