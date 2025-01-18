# file: src/note_gen/routers/user_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId
from unittest.mock import AsyncMock
import pytest

from src.note_gen.database import get_db
from src.note_gen.models.rhythm_pattern import RhythmPattern
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.note_sequence_generator import generate_sequence_from_presets
from src.note_gen.models.scale_info import ScaleInfo

router = APIRouter()

# ---------------------------------------------------------------------
# RHYTHM PATTERNS
# ---------------------------------------------------------------------

@router.get("/rhythm-patterns", response_model=List[RhythmPattern])
async def get_rhythm_patterns(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[RhythmPattern]:
    """
    GET all rhythm patterns.
    """
    results = []
    async for doc in db.rhythm_patterns.find():
        # Convert to Pydantic model
        results.append(RhythmPattern(**doc))
    return results

@router.get("/rhythm-patterns/{pattern_id}", response_model=RhythmPattern)
async def get_rhythm_pattern_by_id(pattern_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> RhythmPattern:
    """
    GET a single rhythm pattern by its ObjectId.
    Returns 422 if the ID format is invalid, 404 if not found.
    """
    # Validate ObjectId
    try:
        oid = ObjectId(pattern_id)
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ID format")
    
    doc = await db.rhythm_patterns.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rhythm pattern not found")
    
    return RhythmPattern(**doc)

@router.post("/rhythm-patterns", response_model=RhythmPattern, status_code=status.HTTP_201_CREATED)
async def create_rhythm_pattern(pattern: RhythmPattern, db: AsyncIOMotorDatabase = Depends(get_db)) -> RhythmPattern:
    """
    POST a new RhythmPattern.
    - Returns 409 if a pattern with the same name already exists.
    - Otherwise, inserts and returns the newly created pattern.
    """
    # Check for duplicates
    existing = await db.rhythm_patterns.find_one({"name": pattern.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rhythm pattern with name '{pattern.name}' already exists"
        )
    
    # Insert
    doc = pattern.model_dump(exclude={"id"})
    result = await db.rhythm_patterns.insert_one(doc)
    new_id = result.inserted_id
    doc["_id"] = new_id
    return RhythmPattern(**doc)

@router.delete("/rhythm-patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rhythm_pattern(pattern_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> None:
    """
    DELETE a single rhythm pattern.
    - Returns 422 if the ID format is invalid, 404 if not found.
    - Returns 204 No Content on success.
    """
    try:
        oid = ObjectId(pattern_id)
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ID format")
    
    result = await db.rhythm_patterns.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rhythm pattern not found")


# ---------------------------------------------------------------------
# NOTE PATTERNS
# ---------------------------------------------------------------------

@router.get("/note-patterns", response_model=List[NotePattern])
async def get_note_patterns(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[NotePattern]:
    """
    GET all note patterns.
    """
    results = []
    async for doc in db.note_patterns.find():
        results.append(NotePattern(**doc))
    return results

@router.get("/note-patterns/{pattern_id}", response_model=NotePattern)
async def get_note_pattern_by_id(pattern_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> NotePattern:
    """
    GET a single note pattern by its ObjectId.
    Returns 422 if the ID is invalid, 404 if not found.
    """
    try:
        oid = ObjectId(pattern_id)
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ID format")
    
    doc = await db.note_patterns.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note pattern not found")
    return NotePattern(**doc)

@router.post("/note-patterns", response_model=NotePattern, status_code=status.HTTP_201_CREATED)
async def create_note_pattern(pattern: NotePattern, db: AsyncIOMotorDatabase = Depends(get_db)) -> NotePattern:
    """
    POST a new NotePattern.
    - Returns 409 if a pattern with the same name already exists.
    """
    existing = await db.note_patterns.find_one({"name": pattern.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Note pattern with name '{pattern.name}' already exists"
        )
    
    doc = pattern.model_dump(exclude={"id"})
    result = await db.note_patterns.insert_one(doc)
    doc["_id"] = result.inserted_id
    return NotePattern(**doc)

@router.delete("/note-patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_pattern(pattern_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> None:
    """
    DELETE a single note pattern.
    - Returns 422 if invalid, 404 if not found.
    """
    try:
        oid = ObjectId(pattern_id)
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ID format")

    result = await db.note_patterns.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note pattern not found")


# ---------------------------------------------------------------------
# CHORD PROGRESSIONS
# ---------------------------------------------------------------------

@router.get("/chord-progressions", response_model=List[ChordProgression])
async def get_chord_progressions(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[ChordProgression]:
    """
    GET all chord progressions.
    """
    results = []
    async for doc in db.chord_progressions.find():
        results.append(ChordProgression(**doc))
    return results

@router.get("/chord-progressions/{prog_id}", response_model=ChordProgression)
async def get_chord_progression(prog_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> ChordProgression:
    """
    GET a single chord progression by ID.
    Returns 422 if invalid, 404 if not found.
    """
    try:
        oid = ObjectId(prog_id)
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ID format")
    
    doc = await db.chord_progressions.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chord progression not found")
    return ChordProgression(**doc)

@router.post("/chord-progressions", response_model=ChordProgression, status_code=status.HTTP_201_CREATED)
async def create_chord_progression(
    progression: ChordProgression,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> ChordProgression:
    """
    POST a new chord progression.
    - Returns 409 if a progression with the same name already exists (if your tests require that).
    """
    existing = await db.chord_progressions.find_one({"name": progression.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Chord progression '{progression.name}' already exists."
        )
    
    doc = progression.model_dump(exclude={"id"})
    result = await db.chord_progressions.insert_one(doc)
    doc["_id"] = result.inserted_id
    return ChordProgression(**doc)

@router.delete("/chord-progressions/{prog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chord_progression(prog_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> None:
    """
    DELETE chord progression.
    """
    try:
        oid = ObjectId(prog_id)
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ID format")
    
    result = await db.chord_progressions.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chord progression not found")


# ---------------------------------------------------------------------
# NOTE SEQUENCES + GENERATE-SEQUENCE
# ---------------------------------------------------------------------

@router.get("/note-sequences", response_model=List[NoteSequence])
async def get_note_sequences(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[NoteSequence]:
    """
    GET /note-sequences
    (If your tests expect some data here, you might need a note_sequences collection.)
    """
    results = []
    async for doc in db.note_sequences.find():
        results.append(NoteSequence(**doc))
    return results

@router.post("/generate-sequence", response_model=NoteSequence, status_code=status.HTTP_200_OK)
async def generate_sequence_endpoint(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> NoteSequence:
    """
    POST /generate-sequence
    - This is a placeholder that matches test_generate_sequence.py usage.
    - Adjust the arguments according to your test payload structure
      (some tests pass a JSON with { "progression_name": "...", "note_pattern_name": "...", ...}).
    """
    # Validate or fetch chord progression
    progression_doc = await db.chord_progressions.find_one({"name": progression_name})
    if not progression_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chord progression not found")

    # Validate or fetch note pattern
    note_pattern_doc = await db.note_patterns.find_one({"name": note_pattern_name})
    if not note_pattern_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note pattern not found")

    # Validate or fetch rhythm pattern
    rhythm_pattern_doc = await db.rhythm_patterns.find_one({"name": rhythm_pattern_name})
    if not rhythm_pattern_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rhythm pattern not found")

    # Actually generate the sequence
    # For now, call your existing logic or a stub.
    sequence = generate_sequence_from_presets(
        progression_name=progression_name,
        note_pattern_name=note_pattern_name,
        rhythm_pattern_name=rhythm_pattern_name,
        scale_info=scale_info
    )
    # If you want to store in DB:
    doc = sequence.model_dump(exclude={"id"})
    result = await db.note_sequences.insert_one(doc)
    doc["_id"] = result.inserted_id
    return NoteSequence(**doc)

# Mock the database cursor to return sample data
mock_cursor = AsyncMock()
mock_cursor.__aiter__.return_value = iter([{ '_id': ObjectId(), 'name': 'Sample Note Pattern' }])

# Mock the database call to return the mock cursor
mock_db = AsyncMock()
mock_db.note_patterns.find.return_value = mock_cursor

# Use the mock database in the test
@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()