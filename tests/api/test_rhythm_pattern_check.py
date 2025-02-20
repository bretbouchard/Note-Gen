"""
Tests for rhythm pattern functionality.
"""
import pytest
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@pytest.fixture
async def test_rhythm_pattern(async_test_client):
    """
    Fixture to create a test rhythm pattern with a unique name.
    Ensures cleanup after the test.
    """
    rhythm_note = RhythmNote(position=0.0, duration=1.0, velocity=100, is_rest=False)
    rhythm_data = RhythmPatternData(
        notes=[rhythm_note],
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
    
    unique_name = f"Test Rhythm Pattern {uuid.uuid4()}"
    rhythm_pattern = RhythmPattern(
        name=unique_name,
        description="A test rhythm pattern",
        data=rhythm_data,
        tags=["test"],
        is_test=True
    )
    
    # Create the pattern
    response = await async_test_client.post('/api/v1/rhythm-patterns', json=rhythm_pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()

    # Cleanup the pattern after the test
    try:
        yield created_pattern
    finally:
        try:
            await async_test_client.delete(f'/api/v1/rhythm-patterns/{created_pattern["id"]}')
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

# Keep all the existing test functions as they are