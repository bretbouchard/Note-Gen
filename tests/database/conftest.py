"""Database-specific test fixtures."""
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.database.repository import MongoDBRepository
from src.note_gen.models.base import BaseModel

class TestModel(BaseModel):
    name: str
    value: int

@pytest_asyncio.fixture
async def test_repository(test_db_conn: AsyncIOMotorDatabase) -> MongoDBRepository[TestModel]:
    """Create a test repository."""
    return MongoDBRepository[TestModel](test_db_conn, "test_collection")



