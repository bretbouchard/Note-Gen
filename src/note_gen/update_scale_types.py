import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def update_scale_types():
    """Update scale types to use ScaleType enum values."""
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.test_note_gen
    try:
        # Update both scale_type and scale_info.scale_type fields
        result = await db.chord_progressions.update_many(
            {"$or": [
                {"scale_type": "MAJOR"},
                {"scale_info.scale_type": "MAJOR"}
            ]},
            {"$set": {
                "scale_type": "MAJOR",
                "scale_info.scale_type": "MAJOR"
            }}
        )
        logger.debug(f"Updated {result.modified_count} documents")
        
        # Verify the update
        updated_docs = await db.chord_progressions.find({}).to_list(None)
        logger.debug(f"Updated documents: {updated_docs}")
        
    except Exception as e:
        logger.error(f"Error updating scale types: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_scale_types())