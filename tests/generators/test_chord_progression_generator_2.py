import pytest
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ScaleType


from src.note_gen.models.note import Note
from src.note_gen.models.roman_numeral import RomanNumeral


class TestChordProgressionGenerator:
    print("TestChordProgressionGenerator class initialized")

    @pytest.fixture
    def setup_scale_info(self):
        root_note = Note(note_name="C", octave=4, duration=1, velocity=64)
        scale_info = ScaleInfo(root=root_note, scale_type=ScaleType.MAJOR)
        return scale_info
    
    @pytest.fixture
    def chord_progression_generator(self, setup_scale_info):
        """Create a ChordProgressionGenerator instance for testing."""
        generator = ChordProgressionGenerator(
            name="Test Progression",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=setup_scale_info,
            complexity=0.5,
            test_mode=True
        )
        return generator
    
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
        qualities = [ChordQuality.MAJOR, ChordQuality.MINOR, ChordQuality.MAJOR]
        progression = generator.generate_custom(degrees, qualities)
        
        assert progression.name == 'Test Progression'
        assert progression.key == 'C'
        assert progression.scale_type == ScaleType.MAJOR
        assert len(progression.chords) == len(degrees)
        
        # Simplified chord verification
        for i, chord in enumerate(progression.chords):
            assert chord.root.note_name == ['C', 'F', 'G'][i]
            assert chord.quality == qualities[i]  # Compare the enum objects directly
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
        qualities = [ChordQuality.MAJOR]
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
        qualities = [ChordQuality.MAJOR]
        with pytest.raises(ValueError, match="Degrees and qualities must have the same length."):  
            generator.generate_custom(degrees, qualities)

    def test_calculate_pattern_complexity(self, chord_progression_generator):
        """Test complexity calculation for different chord patterns."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Simple major progression
        simple_pattern = [(1, ChordQuality.MAJOR), (4, ChordQuality.MAJOR), (5, ChordQuality.MAJOR)]
        
        # Use the class method directly
        complexity = ChordProgressionGenerator.calculate_pattern_complexity(simple_pattern)
        
        # Log the complexity value for debugging
        logger.info(f"Simple pattern complexity: {complexity}")
        
        assert 0 <= complexity <= 1, "Complexity should be between 0 and 1"
        assert complexity < 0.5, f"Simple progression should have low complexity, got {complexity}"
        
        # Complex progression with varied qualities
        complex_pattern = [
            (2, ChordQuality.MINOR_SEVENTH), 
            (5, ChordQuality.DOMINANT_SEVENTH), 
            (1, ChordQuality.MAJOR_SEVENTH), 
            (6, ChordQuality.DIMINISHED)
        ]
        
        # Use the class method directly
        complex_complexity = ChordProgressionGenerator.calculate_pattern_complexity(complex_pattern)
        
        # Log the complexity value for debugging
        logger.info(f"Complex pattern complexity: {complex_complexity}")
        
        assert 0 <= complex_complexity <= 1, "Complexity should be between 0 and 1"
        assert complex_complexity > 0.5, f"Complex progression should have high complexity, got {complex_complexity}"
