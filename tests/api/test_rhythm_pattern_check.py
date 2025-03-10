"""
Tests for rhythm pattern functionality.
"""
import pytest
from src.note_gen.models.patterns import RhythmPattern, RhythmPatternData, RhythmNote
import uuid
import logging
import os

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

@pytest.mark.asyncio
async def test_rhythm_pattern_with_float_values(rhythm_pattern_fixture, client):
    """Test that rhythm patterns with float values in the pattern field are properly handled."""
    
    # Get the pattern from the fixture
    fixture_pattern = rhythm_pattern_fixture["pattern"]
    pattern_id = rhythm_pattern_fixture["id"]
    
    # Verify the fixture has a mix of int and float values
    assert any(isinstance(val, float) for val in fixture_pattern["pattern"]), "Test fixture should have float values in pattern"
    
    # Get the pattern from the API
    response = await client.get(f"/api/v1/rhythm-patterns/{pattern_id}")
    
    # Check the response
    assert response.status_code == 200, f"Failed to get rhythm pattern: {response.text}"
    
    # Parse the response data
    data = response.json()
    
    # Verify the pattern values are preserved
    assert data["pattern"] == fixture_pattern["pattern"], "Pattern values should be preserved"
    
    # Create a new rhythm pattern with float values
    new_pattern = {
        "name": "Float Value Rhythm Pattern",
        "pattern": [0.25, 0.5, 0.75, 1.0, 0.5],  # All float values
        "description": "A rhythm pattern with float values",
        "tags": ["test", "float"],
        "complexity": 3.0,
        "data": {
            "notes": [
                {"duration": 0.25, "position": 0, "is_rest": False, "velocity": 100},
                {"duration": 0.5, "position": 0.25, "is_rest": False, "velocity": 90},
                {"duration": 0.75, "position": 0.75, "is_rest": False, "velocity": 80},
                {"duration": 1.0, "position": 1.5, "is_rest": False, "velocity": 100},
                {"duration": 0.5, "position": 2.5, "is_rest": False, "velocity": 90}
            ],
            "time_signature": "4/4"
        }
    }
    
    # Send the creation request
    create_response = await client.post("/api/v1/rhythm-patterns/", json=new_pattern)
    
    # Check that creation succeeded
    assert create_response.status_code == 201, f"Failed to create rhythm pattern: {create_response.text}"
    
    # Get the created pattern ID
    created_id = create_response.json()["id"]
    
    try:
        # Fetch the created pattern to verify it was stored correctly
        get_response = await client.get(f"/api/v1/rhythm-patterns/{created_id}")
        
        # Check the fetch response
        assert get_response.status_code == 200, f"Failed to get created rhythm pattern: {get_response.text}"
        
        # Parse the fetched data
        fetched_data = get_response.json()
        
        # Verify the pattern values are preserved
        assert fetched_data["pattern"] == new_pattern["pattern"], "Float pattern values should be preserved"
        
    finally:
        # Clean up - delete the created pattern
        if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
            delete_response = await client.delete(f"/api/v1/rhythm-patterns/{created_id}")
            assert delete_response.status_code == 200, f"Failed to delete test rhythm pattern: {delete_response.text}"

@pytest.mark.asyncio
async def test_rhythm_pattern_with_rests(client):
    """Test that rhythm patterns with negative values (rests) are properly handled via the API."""
    
    # Create a new rhythm pattern with both notes and rests
    rest_pattern = {
        "name": "Rest Value Rhythm Pattern",
        "pattern": [1.0, -0.5, 2.0],  # 1 beat note, 0.5 beat rest, 2 beat note
        "description": "A rhythm pattern with rest values (negative numbers)",
        "tags": ["test", "rest"],
        "complexity": 3.0,
        "data": {
            "notes": [
                # First note (1.0 beat)
                {"duration": 1.0, "position": 0, "is_rest": False, "velocity": 100},
                # Rest (0.5 beat)
                {"duration": 0.5, "position": 1.0, "is_rest": True, "velocity": 0},
                # Second note (2.0 beat)
                {"duration": 2.0, "position": 1.5, "is_rest": False, "velocity": 100}
            ],
            "time_signature": "4/4",
            "groove_type": "straight"
        }
    }
    
    # Send the creation request
    create_response = await client.post("/api/v1/rhythm-patterns/", json=rest_pattern)
    
    # Check that creation succeeded
    assert create_response.status_code == 201, f"Failed to create rhythm pattern: {create_response.text}"
    
    # Get the created pattern ID
    created_id = create_response.json()["id"]
    
    try:
        # Fetch the created pattern to verify it was stored correctly
        get_response = await client.get(f"/api/v1/rhythm-patterns/{created_id}")
        
        # Check the fetch response
        assert get_response.status_code == 200, f"Failed to get created rhythm pattern: {get_response.text}"
        
        # Parse the fetched data
        fetched_data = get_response.json()
        
        # Verify the pattern with rests is preserved
        assert fetched_data["pattern"] == rest_pattern["pattern"], "Pattern with rests should be preserved"
        
        # Specifically check that the negative value (rest) is preserved
        assert fetched_data["pattern"][1] == -0.5, "Rest value should be preserved as negative"
        
        # Verify the rest in notes data is properly preserved
        assert fetched_data["data"]["notes"][1]["is_rest"] == True, "Rest flag should be set to True"
        assert fetched_data["data"]["notes"][1]["duration"] == 0.5, "Rest duration should match pattern"
        
    finally:
        # Cleanup - delete the pattern
        if created_id:
            delete_response = await client.delete(f"/api/v1/rhythm-patterns/{created_id}")
            # Only log an error if deletion fails, don't fail the test
            if delete_response.status_code != 204:
                logger.error(f"Failed to delete test pattern: {delete_response.text}")