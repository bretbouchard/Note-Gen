import pytest
from src.note_gen.validation.pattern_pipeline import PatternValidationPipeline
from src.note_gen.core.enums import ValidationLevel, ScaleType
from src.note_gen.factories.pattern_factory import PatternFactory

@pytest.fixture
def validation_pipeline():
    return PatternValidationPipeline()

@pytest.fixture
def valid_note_pattern():
    factory = PatternFactory()
    return factory.create_note_pattern(
        root_note="C",
        scale_type=ScaleType.MAJOR,
        intervals=[0, 2, 4, 5, 7]
    )

def test_validate_note_pattern(validation_pipeline, valid_note_pattern):
    assert validation_pipeline.validate_note_pattern(
        valid_note_pattern,
        ValidationLevel.NORMAL
    )

def test_validate_rhythm_pattern(validation_pipeline):
    factory = PatternFactory()
    pattern = factory.create_rhythm_pattern(
        durations=[1.0, 1.0, 1.0, 1.0],
        time_signature=(4, 4)
    )
    
    assert validation_pipeline.validate_rhythm_pattern(
        pattern,
        ValidationLevel.NORMAL
    )