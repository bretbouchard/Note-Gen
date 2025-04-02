import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase

@pytest.mark.asyncio
async def test_connection(test_db: AsyncIOMotorDatabase):
    """Test database connection."""
    assert test_db is not None
    # Verify connection is working
    await test_db.command("ping")
    assert True
