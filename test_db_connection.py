from motor.motor_asyncio import AsyncIOMotorClient

async def test_db_connection():
    try:
        # Connect to the MongoDB server
        client = AsyncIOMotorClient('mongodb://localhost:27017/')
        
        # Access the note_gen database
        db = client['note_gen']
        
        # Fetch and print the names of the collections
        collections = await db.list_collection_names()
        print("Connected to the database. Collections:", collections)
        
    except Exception as e:
        print("Failed to connect to the database:", str(e))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_db_connection())
