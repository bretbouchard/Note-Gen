import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['note_gen']
    collections = await db.list_collection_names()
    print('Connected to database:', db.name)
    print('Collections:', collections)
    chord_progressions = await db.chord_progressions.find().to_list(length=None)
    print('Chord Progressions:', chord_progressions)
    client.close()  # This line should not be awaited

if __name__ == '__main__':
    asyncio.run(main())
