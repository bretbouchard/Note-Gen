import pytest
from src.note_gen.models.chord import Chord
from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.chord_quality import ChordQualityType

from src.note_gen.models.note import Note
from src.note_gen.models.roman_numeral import RomanNumeral


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
            scale_info=setup_scale_info,
            complexity=0.5,
            test_mode=True
        )
        
        degrees = [1, 4, 5]
        qualities = [ChordQualityType.MAJOR, ChordQualityType.MINOR, ChordQualityType.MAJOR]
        progression = generator.generate_custom(degrees, qualities)
        
        assert progression.name == 'Test Progression'
        assert progression.key == 'C'
        assert progression.scale_type == ScaleType.MAJOR
        assert len(progression.chords) == len(degrees)
        
        # Simplified chord verification
        for i, chord in enumerate(progression.chords):
            assert chord.root.note_name == ['C', 'F', 'G'][i]
            assert chord.quality == qualities[i]
            assert len(chord.notes) == 3  # Assuming triads

    def test_generate_custom_invalid_degree(self, setup_scale_info):
        print("test_generate_custom_invalid_degree method called")
        generator = ChordProgressionGenerator(
            name="Test Progression",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=setup_scale_info,
            complexity=0.5,
            test_mode=True
        )
        degrees = [8]
        qualities = [ChordQualityType.MAJOR]
        with pytest.raises(ValueError, match="Invalid degree: 8"):  
            generator.generate_custom(degrees, qualities)

    def test_generate_custom_mismatched_lengths(self, setup_scale_info):
        print("test_generate_custom_mismatched_lengths method called")
        generator = ChordProgressionGenerator(
            name="Test Progression",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=setup_scale_info,
            complexity=0.5,
            test_mode=True
        )
        degrees = [1, 2]
        qualities = [ChordQualityType.MAJOR]
        with pytest.raises(ValueError, match="Degrees and qualities must have the same length."):  
            generator.generate_custom(degrees, qualities)
