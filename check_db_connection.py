import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from note_gen.config import settings
from note_gen.database.db import get_db_conn
from note_gen.core.constants import DATABASE

async def check_connections():
    print("Checking database connections...")
    
    # Check settings
    print("\nSettings:")
    print(f"MONGODB_URL: {settings.MONGODB_URL}")
    print(f"DATABASE_NAME: {settings.DATABASE_NAME}")
    print(f"TESTING: {settings.TESTING}")
    
    # Check constants
    print("\nConstants:")
    print(f"DATABASE['uri']: {DATABASE['uri']}")
    print(f"DATABASE['name']: {DATABASE['name']}")
    
    # Try to connect using settings
    print("\nConnecting using settings...")
    client1 = AsyncIOMotorClient(settings.MONGODB_URL)
    db1 = client1[settings.DATABASE_NAME]
    collections1 = await db1.list_collection_names()
    print(f"Collections in {settings.DATABASE_NAME}: {collections1}")
    
    # Try to connect using constants
    print("\nConnecting using constants...")
    client2 = AsyncIOMotorClient(DATABASE['uri'])
    db2 = client2[DATABASE['name']]
    collections2 = await db2.list_collection_names()
    print(f"Collections in {DATABASE['name']}: {collections2}")
    
    # Try to connect using get_db_conn
    print("\nConnecting using get_db_conn...")
    db3 = await get_db_conn()
    collections3 = await db3.list_collection_names()
    print(f"Collections in {db3.name}: {collections3}")
    
    # Check chord progressions in each database
    print("\nChecking chord progressions...")
    
    cp_count1 = await db1.chord_progressions.count_documents({})
    print(f"Chord progressions in {settings.DATABASE_NAME}: {cp_count1}")
    
    cp_count2 = await db2.chord_progressions.count_documents({})
    print(f"Chord progressions in {DATABASE['name']}: {cp_count2}")
    
    cp_count3 = await db3.chord_progressions.count_documents({})
    print(f"Chord progressions in {db3.name}: {cp_count3}")

if __name__ == "__main__":
    asyncio.run(check_connections())
