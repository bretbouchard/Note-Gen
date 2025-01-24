# check_db.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_database_contents():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    try:
        db = client.note_gen
        print("Connected to database: note_gen")
        
        collections = await db.list_collection_names()
        print("Collections:", collections)
        
        # Count and list the number of each type of musical element in the database
        chord_progressions_count = db.chord_progressions.count_documents({})
        note_patterns_count = db.note_patterns.count_documents({})
        rhythm_patterns_count = db.rhythm_patterns.count_documents({})

        print('Number of Chord Progressions:', chord_progressions_count)
        print('Number of Note Patterns:', note_patterns_count)
        print('Number of Rhythm Patterns:', rhythm_patterns_count)

        note_patterns = await db.note_patterns.find().to_list(None)
        chord_progressions = await db.chord_progressions.find().to_list(None)
        rhythm_patterns = await db.rhythm_patterns.find().to_list(None)

        print("Note_patterns:", note_patterns)
        print("Chord_progressions:", chord_progressions)
        print("Rhythm_patterns:", rhythm_patterns)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client:  # Check if client is not None before closing
            client.close()  # Close the client without awaiting

if __name__ == "__main__":
    asyncio.run(check_database_contents())