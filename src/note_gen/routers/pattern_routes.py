"""Router for pattern-related endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Annotated
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from src.note_gen.core.enums import ScaleType, ValidationLevel
from src.note_gen.models.patterns import NotePattern, RhythmPattern
from src.note_gen.services.pattern_service import PatternService
from src.note_gen.validation.base_validation import ValidationResult
from src.note_gen.core.database import get_db_conn
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["patterns"])
pattern_service = PatternService()

DbDep = Annotated[AsyncIOMotorDatabase, Depends(get_db_conn)]

class PatternRequest(BaseModel):
    root_note: str
    scale_type: ScaleType
    pattern_config: Dict[str, Any]

# Pattern Generation Endpoints
@router.post("/generate/note", response_model=Dict[str, Any])
async def generate_pattern(request: PatternRequest) -> dict:
    """Generate a new note pattern."""
    try:
        pattern = await pattern_service.generate_musical_pattern(
            root_note=request.root_note,
            scale_type=request.scale_type,
            pattern_config=request.pattern_config
        )
        return {"status": "success", "data": pattern.model_dump()}
    except Exception as e:
        logger.error(f"Error generating pattern: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=ValidationResult)
async def validate_pattern(
    pattern_data: dict,
    validation_level: ValidationLevel = ValidationLevel.NORMAL
) -> ValidationResult:
    """Validate a pattern."""
    try:
        return NotePattern.validate_pattern_data(pattern_data, validation_level)
    except Exception as e:
        logger.error(f"Error validating pattern: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Database CRUD Operations
@router.post("/note-patterns", response_model=NotePattern)
async def create_note_pattern(
    pattern: NotePattern,
    db: DbDep
) -> NotePattern:
    """Create a new note pattern."""
    try:
        pattern_dict = pattern.model_dump()
        result = await db.note_patterns.insert_one(pattern_dict)
        created_pattern = await db.note_patterns.find_one({"_id": result.inserted_id})
        return NotePattern.model_validate(created_pattern)
    except Exception as e:
        logger.error(f"Error creating note pattern: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create note pattern: {str(e)}"
        )

@router.post("/rhythm-patterns", response_model=RhythmPattern)
async def create_rhythm_pattern(
    pattern: RhythmPattern,
    db: DbDep
) -> RhythmPattern:
    """Create a new rhythm pattern."""
    try:
        pattern_dict = pattern.model_dump()
        result = await db.rhythm_patterns.insert_one(pattern_dict)
        created_pattern = await db.rhythm_patterns.find_one({"_id": result.inserted_id})
        return RhythmPattern.model_validate(created_pattern)
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rhythm pattern: {str(e)}"
        )

@router.get("/note-patterns", response_model=List[NotePattern])
async def list_note_patterns(
    db: DbDep
) -> List[NotePattern]:
    """Get all note patterns."""
    patterns = await db.note_patterns.find().to_list(None)
    return [NotePattern(**pattern) for pattern in patterns]

@router.get("/rhythm-patterns", response_model=List[RhythmPattern])
async def list_rhythm_patterns(
    db: DbDep
) -> List[RhythmPattern]:
    """Get all rhythm patterns."""
    patterns = await db.rhythm_patterns.find().to_list(None)
    return [RhythmPattern(**pattern) for pattern in patterns]
