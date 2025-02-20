import pytest
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote, RhythmPatternData
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.enums import ChordQualityType

# Fixture for rhythm pattern
@pytest.fixture
def rhythm_pattern() -> RhythmPattern:
    return RhythmPattern(
        name="Default Rhythm Pattern",
        data=RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0, velocity=100, is_rest=False)],
            time_signature="4/4"
        ),
        description="A default rhythm pattern for testing.",
        tags=["test"],
        complexity=1.0,
        style="basic"
    )

@pytest.fixture
def setup_note_sequence_generator(chord_progression, note_pattern, rhythm_pattern) -> NoteSequenceGenerator:
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern,
        note_pattern=note_pattern
    )
    return generator

# Test with different chord progressions and note patterns
@pytest.mark.parametrize("chord_progression, note_pattern, expected_notes", [
    (ChordProgression(
        name="C Major",
        key="C",
        scale_type="MAJOR",
        scale_info=ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR"),
        chords=[
            Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4), quality=ChordQualityType.MAJOR)
        ]
    ),
     NotePattern(name="Triad", pattern=[1, 3, 5]),  # Valid scale degrees for C major
     [Note(note_name="C", octave=4), Note(note_name="E", octave=4), Note(note_name="G", octave=4), Note(note_name="C", octave=5), Note(note_name="C", octave=4), Note(note_name="E", octave=4), Note(note_name="G", octave=4), Note(note_name="C", octave=5)]),  # Adjusted expected notes
    (ChordProgression(
        name="G Major",
        key="G",
        scale_type="MAJOR",
        scale_info=ScaleInfo(root=Note(note_name="G", octave=4), scale_type="MAJOR"),
        chords=[
            Chord(root=Note(note_name="G", octave=4), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
        ]
    ),
     NotePattern(name="Triad", pattern=[1, 3, 5]),  # Valid scale degrees for G major
     [Note(note_name="G", octave=4), Note(note_name="B", octave=4), Note(note_name="D", octave=4), Note(note_name="G", octave=5), Note(note_name="G", octave=4), Note(note_name="B", octave=4), Note(note_name="D", octave=4), Note(note_name="G", octave=5)]),  # Adjusted expected notes
    (ChordProgression(
        name="A Minor",
        key="A",
        scale_type="MINOR",
        scale_info=ScaleInfo(root=Note(note_name="A", octave=4), scale_type="MINOR"),
        chords=[
            Chord(root=Note(note_name="A", octave=4), quality=ChordQualityType.MINOR),
            Chord(root=Note(note_name="D", octave=4), quality=ChordQualityType.MAJOR)
        ]
    ),
     NotePattern(name="Triad", pattern=[1, 3, 5]),  # Valid scale degrees for A minor
     [Note(note_name="A", octave=4), Note(note_name="C", octave=4), Note(note_name="E", octave=4), Note(note_name="A", octave=5), Note(note_name="A", octave=4), Note(note_name="C", octave=4), Note(note_name="E", octave=4), Note(note_name="A", octave=5)]),  # Adjusted expected notes
])


@pytest.mark.asyncio
async def test_generate_sequence(setup_note_sequence_generator, chord_progression, note_pattern, expected_notes):
    # No need to call setup_note_sequence_generator; it is passed as a fixture
    generator = setup_note_sequence_generator
    note_sequence = await generator.generate_sequence()
    notes = note_sequence.notes
    
    # Check the number of notes generated
    assert len(notes) == len(expected_notes), f"Expected {len(expected_notes)} notes to be generated"
    
    # Check the values and order of notes
    for expected, actual in zip(expected_notes, notes):
        assert expected.note_name == actual.note_name, f"Expected note {expected.note_name}, got {actual.note_name}"
        assert expected.octave == actual.octave, f"Expected octave {expected.octave}, got {actual.octave}"
