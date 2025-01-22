from motor.motor_asyncio import AsyncIOMotorClient

# Connect to MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["note_gen"]

# Cleanup function for note_patterns
async def cleanup_note_patterns() -> None:
    result = await db.note_patterns.delete_many({"id": {"$exists": False}})
    print(f"Removed {result.deleted_count} note patterns without an ID.")

# Cleanup function for rhythm_patterns
async def cleanup_rhythm_patterns() -> None:
    result = await db.rhythm_patterns.delete_many({"id": {"$exists": False}})
    print(f"Removed {result.deleted_count} rhythm patterns without an ID.")

# Run the cleanup functions
async def run_cleanup():
    await cleanup_note_patterns()
    await cleanup_rhythm_patterns()

import asyncio
asyncio.run(run_cleanup())

# Close the connection
client.close()
