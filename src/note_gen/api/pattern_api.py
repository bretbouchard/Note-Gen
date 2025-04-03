"""Pattern API functions for fetching and managing patterns."""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.patterns import NotePattern
from note_gen.core.enums import ScaleType
from note_gen.validation.validation_manager import ValidationManager
from note_gen.database.db import get_db_conn

router = APIRouter()

class PatternCreate(BaseModel):
    name: str
    pattern: List[Dict]
    description: Optional[str] = None

async def check_rhythm_pattern(pattern: RhythmPattern) -> Dict[str, Any]:
    """
    Validate a rhythm pattern.

    Args:
        pattern: RhythmPattern to validate

    Returns:
        Dict containing validation results
    """
    validation_manager = ValidationManager()

    # Basic validation checks
    validation_results = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }

    # Check time signature
    if not pattern.time_signature or len(pattern.time_signature) != 2:
        validation_results["is_valid"] = False
        validation_results["errors"].append("Invalid time signature format")

    # Check pattern notes
    if not pattern.pattern:
        validation_results["is_valid"] = False
        validation_results["errors"].append("Pattern cannot be empty")

    # Check note positions and durations
    total_duration = 0
    last_position = -1

    for note in pattern.pattern:
        # Check position ordering
        if note.position <= last_position:
            validation_results["errors"].append(f"Invalid note position: {note.position}")
            validation_results["is_valid"] = False

        # Check duration validity
        if note.duration <= 0:
            validation_results["errors"].append(f"Invalid note duration: {note.duration}")
            validation_results["is_valid"] = False

        last_position = note.position
        total_duration = max(total_duration, note.position + note.duration)

    # Check if pattern fits within time signature
    measures = total_duration / (pattern.time_signature[0] / pattern.time_signature[1])
    if not measures.is_integer():
        validation_results["warnings"].append("Pattern duration does not align with time signature")

    return validation_results

async def fetch_chord_progressions(db: AsyncIOMotorDatabase):
    """Fetch all chord progressions."""
    return await db.chord_progressions.find().to_list(None)

async def fetch_chord_progression_by_id(db: AsyncIOMotorDatabase, progression_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a specific chord progression by ID."""
    return await db.chord_progressions.find_one({"_id": progression_id})

async def fetch_rhythm_patterns(db: AsyncIOMotorDatabase):
    """Fetch all rhythm patterns."""
    return await db.rhythm_patterns.find().to_list(None)

async def fetch_rhythm_pattern_by_id(db: AsyncIOMotorDatabase, pattern_id: str):
    """Fetch a specific rhythm pattern by ID."""
    return await db.rhythm_patterns.find_one({"_id": pattern_id})

async def fetch_note_patterns(db: AsyncIOMotorDatabase):
    """Fetch all note patterns."""
    return await db.note_patterns.find().to_list(None)

async def fetch_note_pattern_by_id(db: AsyncIOMotorDatabase, pattern_id: str):
    """Fetch a specific note pattern by ID."""
    return await db.note_patterns.find_one({"_id": pattern_id})

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pattern(pattern: PatternCreate, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Create a new pattern."""
    if not pattern.name or not pattern.pattern:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name and pattern are required fields"
        )

    pattern_dict = pattern.model_dump()
    result = await db.patterns.insert_one(pattern_dict)

    return {"id": str(result.inserted_id), "name": pattern.name}

@router.get("/{pattern_id}")
async def get_pattern_by_id(pattern_id: str, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Get a pattern by its ID."""
    try:
        from bson import ObjectId
        from bson.errors import InvalidId
        try:
            object_id = ObjectId(pattern_id)
        except InvalidId:
            raise HTTPException(status_code=404, detail="Invalid pattern ID format")

        pattern = await db.patterns.find_one({"_id": object_id})
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")
        # Convert ObjectId to string for the response
        pattern["_id"] = str(pattern["_id"])
        return {"data": pattern}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/")
async def get_patterns():
    """Get all patterns."""
    return {"data": []}

@router.get("/note")
async def get_note_patterns():
    """Get all note patterns."""
    return {"data": []}

@router.get("/rhythm")
async def get_rhythm_patterns():
    """Get all rhythm patterns."""
    return {"data": []}

@router.post("/generate/note")
async def generate_pattern(request_data: Dict):
    """Generate a note pattern."""
    try:
        # Validate input
        if not all(key in request_data for key in ["root_note", "scale_type", "pattern_config"]):
            raise HTTPException(status_code=422, detail="Missing required fields")

        # Process and return pattern
        return {
            "data": {
                "pattern": [],  # Add your pattern generation logic here
                "root_note": request_data["root_note"],
                "scale_type": request_data["scale_type"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_pattern(pattern_data: Dict, validation_level: str = "NORMAL"):
    """Validate a pattern."""
    try:
        # Add your validation logic here
        return {
            "is_valid": True,
            "validation_level": validation_level,
            "errors": [],
            "warnings": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rhythm", status_code=201)
async def create_rhythm_pattern(pattern: RhythmPattern):
    try:
        # Add your pattern creation logic here
        return {"status": "success", "pattern": pattern}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/check/rhythm")
async def check_rhythm_pattern(pattern: RhythmPattern):
    """Check if a rhythm pattern is valid."""
    try:
        validation_results = await check_rhythm_pattern(pattern)
        return validation_results
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/check/note")
async def check_note_pattern(pattern_data: Dict):
    """Check if a note pattern is valid."""
    try:
        # Add validation logic here
        return {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
