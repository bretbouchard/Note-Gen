import pytest
from src.note_gen.database.db import get_db_conn

@pytest.mark.asyncio
async def test_database_connection(test_db):
    """Test database connection."""
    assert test_db is not None
    # Test ping
    result = await test_db.command('ping')
    assert result['ok'] == 1.0
