from typing import Any, List, Dict
import pytest
from typeguard import TypeCheckError, typechecked
from src.note_gen.database.db import get_db_conn
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.core.enums import ChordQuality
from motor.motor_asyncio import AsyncIOMotorDatabase

@pytest.mark.asyncio
@typechecked
async def test_db_connection_types() -> None:
    """Test type safety of database connection objects."""
    db = await get_db_conn()
    assert isinstance(db, AsyncIOMotorDatabase)
    
    with pytest.raises(TypeCheckError):
        wrong_type: str = db  # type: ignore

@typechecked
def test_model_types() -> None:
    """Test type safety of music models."""
    # Test Note type safety
    note = Note(note_name="C", octave=4)
    assert isinstance(note.note_name, str)
    assert isinstance(note.octave, int)
    
    with pytest.raises(TypeCheckError):
        wrong_note: Dict[str, str] = note  # type: ignore
    
    # Test Chord type safety
    chord = Chord.from_symbol("C")
    assert isinstance(chord.notes, list)
    assert all(isinstance(n, Note) for n in chord.notes)
