import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from src.note_gen.core.enums import ScaleType, ChordQuality

logger = logging.getLogger(__name__)

# Database connection details
MONGO_URI = 'mongodb://localhost:27017'
DB_NAME = 'test_note_gen'
COLLECTION_NAME = 'chord_progressions'

async def update_scale_types():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Update scale types to enum values
    for scale_type in ScaleType:
        await collection.update_many(
            {'scale_type': scale_type.value.lower()},
            {'$set': {'scale_type': scale_type.value}}
        )

    # Update chord qualities to enum values
    for quality in ChordQuality:
        await collection.update_many(
            {'chords.quality': quality.value.lower()},
            {'$set': {'chords.$[].quality': quality.value}}
        )

    print('Update complete.')

if __name__ == '__main__':
    asyncio.run(update_scale_types())
