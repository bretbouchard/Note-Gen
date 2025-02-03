from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.note_gen_db
    chord_progressions = await db.chord_progressions.find().to_list(None)
    note_patterns = await db.note_patterns.find().to_list(None)
    rhythm_patterns = await db.rhythm_patterns.find().to_list(None)
    print('Chord Progressions:', chord_progressions)
    print('Note Patterns:', note_patterns)
    print('Rhythm Patterns:', rhythm_patterns)

if __name__ == '__main__':
    asyncio.run(main())
