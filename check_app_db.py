import asyncio
from note_gen.config import settings
from note_gen.database.db import get_db_conn

async def check_db():
    print("Settings:")
    print(f"MONGODB_URI: {settings.MONGODB_URI}")
    print(f"DATABASE_NAME: {settings.DATABASE_NAME}")
    print(f"TESTING: {settings.TESTING}")
    print(f"mongodb_url: {settings.mongodb_url}")
    print(f"database_name: {settings.database_name}")
    
    db = await get_db_conn()
    print(f"\nConnected to database: {db.name}")
    
    collections = await db.list_collection_names()
    print(f"Collections: {collections}")
    
    chord_progressions_count = await db.chord_progressions.count_documents({})
    print(f"Chord progressions count: {chord_progressions_count}")

if __name__ == "__main__":
    asyncio.run(check_db())
