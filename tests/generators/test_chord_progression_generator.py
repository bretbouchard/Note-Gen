import pytest
from typing import List, Tuple
from pydantic import ValidationError
from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.factories.chord_progression_factory import ChordProgressionFactory
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.core.enums import ScaleType, ChordQuality
from enum import Enum

class ValidationLevel(Enum):
    STRICT = "strict"
    RELAXED = "relaxed"
    CUSTOM = "custom"

@pytest.fixture
def scale_info():
    return ScaleInfo(
        key="C",
        scale_type=ScaleType.MAJOR,
        tonic=Note(pitch="C4")  # Fixed: Use pitch instead of note_name and octave
    )

@pytest.fixture
def generator(scale_info):
    return ChordProgressionGenerator(
        name="Test Generator",
        key="C",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info,
        complexity=0.5,
        chords=[
            Chord(
                root=Note(pitch="C4"),  # Fixed: Use pitch format
                quality=ChordQuality.MAJOR,
                name="C"
            ),
            Chord(
                root=Note(pitch="F4"),  # Fixed: Use pitch format
                quality=ChordQuality.MAJOR,
                name="F"
            ),
            Chord(
                root=Note(pitch="G4"),  # Fixed: Use pitch format
                quality=ChordQuality.MAJOR,
                name="G"
            )
        ]
    )

class TestChordProgressionGenerator:
    def test_initialization(self, generator):
        assert generator.name == "Test Generator"
        assert generator.key == "C"
        assert generator.scale_type == ScaleType.MAJOR
        assert generator.complexity == 0.5

    def test_create_test_generator(self, scale_info):
        """Test the creation of a test generator."""
        test_gen = ChordProgressionGenerator.create_test_generator(
            scale_info=scale_info
        )
        assert test_gen.test_mode is True
        assert test_gen.scale_info == scale_info
        assert isinstance(test_gen.chords, list)
        assert len(test_gen.chords) == 0  # Empty list is now allowed in test mode

    @staticmethod
    def validate_scale_type(scale_type_str: str) -> ScaleType:
        """Validate and convert string to ScaleType enum."""
        try:
            return ScaleType[scale_type_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid scale type: {scale_type_str}")

    def test_validate_scale_type(self):
        # Test string input
        result = ChordProgressionGenerator.validate_scale_type("MAJOR")
        assert result == ScaleType.MAJOR
        
        # Test invalid string
        with pytest.raises(ValueError):
            ChordProgressionGenerator.validate_scale_type("INVALID")

    def test_validate_model_fields(self, generator):
        # Test valid model
        validated = generator.validate_model_fields()
        assert validated == generator

        # Test with mismatched key
        with pytest.raises(ValueError):
            ChordProgressionGenerator(
                name="Test",
                key="D",  # Mismatch with scale_info
                scale_type=ScaleType.MAJOR,
                scale_info=generator.scale_info
            )

    async def test_generate_methods(self, generator):
        # Test pattern-based generation
        pattern = [
            {"degree": 1, "quality": ChordQuality.MAJOR},
            {"degree": 4, "quality": ChordQuality.MAJOR},
            {"degree": 5, "quality": ChordQuality.MAJOR}
        ]
        progression = await generator.generate(pattern=pattern)
        assert len(progression) == 3

        # Test genre-based generation
        progression = await generator.generate(genre="pop")
        assert len(progression) > 0

        # Test progression name based generation
        progression = await generator.generate(progression_name="basic")
        assert len(progression) > 0

        # Test random generation
        progression = await generator.generate(progression_length=4)
        assert len(progression) == 4

    def test_generate_from_pattern(self, generator):
        pattern = [
            (1, ChordQuality.MAJOR),
            (4, ChordQuality.MAJOR),
            (5, ChordQuality.MAJOR)
        ]
        
        chords = generator.generate_from_pattern(pattern)
        assert len(chords) == 3
        assert all(isinstance(chord, Chord) for chord in chords)
        assert chords[0].root.note_name == "C"
        assert chords[1].root.note_name == "F"
        assert chords[2].root.note_name == "G"

    def test_generate_random(self, generator):
        prog = generator.generate_random(4)
        assert len(prog) == 4  # Changed from prog.chords
        assert all(isinstance(c, Chord) for c in prog)

    def test_error_cases(self, generator):
        # Test invalid progression name
        with pytest.raises(ValueError):
            generator.generate(progression_name="invalid")

        # Test missing pattern
        with pytest.raises(ValueError):
            generator.generate(pattern=None)

        # Test invalid scale degree
        with pytest.raises(ValueError):
            generator.generate_from_pattern([(8, ChordQuality.MAJOR)])

    @pytest.mark.parametrize("genre", ["pop", "jazz", "blues", "classical"])
    def test_genre_patterns(self, generator, genre):
        assert genre in generator.genre_patterns
        prog = generator.generate(genre=genre)
        assert len(prog) > 0  # Changed from prog.chords

    def test_complexity_handling(self, generator):
        # Test different complexity levels
        for complexity in [0.0, 0.5, 1.0]:
            generator.complexity = complexity
            prog = generator.generate(progression_length=4)
            assert len(prog) == 4  # Changed from prog.chords

    def test_chord_quality_validation(self, generator):
        """Test validation of chord qualities in patterns."""
        # Test valid chord qualities
        pattern = [
            (1, ChordQuality.MAJOR),
            (4, ChordQuality.MINOR),
            (5, ChordQuality.DIMINISHED)
        ]
        prog = generator.generate_from_pattern(pattern)
        assert len(prog) == 3  # Changed from prog.chords
        
        # Test invalid chord quality
        with pytest.raises(ValueError):
            generator.generate_from_pattern([(1, "INVALID_QUALITY")])

    def test_scale_compatibility(self, generator):
        """Test chord compatibility with scale type."""
        # Test major scale typical progressions
        major_pattern = [(1, ChordQuality.MAJOR), (6, ChordQuality.MINOR)]
        prog = generator.generate_from_pattern(major_pattern)
        assert prog[0].quality == ChordQuality.MAJOR  # Changed from prog.chords[0]
        assert prog[1].quality == ChordQuality.MINOR  # Changed from prog.chords[1]

        # Test with different scale type
        minor_generator = ChordProgressionGenerator(
            name="Minor Test",
            key="C",
            scale_type=ScaleType.MINOR,
            scale_info=ScaleInfo(
                tonic=Note(note_name="C", octave=4),
                scale_type=ScaleType.MINOR,
                key="C"
            ),
            complexity=0.5
        )
        minor_pattern = [(1, ChordQuality.MINOR), (5, ChordQuality.MAJOR)]
        prog = minor_generator.generate_from_pattern(minor_pattern)
        assert prog[0].quality == ChordQuality.MINOR  # Changed from prog.chords[0]

    def test_progression_complexity_calculation(self, generator):
        """Test complexity calculation for different progression patterns."""
        simple_pattern = [
            (1, ChordQuality.MAJOR),
            (4, ChordQuality.MAJOR),
            (5, ChordQuality.MAJOR)
        ]
        
        # Add proper value parameters
        assert generator.calculate_progression_complexity(simple_pattern) == 0.3
        assert generator.calculate_voice_leading_complexity(simple_pattern) == 0.4
        assert generator.calculate_harmonic_complexity(simple_pattern) == 0.5

    def test_pattern_validation(self, generator):
        """Test validation of progression patterns."""
        # Test empty pattern
        with pytest.raises(ValueError):
            generator.generate_from_pattern([])
            
        # Test pattern with invalid degrees
        with pytest.raises(ValueError):
            generator.generate_from_pattern([(-1, ChordQuality.MAJOR)])
            
        # Test pattern with None values
        with pytest.raises(ValueError):
            generator.generate_from_pattern([(None, ChordQuality.MAJOR)])

    def test_genre_specific_constraints(self, generator):
        """Test genre-specific progression constraints."""
        # Test pop progression length
        pop_prog = generator.generate(genre="pop")
        assert 3 <= len(pop_prog.chords) <= 8
        
        # Test jazz progression complexity
        jazz_prog = generator.generate(genre="jazz")
        assert jazz_prog.complexity >= 0.6  # Jazz should be more complex

    def test_generate_from_roman_numerals(self, generator):
        """Test generation from Roman numeral patterns."""
        # Test basic Roman numeral pattern
        pattern = ["I", "IV", "V"]
        prog = generator.generate_from_roman_numerals(pattern)
        assert len(prog.chords) == 3
        assert prog.chords[0].root.note_name == "C"
        assert prog.chords[1].root.note_name == "F"
        assert prog.chords[2].root.note_name == "G"

        # Test with modifiers
        pattern = ["i", "iv", "V7"]
        prog = generator.generate_from_roman_numerals(pattern)
        assert len(prog.chords) == 3
        assert prog.chords[2].quality == ChordQuality.DOMINANT_SEVENTH

        # Test invalid Roman numerals
        with pytest.raises(ValueError):
            generator.generate_from_roman_numerals(["VIII"])

    def test_voice_leading_rules(self, generator):
        """Test voice leading rules enforcement."""
        # Test parallel fifths avoidance
        pattern = [
            (1, ChordQuality.MAJOR),
            (2, ChordQuality.MAJOR)  # Should raise error due to parallel fifths
        ]
        with pytest.raises(ValueError, match="Voice leading rule violation"):
            generator.generate_from_pattern(pattern)
        
        # Test proper voice leading
        valid_pattern = [
            (1, ChordQuality.MAJOR),
            (4, ChordQuality.MAJOR),  # Proper voice leading
            (5, ChordQuality.MAJOR)
        ]
        prog = generator.generate_from_pattern(valid_pattern)
        assert len(prog.chords) == 3

    def test_voice_leading_rules_comprehensive(self, generator):
        """Test comprehensive voice leading rules."""
        # Test parallel octaves
        parallel_octaves = [
            (1, ChordQuality.MAJOR),
            (5, ChordQuality.MAJOR),  # Movement that would create parallel octaves
        ]
        with pytest.raises(ValueError, match="Parallel octaves detected"):
            generator.validate_voice_leading(parallel_octaves)
        
        # Test voice crossing
        voice_crossing = [
            (1, ChordQuality.MAJOR),
            (4, ChordQuality.MAJOR),
            (2, ChordQuality.MINOR)  # Creates voice crossing
        ]
        with pytest.raises(ValueError, match="Voice crossing detected"):
            generator.validate_voice_leading(voice_crossing)
        
        # Test large leaps
        large_leap = [
            (1, ChordQuality.MAJOR),
            (6, ChordQuality.MINOR)  # Creates large leap
        ]
        with pytest.raises(ValueError, match="Large leap detected"):
            generator.validate_voice_leading(large_leap)
        
        # Test valid voice leading
        valid_progression = [
            (1, ChordQuality.MAJOR),
            (4, ChordQuality.MAJOR),
            (5, ChordQuality.DOMINANT_SEVENTH),
            (1, ChordQuality.MAJOR)
        ]
        # Should not raise any exceptions
        assert generator.validate_voice_leading(valid_progression) is True

    def test_secondary_dominants(self, generator):
        """Test secondary dominant generation and resolution."""
        # Test V/V (secondary dominant of V)
        pattern = [(1, ChordQuality.MAJOR), (2, ChordQuality.DOMINANT_SEVENTH), 
                  (5, ChordQuality.MAJOR), (1, ChordQuality.MAJOR)]
        prog = generator.generate_from_pattern(pattern)
        
        # V/V should be D7 in C major, resolving to G
        secondary_dominant = prog.chords[1]
        resolution = prog.chords[2]
        assert secondary_dominant.root.note_name == "D"
        assert secondary_dominant.quality == ChordQuality.DOMINANT_SEVENTH
        assert resolution.root.note_name == "G"

    def test_secondary_dominants_comprehensive(self, generator):
        """Test comprehensive secondary dominant handling."""
        # Test V/V (secondary dominant of V)
        v_of_v_pattern = [
            (1, ChordQuality.MAJOR),
            ("V/V", ChordQuality.DOMINANT_SEVENTH),  # Secondary dominant
            (5, ChordQuality.MAJOR)
        ]
        prog = generator.generate_with_secondary_dominants(v_of_v_pattern)
        assert prog[1].root.note_name == "D"  # V/V in C major is D7
        assert prog[1].quality == ChordQuality.DOMINANT_SEVENTH
        
        # Test V/ii
        v_of_ii_pattern = [
            (1, ChordQuality.MAJOR),
            ("V/ii", ChordQuality.DOMINANT_SEVENTH),
            (2, ChordQuality.MINOR)
        ]
        prog = generator.generate_with_secondary_dominants(v_of_ii_pattern)
        assert prog[1].root.note_name == "E"  # V/ii in C major is E7
        
        # Test resolution validation
        invalid_resolution = [
            (1, ChordQuality.MAJOR),
            ("V/V", ChordQuality.DOMINANT_SEVENTH),
            (4, ChordQuality.MAJOR)  # Invalid resolution
        ]
        with pytest.raises(ValueError, match="Invalid secondary dominant resolution"):
            generator.generate_with_secondary_dominants(invalid_resolution)

    def test_chord_substitutions(self, generator):
        """Test chord substitution mechanisms."""
        # Test tritone substitution
        original_pattern = [(1, ChordQuality.MAJOR), (5, ChordQuality.DOMINANT_SEVENTH), 
                          (1, ChordQuality.MAJOR)]
        prog = generator.generate_with_substitutions(original_pattern, 
                                                   substitution_type="tritone")
        
        # In C major, G7 should be substituted with Db7
        subbed_chord = prog.chords[1]
        assert subbed_chord.root.note_name in ["Db", "C#"]
        assert subbed_chord.quality == ChordQuality.DOMINANT_SEVENTH

    def test_modal_interchange(self, generator):
        """Test modal interchange chord generation."""
        # Test borrowing chords from parallel minor
        prog = generator.generate_with_modal_interchange(
            base_pattern=[(1, ChordQuality.MAJOR), (4, ChordQuality.MAJOR)],
            interchange_scale=ScaleType.MINOR
        )
        
        # Should include at least one borrowed chord
        borrowed_chords = [chord for chord in prog.chords 
                         if chord.quality in [ChordQuality.MINOR, 
                                            ChordQuality.DIMINISHED]]
        assert len(borrowed_chords) > 0

    def test_complexity_based_pattern_generation(self, generator):
        """Test pattern generation based on different complexity levels."""
        # Test low complexity
        generator.complexity = 0.2
        prog = generator.generate(progression_length=4)
        assert all(chord.quality in [ChordQuality.MAJOR, ChordQuality.MINOR] 
                  for chord in prog.chords)
        
        # Test medium complexity
        generator.complexity = 0.5
        prog = generator.generate(progression_length=4)
        assert any(chord.quality in [ChordQuality.MAJOR_SEVENTH, 
                                   ChordQuality.MINOR_SEVENTH,
                                   ChordQuality.DOMINANT_SEVENTH] 
                  for chord in prog.chords)
        
        # Test high complexity
        generator.complexity = 0.8
        prog = generator.generate(progression_length=4)
        assert any(chord.quality in [ChordQuality.HALF_DIMINISHED_SEVENTH,
                                   ChordQuality.AUGMENTED,
                                   ChordQuality.DIMINISHED_SEVENTH]
                  for chord in prog.chords)

    def test_pattern_validation_edge_cases(self, generator):
        """Test edge cases in pattern validation."""
        # Test single chord pattern
        single_pattern = [(1, ChordQuality.MAJOR)]
        prog = generator.generate_from_pattern(single_pattern)
        assert len(prog.chords) == 1
        
        # Test maximum length pattern
        max_pattern = [(1, ChordQuality.MAJOR)] * 16
        prog = generator.generate_from_pattern(max_pattern)
        assert len(prog.chords) == 16
        
        # Test invalid degree combinations
        with pytest.raises(ValueError):
            generator.generate_from_pattern([(8, ChordQuality.MAJOR)])
        
        with pytest.raises(ValueError):
            generator.generate_from_pattern([(0, ChordQuality.MAJOR)])

    def test_scale_integration_scenarios(self, generator):
        """Test various scale integration scenarios."""
        # Test with different scale types
        scales = [ScaleType.MINOR, ScaleType.HARMONIC_MINOR, 
                 ScaleType.MELODIC_MINOR, ScaleType.DORIAN]
        
        for scale_type in scales:
            gen = ChordProgressionGenerator(
                name="Scale Test",
                key="C",
                scale_type=scale_type,
                scale_info=ScaleInfo(
                    key="C",
                    scale_type=scale_type
                ),
                complexity=0.5
            )
            prog = gen.generate(progression_length=4)
            # Verify progression length and chord qualities match scale type
            assert len(prog.chords) > 0
            
            # Verify first chord quality matches scale type
            first_chord = prog.chords[0]
            if scale_type in [ScaleType.MINOR, ScaleType.HARMONIC_MINOR, 
                            ScaleType.MELODIC_MINOR, ScaleType.DORIAN]:
                assert first_chord.quality == ChordQuality.MINOR
            else:
                assert first_chord.quality == ChordQuality.MAJOR
                
            # Verify all chords follow scale-specific rules
            for chord in prog.chords:
                assert chord.scale_degree is not None
                assert 1 <= chord.scale_degree <= 7
                assert chord.quality in ChordQuality.__members__.values()

    def test_chord_quality_mapping(self, generator):
        """Test chord quality mapping for different scale degrees."""
        # Test major scale degree mappings
        mappings = [
            (1, ChordQuality.MAJOR),
            (2, ChordQuality.MINOR),
            (3, ChordQuality.MINOR),
            (4, ChordQuality.MAJOR),
            (5, ChordQuality.MAJOR),
            (6, ChordQuality.MINOR),
            (7, ChordQuality.DIMINISHED)
        ]
        
        for degree, expected_quality in mappings:
            pattern = [(degree, expected_quality)]
            prog = generator.generate_from_pattern(pattern)
            assert prog.chords[0].quality == expected_quality

    def test_progression_transformation(self, generator):
        """Test progression transformation methods."""
        base_pattern = [(1, ChordQuality.MAJOR), (4, ChordQuality.MAJOR),
                       (5, ChordQuality.MAJOR)]
        
        # Test transposition
        prog = generator.generate_from_pattern(base_pattern)
        transposed = generator.transpose_progression(prog, "G")
        assert transposed.chords[0].root.note_name == "G"
        
        # Test inversion
        inverted = generator.invert_progression(prog)
        assert len(inverted.chords) == len(prog.chords)
        assert inverted.chords != prog.chords

    def test_error_handling_and_validation(self, generator):
        """Test error handling and validation scenarios."""
        # Test invalid complexity value
        with pytest.raises(ValueError):
            generator.complexity = 1.5
            
        # Test invalid key
        with pytest.raises(ValueError):
            ChordProgressionGenerator(
                name="Invalid",
                key="H",  # Invalid key
                scale_type=ScaleType.MAJOR,
                scale_info=generator.scale_info
            )
            
        # Test mismatched scale info
        with pytest.raises(ValueError):
            ChordProgressionGenerator(
                name="Mismatched",
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=ScaleInfo(
                    key="D",  # Mismatched key
                    scale_type=ScaleType.MAJOR
                )
            )

    def test_progression_analysis(self, generator):
        """Test progression analysis functionality."""
        pattern = [(1, ChordQuality.MAJOR), (4, ChordQuality.MAJOR),
                  (5, ChordQuality.DOMINANT_SEVENTH), (1, ChordQuality.MAJOR)]
        prog = generator.generate_from_pattern(pattern)
        
        # Test cadence detection
        cadence_type = generator.analyze_cadence(prog)
        assert cadence_type in ["perfect", "imperfect", "deceptive", "half"]
        
        # Test progression complexity analysis
        complexity_score = generator.analyze_complexity(prog)
        assert 0 <= complexity_score <= 1
        
        # Test chord function analysis
        functions = generator.analyze_chord_functions(prog)
        assert len(functions) == len(prog.chords)
        assert "tonic" in functions
        assert "dominant" in functions

    def test_genre_specific_patterns(self, generator):
        """Test genre-specific progression patterns."""
        genres = ["jazz", "blues", "pop", "classical"]
        
        for genre in genres:
            prog = generator.generate(genre=genre)
            
            if genre == "jazz":
                # Check for seventh chords
                assert any(chord.quality in [ChordQuality.MAJOR_SEVENTH,
                                           ChordQuality.MINOR_SEVENTH,
                                           ChordQuality.DOMINANT_SEVENTH]
                          for chord in prog.chords)
                
            elif genre == "blues":
                # Check for dominant seventh chords
                assert any(chord.quality == ChordQuality.DOMINANT_SEVENTH
                          for chord in prog.chords)
                
            elif genre == "pop":
                # Check typical pop progression length
                assert 3 <= len(prog.chords) <= 5

    def test_roman_numeral_generation(self, generator):
        """Test generation from roman numerals."""
        from src.note_gen.models.roman_numeral import RomanNumeral
        
        numerals = [
            RomanNumeral(numeral="I"),
            RomanNumeral(numeral="IV"),
            RomanNumeral(numeral="V")
        ]
        
        prog = generator.generate_from_roman_numerals(numerals)
        assert len(prog.chords) == 3
        assert prog.chords[0].root.note_name == "C"
        assert prog.chords[1].root.note_name == "F"
        assert prog.chords[2].root.note_name == "G"

    def test_scale_degree_integration(self, generator):
        """Test integration with ScaleDegree model."""
        from src.note_gen.models.scale_degree import ScaleDegree
        
        degrees = [
            ScaleDegree(degree=1, quality=ChordQuality.MAJOR),
            ScaleDegree(degree=4, quality=ChordQuality.MAJOR),
            ScaleDegree(degree=5, quality=ChordQuality.MAJOR)
        ]
        
        prog = generator.generate_from_scale_degrees(degrees)
        assert len(prog.chords) == 3
        assert prog.chords[0].quality == ChordQuality.MAJOR
        assert prog.chords[1].quality == ChordQuality.MAJOR
        assert prog.chords[2].quality == ChordQuality.MAJOR

    def test_edge_cases(self, generator):
        """Test edge cases and error handling."""
        # Test empty pattern
        with pytest.raises(ValueError, match="Empty pattern"):
            generator.generate_from_pattern([])
        
        # Test invalid chord quality combinations
        with pytest.raises(ValueError, match="Invalid chord quality"):
            generator.generate_from_pattern([
                (1, ChordQuality.AUGMENTED),  # Unusual in major scale
                (4, ChordQuality.MAJOR)
            ])
        
        # Test octave boundaries
        high_pattern = [(1, ChordQuality.MAJOR)] * 12  # Too many repetitions
        with pytest.raises(ValueError, match="Exceeds octave range"):
            generator.generate_from_pattern(high_pattern)

    def test_pattern_generation_with_validation_levels(self, generator):
        """Test pattern generation with different validation levels."""
        pattern = [
            (1, ChordQuality.MAJOR),
            (4, ChordQuality.MAJOR),
            (5, ChordQuality.DOMINANT_SEVENTH)
        ]
        
        # Test strict validation
        prog_strict = generator.generate_from_pattern(
            pattern,
            validation_level=ValidationLevel.STRICT
        )
        assert len(prog_strict) == 3
        assert all(chord.is_valid(ValidationLevel.STRICT) for chord in prog_strict)
        
        # Test relaxed validation
        prog_relaxed = generator.generate_from_pattern(
            pattern,
            validation_level=ValidationLevel.RELAXED
        )
        assert len(prog_relaxed) == 3
        
        # Test custom validation rules
        custom_rules = {
            "allow_parallel_fifths": True,
            "max_voice_leap": 8,
            "require_resolution": False
        }
        prog_custom = generator.generate_from_pattern(
            pattern,
            validation_level=ValidationLevel.CUSTOM,
            validation_rules=custom_rules
        )
        assert len(prog_custom) == 3
