"""Tests for sequence service."""
import pytest
from unittest.mock import MagicMock, AsyncMock
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.services.sequence_service import SequenceService


@pytest.fixture
def mock_db():
    """Create a mock database."""
    return MagicMock(spec=AsyncIOMotorDatabase)


def test_service_init(mock_db):
    """Test service initialization."""
    service = SequenceService(mock_db)
    assert service.db == mock_db


@pytest.mark.asyncio
async def test_generate_sequence(mock_db):
    """Test generating a sequence."""
    # Create service
    service = SequenceService(mock_db)
    
    # Define test parameters
    params = {
        "key": "C",
        "scale_type": "MAJOR",
        "tempo": 120,
        "length": 4
    }
    
    # Call the method (which is currently a stub)
    result = await service.generate_sequence(params)
    
    # Since the method is a stub that returns None, we just verify it doesn't raise an exception
    assert result is None
