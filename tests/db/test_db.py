import unittest
from unittest.mock import patch
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import logging
import os

# Configure logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def seed_test_db():
    client = AsyncIOMotorClient('localhost', 27017)
    db = client.test_note_gen

    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        await db.chord_progressions.delete_many({})
        await db.note_patterns.delete_many({})
        await db.rhythm_patterns.delete_many({})

    try:
        # Seed chord progressions
        chord_progressions = [
            {
                'name': 'Sample Progression 1',
                'chords': [
                    {'root': {'note_name': 'C', 'octave': 4}, 'quality': 'MAJOR'},
                    {'root': {'note_name': 'G', 'octave': 4}, 'quality': 'MAJOR'}
                ],
                'key': 'C',
                'scale_type': 'MAJOR'
            },
            {
                'name': 'Sample Progression 2',
                'chords': [
                    {'root': {'note_name': 'D', 'octave': 4}, 'quality': 'MINOR'},
                    {'root': {'note_name': 'A', 'octave': 4}, 'quality': 'MAJOR'}
                ],
                'key': 'D',
                'scale_type': 'MINOR'
            }
        ]
        result = await db.chord_progressions.insert_many(chord_progressions)
        # logger.debug(f'Successfully inserted {len(result.inserted_ids)} chord progressions.')
    except Exception as e:
        logger.error(f'Error inserting chord progressions: {e}')

    try:
        # Seed rhythm patterns
        result = await db.rhythm_patterns.insert_many([
            {
                'name': 'Basic Rhythm',
                'data': {'notes': [{'duration': 1.0, 'velocity': 100}], 'time_signature': '4/4'}
            }
        ])
        # logger.debug(f'Successfully inserted {len(result.inserted_ids)} rhythm patterns.')
    except Exception as e:
        logger.error(f'Error inserting rhythm patterns: {e}')

    client.close()

if __name__ == '__main__':
    asyncio.run(seed_test_db())
