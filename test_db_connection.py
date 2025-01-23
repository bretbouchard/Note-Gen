import asyncio
import logging
from src.note_gen.database import get_client, get_db, close_mongo_connection

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_connection():
    client = await get_client()
    if client is None:
        logging.error('Failed to initialize MongoDB client.')
        return
    async with get_db() as db:
        collections = await db.list_collection_names()
        print('Connected to database. Collections:', collections)

        for collection_name in collections:
            collection = db[collection_name]
            documents = await collection.find().to_list(length=10)  # Fetch up to 10 documents
            print(f'Contents of {collection_name}:', documents)

    logging.info(f'State of client before closing: {client}')
    await close_mongo_connection()  # Use the proper cleanup function

if __name__ == "__main__":
    asyncio.run(test_connection())