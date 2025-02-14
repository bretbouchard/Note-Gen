import os
from src.note_gen.database.db import MongoDBConnection
import asyncio

async def main():
    async with MongoDBConnection(uri=os.getenv("MONGODB_URI"), db_name="test_note_gen") as db:
        collections = await db.list_collections()
        print(collections)

if __name__ == '__main__':
    asyncio.run(main())
