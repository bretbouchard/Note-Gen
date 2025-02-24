import asyncio
import os
import sys

# Add the src directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from import_presets import import_presets_if_empty
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    # MongoDB connection setup
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'note_gen')
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    await import_presets_if_empty(db)

if __name__ == '__main__':
    asyncio.run(main())
