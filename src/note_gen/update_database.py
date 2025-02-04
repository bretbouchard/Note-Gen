from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

async def update_note_patterns(db: AsyncIOMotorDatabase):
    async for note_pattern in db.note_patterns.find():
        # Prepare the update data
        update_data = {
            'pattern_type': 'default_type',  # Set a default or derived value
            'complexity': 1.0,                # Set a default value
            # Include other fields as necessary
        }
        # Update the record in the database
        await db.note_patterns.update_one(
            {'_id': note_pattern['_id']},
            {'$set': update_data}
        )

async def update_rhythm_patterns(db: AsyncIOMotorDatabase):
    async for rhythm_pattern in db.rhythm_patterns.find():
        # Prepare the update data
        update_data = {
            'complexity': 1.0,                # Set a default value
            # Include other fields as necessary
        }
        # Update the record in the database
        await db.rhythm_patterns.update_one(
            {'_id': rhythm_pattern['_id']},
            {'$set': update_data}
        )

async def update_database(db: AsyncIOMotorDatabase):
    await update_note_patterns(db)
    await update_rhythm_patterns(db)
