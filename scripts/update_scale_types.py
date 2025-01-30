import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Database connection details
MONGO_URI = 'mongodb://localhost:27017'
DB_NAME = 'test_note_gen'
COLLECTION_NAME = 'chord_progressions'

async def update_scale_types():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Update scale types to uppercase
    await collection.update_many(
        {'scale_type': 'major'},
        {'$set': {'scale_type': 'MAJOR'}}
    )
    await collection.update_many(
        {'scale_type': 'MINOR'},
        {'$set': {'scale_type': 'MINOR'}}
    )

    # Update chord qualities to uppercase without array filters
    await collection.update_many(
        {'chords.quality': 'major'},
        {'$set': {'chords.$[].quality': 'MAJOR'}}
    )
    await collection.update_many(
        {'chords.quality': 'MINOR'},
        {'$set': {'chords.$[].quality': 'MINOR'}}
    )

    print('Update complete.')

if __name__ == '__main__':
    asyncio.run(update_scale_types())
