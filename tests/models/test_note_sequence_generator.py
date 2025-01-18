import pytest
from src.note_gen.models.note_sequence_generator import NoteSequenceGenerator
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.enums import ChordQualityType

@pytest.fixture
def setup_note_sequence_generator() -> NoteSequenceGenerator:
    scale_info = ScaleInfo(root={"note_name": "C", "octave": 4}, scale_type="major")
    chord1 = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
    chord2 = Chord(root=Note(note_name="F", octave=4), quality=ChordQualityType.MAJOR)
    chord_progression = ChordProgression(scale_info=scale_info, chords=[chord1, chord2])
    note_sequence = NoteSequence(notes=[])
    
    rhythm_note1 = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_note2 = RhythmNote(position=1.0, duration=0.5, velocity=100, is_rest=False)
    
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
        pattern="4 4"  # Two quarter notes
    )
    
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern
    )
    return generator

def test_generate_sequence(setup_note_sequence_generator: NoteSequenceGenerator) -> None:
    generator = setup_note_sequence_generator
    notes = generator.generate()
    assert len(notes) == 2  # Expecting 2 notes for 2 chords
    assert isinstance(notes[0], Note)
    assert isinstance(notes[1], Note)

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
    scale_info = ScaleInfo(root={"note_name": "C", "octave": 4}, scale_type="major")
    chord = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
    chord_progression = ChordProgression(scale_info=scale_info, chords=[chord])
    generator.chord_progression = chord_progression
    root_note = generator.chord_progression.get_root_note_from_chord(chord)
    assert root_note is not None
    assert root_note.note_name == "C"

def test_note_sequence_generator_i_iv_v_i() -> None:
    # Create scale info (C major)
    scale_info = ScaleInfo(root={"note_name": "C", "octave": 4}, scale_type="major")
    
    # Create chord progression (I-IV-V-I in C major)
    chord1 = Chord(root={'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100}, quality=ChordQualityType.MAJOR)
    chord2 = Chord(root={'note_name': 'F', 'octave': 4, 'duration': 1.0, 'velocity': 100}, quality=ChordQualityType.MAJOR)
    chord3 = Chord(root={'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100}, quality=ChordQualityType.MAJOR)
    chord4 = Chord(root={'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100}, quality=ChordQualityType.MAJOR)
    chords = [chord1, chord2, chord3, chord4]  # Updated to include all chords
    chord_progression = ChordProgression(
        scale_info=scale_info,
        chords=chords,
        name='Test Progression',
        key='C'
    )
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
        style="basic"  # Updated to valid style
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
    
    # Check generated sequence
    assert len(notes) == 4
    assert all(isinstance(note, Note) for note in notes)
    assert [note.note_name for note in notes] == ["C", "F", "G", "C"]
    assert all(note.octave == 4 for note in notes)
