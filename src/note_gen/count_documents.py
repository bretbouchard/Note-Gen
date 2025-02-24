import asyncio
from src.note_gen.database.db import get_db_conn

async def count_documents():
    db = await get_db_conn()
    chord_count = await db.chord_progressions.count_documents({})
    note_count = await db.note_patterns.count_documents({})
    rhythm_count = await db.rhythm_patterns.count_documents({})
    print(f"Chord Progressions: {chord_count}, Note Patterns: {note_count}, Rhythm Patterns: {rhythm_count}")

if __name__ == '__main__':
    asyncio.run(count_documents())
