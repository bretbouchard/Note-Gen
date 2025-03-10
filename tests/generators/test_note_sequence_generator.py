import pytest
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.patterns import RhythmPattern, RhythmPatternData, RhythmNote
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.patterns import NotePattern
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def setup_note_sequence_generator() -> NoteSequenceGenerator:
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    
    # Fix: Create Chord instances with ChordQuality directly instead of trying to use Chord as a factory
    chord1 = Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR)
    chord2 = Chord(root=Note(note_name="F", octave=4), quality=ChordQuality.MAJOR)
    
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
        data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0, velocity=100, is_rest=False)]),
        pattern=[1, 1, -1]  # Updated pattern representation
    )
    
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern,
        note_pattern=note_pattern
    )
    return generator

async def test_generate_sequence(setup_note_sequence_generator: NoteSequenceGenerator) -> None:
    generator = setup_note_sequence_generator
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    note_sequence = await generator.generate_sequence(
        chord_progression=generator.chord_progression,
        note_pattern=generator.note_pattern,
        rhythm_pattern=generator.rhythm_pattern,
        scale_info=scale_info
    )
    notes = note_sequence.notes
    
    logger.info(f"Generated notes: {[note.note_name for note in notes]}")
    logger.info(f"Generated notes with octave: {[f'{note.note_name}{note.octave}' for note in notes]}")
    
    # Check the number of notes generated
    assert len(notes) == 8, "Expected 8 notes to be generated"
    
    # Check the values and order of notes
    expected_notes = [
        Note(note_name="C", octave=4),
        Note(note_name="E", octave=4),
        Note(note_name="G", octave=4),
        Note(note_name="C", octave=4),
        Note(note_name="F", octave=4),
        Note(note_name="A", octave=4),
        Note(note_name="C", octave=4),  # C in the next octave
        Note(note_name="F", octave=4)
    ]
    
    for expected, actual in zip(expected_notes, notes):
        assert expected.note_name == actual.note_name, f"Expected note {expected.note_name}, got {actual.note_name}"
        assert expected.octave == actual.octave, f"Expected octave {expected.octave}, got {actual.octave}"
    
    # Additional tests can be added here for different pattern variables
