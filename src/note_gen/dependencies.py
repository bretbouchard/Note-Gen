"""FastAPI dependencies."""
from typing import AsyncGenerator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

# Use consistent import style
from note_gen.database.db import get_db_conn, close_mongo_connection
from src.note_gen.controllers.chord_progression_controller import ChordProgressionController
from src.note_gen.database.repositories.base_repository import BaseRepository

async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection dependency."""
    async for db in get_db_conn():
        yield db

async def get_chord_progression_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get chord progression repository dependency."""
    # This would typically use a specific repository implementation
    # For now, we'll use a placeholder
    from src.note_gen.database.repositories.base_repository import BaseRepository
    from src.note_gen.models.chord_progression import ChordProgression

    return BaseRepository[ChordProgression](db.chord_progressions)

async def get_chord_progression_controller(
    repository: BaseRepository = Depends(get_chord_progression_repository)
) -> ChordProgressionController:
    """Get chord progression controller dependency."""
    return ChordProgressionController(repository)
