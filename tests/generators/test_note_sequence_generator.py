import pytest
from src.note_gen.core.enums import ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.generators.note_sequence_generator import NoteSequenceGenerator

@pytest.mark.asyncio
async def test_generate_sequence(scale_info):
    generator = NoteSequenceGenerator()
    sequence = await generator.generate(
        scale_info=scale_info,
        pattern_name="test_pattern"
    )
    assert sequence is not None
    assert len(sequence.notes) > 0
