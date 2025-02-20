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
from typing import List
import logging
import os

# Set up logging configuration
log_file_path = 'logs/app.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Log to specified file
        logging.StreamHandler()  # Also log to console
    ]
)

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
        style="basic"
    )

@pytest.fixture
def setup_note_sequence_generator(rhythm_pattern) -> NoteSequenceGenerator:
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    chord1 = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
    chord2 = Chord(root=Note(note_name="F", octave=4), quality=ChordQualityType.MAJOR)
    chord_progression = ChordProgression(name="Test Progression", key="C", scale_type="MAJOR", scale_info=scale_info, chords=[chord1, chord2])
    note_pattern = NotePattern(name="Test Pattern", pattern=[1, 3, 5])  # Valid intervals for C major triad
    logger.info(f"Type of rhythm_pattern: {type(rhythm_pattern)}")  # Log the type of rhythm_pattern
    logger.info(f"Rhythm pattern before passing to generator: {rhythm_pattern}")  # Log the rhythm_pattern
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern,
        note_pattern=note_pattern
    )
    return generator

@pytest.mark.parametrize("chord_progression, expected_notes", [
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
    [
        Note(note_name="D", octave=4),  # C + 1
        Note(note_name="E", octave=4),  # C + 3
        Note(note_name="G", octave=4),  # C + 5
        Note(note_name="D", octave=4),  # C + 1 (repeat)
        Note(note_name="G", octave=4),  # F + 1
        Note(note_name="A", octave=4),  # F + 3
        Note(note_name="C", octave=5),  # F + 5 (next octave)
        Note(note_name="G", octave=4)   # F + 1 (repeat)
    ]),  # Adjusted expected notes
])

async def test_generate_sequence(setup_note_sequence_generator: NoteSequenceGenerator, chord_progression: ChordProgression, expected_notes: List[Note]) -> None:
    generator = setup_note_sequence_generator
    generator.chord_progression = chord_progression
    generator.rhythm_pattern = RhythmPattern.from_str('{"name": "Default Rhythm Pattern", "data": {"time_signature": "4/4", "notes": [{"position": 0, "duration": 1.0, "velocity": 100, "is_rest": false}]}}')  # Ensure correct format
    note_sequence = await generator.generate_sequence()
    notes = note_sequence.notes
    print(f"Expected notes: {[note.note_name for note in expected_notes]}")  # Print expected notes
    print(f"Count of expected notes: {len(expected_notes)}")  # Print count of expected notes
    print(f"Generated notes: {[note.note_name for note in notes]}")  # Print generated notes
    print(f"Actual generated notes: {[note.note_name for note in notes]}")  # Print actual generated notes
    print(f"Count of generated notes: {len(notes)}")  # Print count of generated notes
    assert len(notes) == len(expected_notes), "Number of generated notes does not match expected."
    for expected, actual in zip(expected_notes, notes):
        assert expected.note_name == actual.note_name, f"Expected note {expected.note_name}, got {actual.note_name}"
