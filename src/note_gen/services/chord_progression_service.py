"""Service layer for chord progression operations."""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.database.db import get_database
from src.note_gen.models.chord_progression import ChordProgression

class ChordProgressionService:
    """Service for handling chord progression operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.chord_progressions

    @classmethod
    async def create(cls) -> 'ChordProgressionService':
        """Factory method to create a new service instance."""
        db = await get_database()
        return cls(db)

    async def save_progression(self, progression: ChordProgression) -> str:
        """Save a chord progression to the database."""
        result = await self.collection.insert_one(progression.model_dump())
        return str(result.inserted_id)

    # Add other service methods as needed
