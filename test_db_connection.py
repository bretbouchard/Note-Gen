import asyncio
import logging
from src.note_gen.dependencies import get_db
from src.note_gen.database import close_mongo_connection, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_connection():
    # Initialize database
    db = await init_db()
    if db is None:
        logging.error('Failed to initialize MongoDB connection.')
        return

    logging.info("Database instance obtained")

    collections = await db.list_collection_names()
    print('Connected to database. Collections:', collections)

    for collection_name in collections:
        collection = db[collection_name]
        documents = await collection.find().to_list(length=10)  # Fetch up to 10 documents
        print(f'Contents of {collection_name}:', documents)

    await close_mongo_connection()  # Use the proper cleanup function
    logging.info("MongoDB connection closed")

if __name__ == "__main__":
    asyncio.run(test_connection())