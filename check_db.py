import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

async def check_database_contents() -> None:
    client: AsyncIOMotorClient
    db: AsyncIOMotorDatabase

    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client.note_gen  # Ensure you are using the correct database name
        print("Connected to database:", db.name)
        collections = await db.list_collection_names()
        print("Collections:", collections)

        note_patterns = await db.note_patterns.find().to_list(None)
        print("Note_patterns:", note_patterns)

        chord_progressions = await db.chord_progressions.find().to_list(None)
        print("Chord_progressions:", chord_progressions)

        rhythm_patterns = await db.rhythm_patterns.find().to_list(None)
        print("Rhythm_patterns:", rhythm_patterns)
    except Exception as e:
        print(f"An error occurred while connecting to the database: {e}")
    finally:
        if client is not None:
            await client.close()  # Only close if client was successfully created

if __name__ == "__main__":
    asyncio.run(check_database_contents())