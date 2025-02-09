"""
Routes for rhythm pattern operations.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from bson import ObjectId
from src.note_gen.models.rhythm_pattern import RhythmPattern
from src.note_gen.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(
    prefix="",  
    tags=["rhythm-patterns"]
)

@router.post("/api/v1/rhythm-patterns", response_model=RhythmPattern, status_code=status.HTTP_201_CREATED)
async def create_rhythm_pattern(
    pattern: RhythmPattern,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> RhythmPattern:
    """Create a new rhythm pattern."""
    try:
        # Check if pattern with same name exists
        existing_pattern = await db.rhythm_patterns.find_one({"name": pattern.name})
        if existing_pattern:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Rhythm pattern with name '{pattern.name}' already exists"
            )

        # Convert to dict for MongoDB storage
        pattern_dict = pattern.model_dump(by_alias=True)
        
        # Store in database
        result = await db.rhythm_patterns.insert_one(pattern_dict)
        
        # Add the generated ID to the pattern
        pattern_dict["id"] = str(result.inserted_id)
        return RhythmPattern(**pattern_dict)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/api/v1/rhythm-patterns", response_model=List[RhythmPattern])
async def get_rhythm_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[RhythmPattern]:
    """Get all rhythm patterns."""
    try:
        cursor = db.rhythm_patterns.find()
        patterns = await cursor.to_list(length=None)
        return [RhythmPattern(**pattern) for pattern in patterns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/rhythm-patterns/{pattern_id}", response_model=RhythmPattern)
async def get_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> RhythmPattern:
    """Get a specific rhythm pattern by ID."""
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(pattern_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid rhythm pattern ID format"
            )
            
        pattern = await db.rhythm_patterns.find_one({"_id": ObjectId(pattern_id)})
        if not pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rhythm pattern not found"
            )
        return RhythmPattern(**pattern)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/api/v1/rhythm-patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a rhythm pattern by ID."""
    try:
        result = await db.rhythm_patterns.delete_one({"_id": ObjectId(pattern_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rhythm pattern not found"
            )
    except Exception as e:
        if "Invalid ObjectId" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rhythm pattern not found"
            )
        raise HTTPException(status_code=500, detail=str(e))
