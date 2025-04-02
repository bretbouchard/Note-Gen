"""FastAPI dependencies."""
from typing import AsyncGenerator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

# Use consistent import style
from note_gen.database.db import get_db_conn, close_mongo_connection
from src.note_gen.controllers.chord_progression_controller import ChordProgressionController
from src.note_gen.controllers.pattern_controller import PatternController
from src.note_gen.controllers.sequence_controller import SequenceController
from src.note_gen.controllers.user_controller import UserController
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

async def get_note_pattern_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get note pattern repository dependency."""
    from src.note_gen.models.patterns import NotePattern

    return BaseRepository[NotePattern](db.note_patterns)

async def get_rhythm_pattern_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get rhythm pattern repository dependency."""
    from src.note_gen.models.patterns import RhythmPattern

    return BaseRepository[RhythmPattern](db.rhythm_patterns)

async def get_pattern_controller(
    note_pattern_repository: BaseRepository = Depends(get_note_pattern_repository),
    rhythm_pattern_repository: BaseRepository = Depends(get_rhythm_pattern_repository)
) -> PatternController:
    """Get pattern controller dependency."""
    return PatternController(note_pattern_repository, rhythm_pattern_repository)

async def get_sequence_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get sequence repository dependency."""
    from src.note_gen.models.sequence import Sequence

    return BaseRepository[Sequence](db.sequences)

async def get_sequence_controller(
    sequence_repository: BaseRepository = Depends(get_sequence_repository),
    pattern_controller: PatternController = Depends(get_pattern_controller),
    chord_progression_repository: BaseRepository = Depends(get_chord_progression_repository)
) -> SequenceController:
    """Get sequence controller dependency."""
    return SequenceController(sequence_repository, pattern_controller, chord_progression_repository)

async def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get user repository dependency."""
    from src.note_gen.models.user import User

    return BaseRepository[User](db.users)

async def get_user_controller(
    user_repository: BaseRepository = Depends(get_user_repository)
) -> UserController:
    """Get user controller dependency."""
    return UserController(user_repository)
