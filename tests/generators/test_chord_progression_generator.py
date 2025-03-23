from typing import List, Tuple, Optional, Union, Dict, Any
import pytest
from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.core.enums import ScaleType, ChordQuality
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.patterns import ChordProgressionPattern, ChordProgressionPatternItem
from unittest.mock import patch
import uuid

# Remove the model_rebuild call as it's causing the PydanticDescriptorProxy error
# ChordProgression.model_rebuild()

@pytest.fixture
def basic_generator() -> ChordProgressionGenerator:
    """Create a basic ChordProgressionGenerator for testing."""
    # Create a note with proper octave
    root_note = Note(
        note_name="C", 
        octave=4,
        duration=1.0,
        position=0.0,
        velocity=64,
        stored_midi_number=None,
        scale_degree=None,
        prefer_flats=False
    )
    
    # Create ScaleInfo with proper key format (note_name + octave)
    scale_info = ScaleInfo(
        root=root_note,
        scale_type=ScaleType.MAJOR,
        key="C4"  # Updated to include octave
    )
    
    # Create test chords
    test_chords = [
        Chord(
            root=Note(
                note_name="C", 
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ), 
            quality=ChordQuality.MAJOR,
            inversion=0,
            notes=[],
            id='test',
            description='test',
            tags=['test'],
            genre='test'
        ),
        Chord(
            root=Note(
                note_name="F", 
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ), 
            quality=ChordQuality.MAJOR,
            inversion=0,
            notes=[],
            id='test',
            description='test',
            tags=['test'],
            genre='test'
        ),
        Chord(
            root=Note(
                note_name="G", 
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ), 
            quality=ChordQuality.MAJOR,
            inversion=0,
            notes=[],
            id='test',
            description='test',
            tags=['test'],
            genre='test'
        )
    ]
    
    # Ensure each chord has notes generated
    for chord in test_chords:
        if not chord.notes:
            chord.notes = chord.generate_notes()
    
    return ChordProgressionGenerator(
        name="Test Progression",
        chords=test_chords,
        key="C",  # This is the key name without octave for the generator
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info,
        complexity=0.5,
        test_mode=True  # Enable test mode to bypass some validations
    )

@pytest.fixture
def mock_generate(basic_generator: ChordProgressionGenerator):
    with patch.object(basic_generator, 'generate') as mock:
        mock.return_value = ChordProgression(
            id=str(uuid.uuid4()),
            name="Test Generated Progression",
            chords=["C", "F", "G"],  
            scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR),
            key="C",
            scale_type=ScaleType.MAJOR,
            complexity=0.5,
            description="Test progression",
            tags=["test"],
            quality="test",
            genre="test"
        )
        yield mock

def test_generate(basic_generator: ChordProgressionGenerator) -> None:
    """Test the main generate method with different parameters."""
    with patch.object(basic_generator, 'generate_from_pattern_strings') as mock_pattern:
        with patch.object(basic_generator, 'generate_common_progression') as mock_common_progression:
            with patch.object(basic_generator, 'generate_from_genre') as mock_genre:
                with patch.object(basic_generator, 'generate_from_pattern_strings') as mock_pattern_strings:

                    mock_pattern.return_value = ChordProgression(
                        id=str(uuid.uuid4()),
                        name='Test Progression',
                        chords=[
                            Chord(root=Note(note_name='C', octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=60, scale_degree=None), quality=ChordQuality.MAJOR, inversion=0),
                            Chord(root=Note(note_name='F', octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=65, scale_degree=None), quality=ChordQuality.MAJOR, inversion=0),
                            Chord(root=Note(note_name='G', octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=67, scale_degree=None), quality=ChordQuality.MAJOR, inversion=0),
                        ],
                        key='C',
                        scale_type=ScaleType.MAJOR,
                        scale_info=ScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=60, scale_degree=None), key='C4', scale_type=ScaleType.MAJOR),
                        complexity=0.5,
                        description='Test progression',
                        tags=['test'],
                        quality='test',
                        genre='test'
                    )
                    mock_common_progression.return_value = ChordProgression(
                        id=str(uuid.uuid4()),
                        name="Test Generated Progression",
                        chords=["C", "F", "G"],  
                        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR),
                        key="C",
                        scale_type=ScaleType.MAJOR,
                        complexity=0.5,
                        description="Test progression",
                        tags=["test"],
                        quality="test",
                        genre="test"
                    )
                    mock_genre.return_value = ChordProgression(
                        id=str(uuid.uuid4()),
                        name="Test Generated Progression",
                        chords=["C", "F", "G"],  
                        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR),
                        key="C",
                        scale_type=ScaleType.MAJOR,
                        complexity=0.5,
                        description="Test progression",
                        tags=["test"],
                        quality="test",
                        genre="test"
                    )
                    mock_pattern_strings.return_value = ChordProgression(
                        id=str(uuid.uuid4()),
                        name="Test Generated Progression",
                        chords=["C", "F", "G"],  
                        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR),
                        key="C",
                        scale_type=ScaleType.MAJOR,
                        complexity=0.5,
                        description="Test progression",
                        tags=["test"],
                        quality="test",
                        genre="test"
                    )

                    # Test with pattern
                    pattern: List[Union[str, Dict[str, Any]]] = ["1", "4", "5"]

                    progression = basic_generator.generate(pattern=pattern)

                    assert isinstance(progression, ChordProgression)

                    # Reset mocks
                    mock_pattern.reset_mock()
                    mock_common_progression.reset_mock()
                    mock_genre.reset_mock()
                    mock_pattern_strings.reset_mock()

                    # Test with progression_name
                    progression = basic_generator.generate(progression_name="test_progression")

                    assert isinstance(progression, ChordProgression)

                    # Reset mocks
                    mock_pattern.reset_mock()
                    mock_common_progression.reset_mock()
                    mock_genre.reset_mock()
                    mock_pattern_strings.reset_mock()

                    # Test with genre
                    progression = basic_generator.generate(genre="pop")

                    assert isinstance(progression, ChordProgression)

                    # Reset mocks
                    mock_pattern.reset_mock()
                    mock_common_progression.reset_mock()
                    mock_genre.reset_mock()
                    mock_pattern_strings.reset_mock()

                    # Test with progression_length
                    progression = basic_generator.generate(progression_length=6)

                    assert isinstance(progression, ChordProgression)

                    # Reset mocks
                    mock_pattern.reset_mock()
                    mock_common_progression.reset_mock()
                    mock_genre.reset_mock()
                    mock_pattern_strings.reset_mock()

                    # Test with no parameters (should use default length)
                    progression = basic_generator.generate()

                    assert isinstance(progression, ChordProgression)

def test_generate_from_roman_numerals_valid_pattern(basic_generator: ChordProgressionGenerator) -> None:
    """Test generating a chord progression from Roman numerals."""
    pattern = ["I", "IV", "V", "I"]
    result = basic_generator.generate_from_roman_numerals(pattern)
    assert isinstance(result, list)
    assert len(result) == 4
    for degree, quality in result:
        assert isinstance(degree, int)
        assert isinstance(quality, ChordQuality)

def test_generate_from_roman_numerals_invalid_pattern(basic_generator: ChordProgressionGenerator) -> None:
    """Test generating a chord progression from Roman numerals."""
    pattern = ["INVALID"]
    with pytest.raises(ValueError) as excinfo:
        basic_generator.generate_from_roman_numerals(pattern)
    assert "Invalid Roman numeral" in str(excinfo.value)

def test_generate_from_roman_numerals_empty_pattern(basic_generator: ChordProgressionGenerator) -> None:
    """Test generating a chord progression from Roman numerals."""
    pattern = []
    result = basic_generator.generate_from_roman_numerals(pattern)
    assert isinstance(result, list)
    assert len(result) == 0

def test_generate_large(basic_generator: ChordProgressionGenerator) -> None:
    """Test generating a large chord progression."""
    length = 16
    result = basic_generator.generate_large(length)
    assert isinstance(result, ChordProgression)
    assert len(result.chords) == length
    assert result.scale_type == ScaleType.MAJOR
    assert result.key == "C"
