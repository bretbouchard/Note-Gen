import pytest
import pytest_asyncio
from src.note_gen.database.db import get_db, get_db_conn
from src.note_gen.models.note import Note
from src.note_gen.core.enums import ScaleType, ChordQuality
from src.note_gen.core.constants import (
    DEFAULT_MONGODB_URI,
    DEFAULT_DB_NAME,
    COLLECTION_NAMES,
    DEFAULT_KEY,
    DEFAULT_SCALE_TYPE
)
from pydantic import ValidationError

@pytest_asyncio.fixture
async def db_connection():
    async for conn in get_db():
        yield conn

@pytest.mark.asyncio
async def test_api_functionality(db_connection):
    """Test basic API functionality with proper DB connection."""
    # Test implementation here
    collection = db_connection[COLLECTION_NAMES['chord_progressions']]
    assert collection is not None

@pytest.mark.asyncio
async def test_note_validation():
    """Test note validation in API context."""
    with pytest.raises(ValidationError):
        Note(
            note_name="H",  # Invalid note name
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        )
