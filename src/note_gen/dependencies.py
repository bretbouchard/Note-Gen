"""FastAPI dependencies."""

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

# Use consistent import style
from note_gen.database.db import get_db_conn
from note_gen.controllers.chord_progression_controller import ChordProgressionController
from note_gen.controllers.pattern_controller import PatternController
from note_gen.controllers.sequence_controller import SequenceController
from note_gen.controllers.user_controller import UserController
from note_gen.database.repositories.base import BaseRepository

async def get_database() -> AsyncIOMotorDatabase:
    """Get database connection dependency."""
    return await get_db_conn()

async def get_chord_progression_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get chord progression repository dependency."""
    from note_gen.database.repositories.chord_progression_repository import ChordProgressionRepository

    return ChordProgressionRepository(db.chord_progressions)

async def get_chord_progression_controller(
    repository: BaseRepository = Depends(get_chord_progression_repository)
) -> ChordProgressionController:
    """Get chord progression controller dependency."""
    return ChordProgressionController(repository)

async def get_note_pattern_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get note pattern repository dependency."""
    from note_gen.database.repositories.note_pattern_repository import NotePatternRepository

    return NotePatternRepository(db.note_patterns)

async def get_rhythm_pattern_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get rhythm pattern repository dependency."""
    from note_gen.database.repositories.rhythm_pattern_repository import RhythmPatternRepository

    return RhythmPatternRepository(db.rhythm_patterns)

async def get_pattern_controller(
    note_pattern_repository: BaseRepository = Depends(get_note_pattern_repository),
    rhythm_pattern_repository: BaseRepository = Depends(get_rhythm_pattern_repository)
) -> PatternController:
    """Get pattern controller dependency."""
    return PatternController(note_pattern_repository, rhythm_pattern_repository)

async def get_sequence_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get sequence repository dependency."""
    from note_gen.database.repositories.sequence_repository import SequenceRepository

    return SequenceRepository(db.sequences)

async def get_sequence_controller(
    sequence_repository: BaseRepository = Depends(get_sequence_repository),
    pattern_controller: PatternController = Depends(get_pattern_controller),
    chord_progression_repository: BaseRepository = Depends(get_chord_progression_repository)
) -> SequenceController:
    """Get sequence controller dependency."""
    return SequenceController(sequence_repository, pattern_controller, chord_progression_repository)

async def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    """Get user repository dependency."""
    from note_gen.database.repositories.user_repository import UserRepository

    return UserRepository(db.users)

async def get_user_controller(
    user_repository: BaseRepository = Depends(get_user_repository)
) -> UserController:
    """Get user controller dependency."""
    return UserController(user_repository)
