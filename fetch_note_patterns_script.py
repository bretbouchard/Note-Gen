import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from src.note_gen.fetch_patterns import _fetch_note_patterns

async def main():
    client = AsyncIOMotorClient()
    db = client.note_gen
    patterns = await _fetch_note_patterns(db)
    print(patterns)

if __name__ == '__main__':
    asyncio.run(main())
