"""Database initialization module."""
from motor.motor_asyncio import AsyncIOMotorClient
from src.note_gen.core.constants import DATABASE

# Initialize the MongoDB client
client = AsyncIOMotorClient(DATABASE["uri"])
db = client[DATABASE["name"]]

async def get_database():
    """Get the database instance."""
    return db
