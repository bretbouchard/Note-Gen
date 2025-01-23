from pymongo import IndexModel
from motor.motor_asyncio import AsyncIOMotorDatabase

async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Ensure necessary indexes are created for the collections in the database."""
    try:
        await db.chord_progressions.create_indexes([
            IndexModel([('name', 1)], unique=True),  # Unique index on name
        ])
        await db.note_patterns.create_indexes([
            IndexModel([('pattern_type', 1)], unique=True),  # Unique index on pattern_type
        ])
        await db.rhythm_patterns.create_indexes([
            IndexModel([('complexity', 1)])  # Index on complexity for faster queries
        ])
    except Exception as e:
        print(f"Error creating indexes: {e}")