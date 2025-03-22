from motor.motor_asyncio import AsyncIOMotorClient
from src.note_gen.core.constants import (
    DEFAULT_MONGODB_URI,
    DEFAULT_DB_NAME,
    COLLECTION_NAMES
)

async def count_documents():
    client = AsyncIOMotorClient(DEFAULT_MONGODB_URI)
    db = client[DEFAULT_DB_NAME]
    
    counts = {
        name: await db[coll_name].count_documents({})
        for name, coll_name in COLLECTION_NAMES.items()
    }
    return counts

if __name__ == '__main__':
    asyncio.run(count_documents())
