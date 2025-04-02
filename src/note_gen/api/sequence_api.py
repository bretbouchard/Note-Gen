from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..database.db import get_db_conn
from ..models.sequence import NoteSequence, NoteSequenceCreate
from typing import List, Dict, Any
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=NoteSequence, status_code=201)
async def create_sequence(
    sequence: NoteSequenceCreate,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> Dict[str, Any]:
    """Create a new note sequence."""
    sequence_dict = sequence.model_dump()
    result = await db.note_sequences.insert_one(sequence_dict)
    # Convert ObjectId to string and use the correct field name
    created_sequence = await db.note_sequences.find_one({"_id": result.inserted_id})
    if not created_sequence:
        raise HTTPException(status_code=404, detail="Failed to create sequence")

    # Convert ObjectId to string and add id field for the response
    id_str = str(created_sequence["_id"])
    created_sequence["_id"] = id_str
    created_sequence["id"] = id_str  # Add id field for the test
    return dict(created_sequence)

@router.get("/", response_model=List[NoteSequence])
async def get_sequences(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[Dict[str, Any]]:
    """Get all note sequences."""
    sequences = await db.note_sequences.find().to_list(length=None)
    # Convert ObjectId to string for each sequence
    for seq in sequences:
        id_str = str(seq["_id"])
        seq["_id"] = id_str
        seq["id"] = id_str  # Add id field for the test
    return sequences

@router.get("/{sequence_id}", response_model=NoteSequence)
async def get_sequence(
    sequence_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> Dict[str, Any]:
    """Get a specific sequence by ID."""
    try:
        sequence = await db.note_sequences.find_one({"_id": ObjectId(sequence_id)})
        if not sequence:
            raise HTTPException(status_code=404, detail="Sequence not found")
        id_str = str(sequence["_id"])
        sequence["_id"] = id_str
        sequence["id"] = id_str  # Add id field for the test
        return dict(sequence)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
