import pytest
from unittest.mock import patch
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.patterns import RhythmPattern, RhythmPatternData, RhythmNote, NotePattern, NotePatternData, ChordProgression
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord, ChordQuality
import logging

logger = logging.getLogger(__name__)

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
        style="basic",
        pattern=[1, 1, -1]
    )

@pytest.fixture
def setup_note_sequence_generator() -> NoteSequenceGenerator:
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    chord1 = Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR)
    chord2 = Chord(root=Note(note_name="F", octave=4), quality=ChordQuality.MAJOR)
    chord_progression = ChordProgression(
        name="Test Progression",
        key="C",
        scale_type="MAJOR",
        scale_info=scale_info,
        chords=[chord1, chord2]
    )
    note_pattern = NotePattern(
        name="Test Pattern",
        intervals=[1, 3, 5],
        data=NotePatternData(
            intervals=[1, 3, 5],
            duration=1.0,
            velocity=100,
            notes=[Note(note_name="C", octave=4)]
        ),
        tags=["test"],
        complexity=0.5
    )
    rhythm_pattern = RhythmPattern(
        name="Test Rhythm Pattern",
        data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0, velocity=100, is_rest=False)]),
        description="A test rhythm pattern",
        tags=["test"],
        complexity=1.0,
        style="basic",
        pattern=[1, 1, -1]
    )
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern,
        note_pattern=note_pattern
    )
    return generator

@pytest.mark.parametrize("chord_progression, note_pattern, expected_notes", [
    (ChordProgression(
        name="C Major",
        key="C",
        scale_type="MAJOR",
        scale_info=ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR"),
        chords=[
            Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="F", octave=4), quality=ChordQuality.MAJOR)
        ]
    ),
     NotePattern(
        name="Triad",
        intervals=[1, 3, 5],
        data=NotePatternData(
            intervals=[1, 3, 5],
            duration=1.0,
            velocity=100,
            notes=[Note(note_name="C", octave=4)]
        ),
        tags=["valid_tag"],
        complexity=0.5,
        description="A triad pattern",
        style="basic"
    ),
     [Note(note_name="C", octave=4), Note(note_name="E", octave=4), Note(note_name="G", octave=4),
      Note(note_name="C", octave=4), Note(note_name="F", octave=4), Note(note_name="A", octave=4),
      Note(note_name="C", octave=4), Note(note_name="F", octave=4)]),
    (ChordProgression(
        name="A Minor",
        key="A",
        scale_type="MINOR",
        scale_info=ScaleInfo(root=Note(note_name="A", octave=4), scale_type="MINOR"),
        chords=[
            Chord(root=Note(note_name="A", octave=4), quality=ChordQuality.MINOR),
            Chord(root=Note(note_name="D", octave=4), quality=ChordQuality.MAJOR)
        ]
    ),
     NotePattern(
        name="Triad",
        intervals=[1, 3, 5],
        data=NotePatternData(
            intervals=[1, 3, 5],
            duration=1.0,
            velocity=100,
            notes=[Note(note_name="A", octave=4)]
        ),
        tags=["valid_tag"],
        complexity=0.5,
        description="A triad pattern",
        style="basic"
    ),
     [Note(note_name="A", octave=4), Note(note_name="C", octave=4), Note(note_name="E", octave=4),
      Note(note_name="A", octave=4), Note(note_name="D", octave=4), Note(note_name="F#", octave=4),
      Note(note_name="A", octave=4), Note(note_name="D", octave=4)])
])

@pytest.mark.asyncio
async def test_generate_sequence(setup_note_sequence_generator, chord_progression, note_pattern, expected_notes):
    generator = setup_note_sequence_generator
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    note_sequence = await generator.generate_sequence(
        chord_progression=chord_progression,
        note_pattern=note_pattern,
        rhythm_pattern=generator.rhythm_pattern,
        scale_info=scale_info
    )
    notes = note_sequence.notes
    assert len(notes) == len(expected_notes)
    for expected, actual in zip(expected_notes, notes):
        assert expected.note_name == actual.note_name
        assert expected.octave == actual.octave