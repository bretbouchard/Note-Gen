import os
os.environ["TESTING"] = "1"

import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.api.pattern_api import (
    fetch_chord_progressions,
    fetch_chord_progression_by_id,
    fetch_rhythm_patterns,
    fetch_rhythm_pattern_by_id,
    fetch_note_patterns,
    fetch_note_pattern_by_id
)
from src.note_gen.database import get_database

@pytest.mark.asyncio
async def test_fetch_chord_progressions(test_db: AsyncIOMotorDatabase):
    """Test fetching all chord progressions."""
    progressions = await fetch_chord_progressions(test_db)
    assert isinstance(progressions, list)

@pytest.mark.asyncio
async def test_fetch_chord_progression_by_id(test_db: AsyncIOMotorDatabase):
    """Test fetching a specific chord progression."""
    progression = await fetch_chord_progression_by_id(test_db, "test_id")
    assert progression is None or isinstance(progression, dict)

@pytest.mark.asyncio
async def test_fetch_rhythm_patterns(test_db: AsyncIOMotorDatabase):
    """Test fetching all rhythm patterns."""
    patterns = await fetch_rhythm_patterns(test_db)
    assert isinstance(patterns, list)

@pytest.mark.asyncio
async def test_fetch_rhythm_pattern_by_id(test_db: AsyncIOMotorDatabase):
    """Test fetching a specific rhythm pattern."""
    pattern = await fetch_rhythm_pattern_by_id(test_db, "test_id")
    assert pattern is None or isinstance(pattern, dict)

@pytest.mark.asyncio
async def test_fetch_note_patterns(test_db: AsyncIOMotorDatabase):
    """Test fetching all note patterns."""
    patterns = await fetch_note_patterns(test_db)
    assert isinstance(patterns, list)

@pytest.mark.asyncio
async def test_fetch_note_pattern_by_id(test_db: AsyncIOMotorDatabase):
    """Test fetching a specific note pattern."""
    pattern = await fetch_note_pattern_by_id(test_db, "test_id")
    assert pattern is None or isinstance(pattern, dict)
