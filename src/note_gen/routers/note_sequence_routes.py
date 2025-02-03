# src/note_gen/routers/note_sequence_routes.py

from fastapi import APIRouter, HTTPException, Depends
from motor import motor_asyncio
from typing import List
from src.note_gen.dependencies import get_db
from src.note_gen.models.note_sequence import NoteSequence
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Get all note sequences
@router.get("/note-sequences", response_model=List[NoteSequence])
async def get_note_sequences(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Fetching all note sequences")
    try:
        note_sequences = await db.note_sequences.find().to_list(length=None)
        logger.debug(f"Fetched {len(note_sequences)} note sequences from the database")
        return note_sequences
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching note sequences: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching note sequences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get a single note sequence by ID
@router.get("/note-sequences/{sequence_id}", response_model=NoteSequence)
async def get_note_sequence(sequence_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Fetching note sequence with ID: {sequence_id}")
    try:
        note_sequence = await db.note_sequences.find_one({"_id": ObjectId(sequence_id)})
        if note_sequence is None:
            logger.warning(f"Note sequence not found for ID: {sequence_id}")
            raise HTTPException(status_code=404, detail="Note sequence not found")
        return note_sequence
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching note sequence with ID {sequence_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching note sequence with ID {sequence_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
