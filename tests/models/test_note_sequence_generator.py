import pytest
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.models.enums import ChordQualityType
from pydantic import BaseModel, Field, ConfigDict, field_validator

@pytest.fixture
def setup_note_sequence_generator() -> NoteSequenceGenerator:
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    chord1 = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
    chord2 = Chord(root=Note(note_name="F", octave=4), quality=ChordQualityType.MAJOR)
    chord_progression = ChordProgression(name="Test Progression", key="C", scale_type="MAJOR", scale_info=scale_info, chords=[chord1, chord2])
    note_sequence = NoteSequence(notes=[])
    
    rhythm_note1 = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_note2 = RhythmNote(position=1.0, duration=1.0, velocity=100, is_rest=False)
    
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note1, rhythm_note2],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,  
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )
    
    rhythm_pattern = RhythmPattern(
        id="test_pattern_id",
        name="Test Pattern",
        description="Test pattern",
        tags=["test"],
        complexity=1.0,
        style="test",
        data=rhythm_data,
        pattern="4 4 4 4"  # Four quarter notes to match the total duration of 4 beats
    )
    
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern
    )
    return generator

def test_generate_sequence(setup_note_sequence_generator: NoteSequenceGenerator) -> None:
    generator = setup_note_sequence_generator
    note_sequence = generator.generate()
    notes = note_sequence.notes
    assert len(notes) == 6  # Expecting 6 notes for 2 chords
    assert isinstance(notes[0], Note)
    assert isinstance(notes[1], Note)
    assert isinstance(notes[2], Note)
    assert isinstance(notes[3], Note)

def test_get_root_note_from_chord_valid(setup_note_sequence_generator: NoteSequenceGenerator) -> None:
    generator = setup_note_sequence_generator
    chord = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
    root_note = generator.chord_progression.get_root_note_from_chord(chord)
    assert root_note.note_name == "C"
    assert root_note.octave == 4

def test_get_root_note_from_chord_none_root(setup_note_sequence_generator: NoteSequenceGenerator) -> None:
    generator = setup_note_sequence_generator
    root_note = generator.chord_progression.get_root_note_from_chord(None)
    assert root_note is None

def test_get_root_note_from_chord_none_scale(setup_note_sequence_generator: NoteSequenceGenerator) -> None:
    generator = setup_note_sequence_generator
    # Create a chord progression with no scale type
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    chord = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
    chord_progression = ChordProgression(name="Test Progression", key="C", scale_type="MAJOR", scale_info=scale_info, chords=[chord])
    generator.chord_progression = chord_progression
    root_note = generator.get_root_note_from_chord(chord)
    assert root_note.note_name == "C"

def test_note_sequence_generator_i_iv_v_i() -> None:
    # Create scale info (C MAJOR)
    scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
    
    # Create chord progression (I-IV-V-I in C MAJOR)
    chord1 = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
    chord2 = Chord(root=Note(note_name="F", octave=4), quality=ChordQualityType.MAJOR)
    chord3 = Chord(root=Note(note_name="G", octave=4), quality=ChordQualityType.MAJOR)
    chord_progression = ChordProgression(name="I-IV-V-I Progression", key="C", scale_type="MAJOR", scale_info=scale_info, chords=[chord1, chord2, chord3, chord1])
    # Create note sequence (simple sequence following chord roots)
    notes = [
        {"note_name": "C", "octave": 4, "duration": 1.0},
        {"note_name": "F", "octave": 4, "duration": 1.0},
        {"note_name": "G", "octave": 4, "duration": 1.0},
        {"note_name": "C", "octave": 4, "duration": 1.0},
    ]
    note_sequence = NoteSequence(notes=[Note(**n) for n in notes])
    
    # Create rhythm pattern (quarter notes)
    rhythm_data = RhythmPatternData(
        notes=[RhythmNote(position=float(i), duration=1.0, velocity=100, is_rest=False) for i in range(4)],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,  
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=4.0,
        style="basic"  
    )
    
    rhythm_pattern = RhythmPattern(
        id="test_pattern_id",
        name="Test Pattern",
        description="Test pattern",
        tags=["test"],
        complexity=1.0,
        style="test",
        data=rhythm_data,
        pattern="4 4 4 4"  # Quarter notes
    )
    
    # Create generator
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern
    )
    
    # Generate sequence
    notes = generator.generate()
    
    # Log the generated notes
    print([note.note_name for note in notes.notes])
    
    # Check generated sequence
    assert len(notes.notes) == 12  # Updated from 9 to 12
    assert all(isinstance(note, Note) for note in notes.notes)
    assert [note.note_name for note in notes.notes] == ["C", "E", "G", "F", "A", "C", "G", "B", "D", "C", "E", "G"]
    assert all(note.octave in [4, 5] for note in notes.notes)  # Allow notes in octaves 4 and 5
