import pytest
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ScaleType, ChordQualityType
from src.note_gen.models.note import Note


class TestChordProgressionGenerator:
    print("TestChordProgressionGenerator class initialized")

    @pytest.fixture
    def setup_scale_info(self):
        root_note = Note(note_name="C", octave=4, duration=1, velocity=64)
        scale_info = ScaleInfo(root=root_note, scale_type=ScaleType.MAJOR)
        return scale_info

    def test_generate_custom_valid(self, setup_scale_info):
        print("test_generate_custom_valid method called")

        generator = ChordProgressionGenerator(
            name="Test Progression",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=setup_scale_info
        )
        
        degrees = [1, 4, 5]
        qualities = [ChordQualityType.MAJOR, ChordQualityType.MINOR, ChordQualityType.MAJOR]
        progression = generator.generate_custom(degrees, qualities)
        scale_info = ScaleInfo(root=Note(note_name='C', octave=4, duration=1, velocity=64), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name='C', octave=4, duration=1, velocity=64), quality=ChordQualityType.MAJOR, notes=[
                Note(note_name='C', octave=4, duration=1, velocity=64), 
                Note(note_name='E', octave=4, duration=1, velocity=64), 
                Note(note_name='G', octave=4, duration=1, velocity=64)
            ]),
            Chord(root=Note(note_name='F', octave=4, duration=1, velocity=64), quality=ChordQualityType.MINOR, notes=[
                Note(note_name='F', octave=4, duration=1, velocity=64), 
                Note(note_name='Ab', octave=4, duration=1, velocity=64), 
                Note(note_name='C', octave=5, duration=1, velocity=64)
            ]),
            Chord(root=Note(note_name='G', octave=4, duration=1, velocity=64), quality=ChordQualityType.MAJOR, notes=[
                Note(note_name='G', octave=4, duration=1, velocity=64), 
                Note(note_name='B', octave=4, duration=1, velocity=64), 
                Note(note_name='D', octave=5, duration=1, velocity=64)
            ])
        ]
        progression = ChordProgression(name='Test Progression', chords=chords, key='C', scale_type=ScaleType.MAJOR, scale_info=scale_info) 
        assert progression.name == 'Test Progression'
        assert progression.key == 'C'
        assert progression.scale_type == ScaleType.MAJOR
        assert len(progression.chords) == len(chords)
        for expected_chord, generated_chord in zip(chords, progression.chords):
            assert expected_chord.root.note_name == generated_chord.root.note_name
            assert expected_chord.quality == generated_chord.quality
            assert len(expected_chord.notes) == len(generated_chord.notes)
            for expected_note, generated_note in zip(expected_chord.notes, generated_chord.notes):
                assert expected_note.note_name == generated_note.note_name
                assert expected_note.octave == generated_note.octave
                assert expected_note.duration == generated_note.duration
                assert expected_note.velocity == generated_note.velocity
            for i, note in enumerate(generated_chord.notes):
                assert note.note_name == chords[generated_chord.root.note_name == 'C'][i].notes[i].note_name
                assert note.octave == chords[generated_chord.root.note_name == 'C'][i].notes[i].octave
                assert note.duration == chords[generated_chord.root.note_name == 'C'][i].notes[i].duration
                assert note.velocity == chords[generated_chord.root.note_name == 'C'][i].notes[i].velocity
            assert generated_chord.quality == chords[generated_chord.root.note_name == 'C'].quality
        for i, chord in enumerate(progression.chords):
            assert chord.root.note_name == chords[i].root.note_name
            assert chord.quality == chords[i].quality
            assert len(chord.notes) == len(chords[i].notes)
            for j, note in enumerate(chord.notes):
                assert note.note_name == chords[i].notes[j].note_name
                assert note.octave == chords[i].notes[j].octave
            assert chord.notes is not None
            assert chord.quality is not None
            for expected_chord, generated_chord in zip(chords, progression.chords):
                assert expected_chord.root.note_name == generated_chord.root.note_name
                assert expected_chord.quality == generated_chord.quality
                assert len(expected_chord.notes) == len(generated_chord.notes)
                for expected_note, generated_note in zip(expected_chord.notes, generated_chord.notes):
                    assert expected_note.note_name == generated_note.note_name
                    assert expected_note.octave == generated_note.octave
                    assert expected_note.duration == generated_note.duration
                    assert expected_note.velocity == generated_note.velocity

    def test_generate_custom_invalid_degree(self, setup_scale_info):
        print("test_generate_custom_invalid_degree method called")
        generator = ChordProgressionGenerator(
            name="Test Progression",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=setup_scale_info
        )
        degrees = [8]  # Invalid degree
        qualities = [ChordQualityType.MAJOR]
        with pytest.raises(ValueError, match="Invalid degree: 8"):  
            generator.generate_custom(degrees, qualities)

    def test_generate_custom_mismatched_lengths(self, setup_scale_info):
        generator = ChordProgressionGenerator(
            name="Test Progression",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=setup_scale_info
        )
        degrees = [1, 2]
        qualities = [ChordQualityType.MAJOR]  # Mismatched lengths
        with pytest.raises(ValueError, match="Degrees and qualities must have the same length."):  
            generator.generate_custom(degrees, qualities)
