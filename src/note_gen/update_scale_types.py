import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from src.note_gen.core.constants import (
    DEFAULT_MONGODB_URI,
    DEFAULT_DB_NAME,
    COLLECTION_NAMES
)
from src.note_gen.core.enums import ScaleType

logger = logging.getLogger(__name__)

async def update_scale_types():
    """Update scale types to use ScaleType enum values."""
    client = AsyncIOMotorClient(DEFAULT_MONGODB_URI)
    db = client[DEFAULT_DB_NAME]
    collection = db[COLLECTION_NAMES['chord_progressions']]
    
    try:
        # Update both scale_type and scale_info.scale_type fields
        result = await collection.update_many(
            {"$or": [
                {"scale_type": ScaleType.MAJOR.value},
                {"scale_info.scale_type": ScaleType.MAJOR.value}
            ]},
            {"$set": {
                "scale_type": ScaleType.MAJOR.value,
                "scale_info.scale_type": ScaleType.MAJOR.value
            }}
        )
        logger.debug(f"Updated {result.modified_count} documents")
        
        # Verify the update
        updated_docs = await collection.find({}).to_list(None)
        logger.debug(f"Updated documents: {updated_docs}")
        
    except Exception as e:
        logger.error(f"Error updating scale types: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_scale_types())
