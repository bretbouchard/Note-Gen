import asyncio
import logging
from src.note_gen.dependencies import get_db_conn
from src.note_gen.database.db import close_mongo_connection, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_connection():
    try:
        # Initialize database
        await init_db()
        logging.info("Database initialized")

        async with get_db_conn() as db:
            collections = await db.list_collection_names()
            print('Connected to database. Collections:', collections)

            for collection_name in collections:
                count = await db[collection_name].count_documents({})
                print(f'Collection {collection_name} has {count} documents')

    except Exception as e:
        logging.error(f'Error connecting to database: {e}')
        raise
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_connection())