"""
src/note_gen/database/__init__.py

Database module initialization and exports.
"""

from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from .db import (
    get_db_conn,
    init_db,
    close_mongo_connection,
    MONGODB_URI,
    DATABASE_NAME,
)

async def get_chord_progression_by_name(db: AsyncIOMotorDatabase, name: str) -> Optional[Dict[str, Any]]:
    """Get a chord progression by name."""
    return await db.chord_progressions.find_one({"name": name})

async def get_note_pattern_by_name(db: AsyncIOMotorDatabase, name: str) -> Optional[Dict[str, Any]]:
    """Get a note pattern by name."""
    return await db.note_patterns.find_one({"name": name})

async def get_rhythm_pattern_by_name(db: AsyncIOMotorDatabase, name: str) -> Optional[Dict[str, Any]]:
    """Get a rhythm pattern by name."""
    return await db.rhythm_patterns.find_one({"name": name})

__all__ = [
    'get_db_conn',
    'init_db',
    'close_mongo_connection',
    'MONGODB_URI',
    'DATABASE_NAME',
    'get_chord_progression_by_name',
    'get_note_pattern_by_name',
    'get_rhythm_pattern_by_name',
]
