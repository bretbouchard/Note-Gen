"""
Consolidated routes for rhythm pattern operations with improved error handling and logging.
"""
import sys
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
import logging
import uuid
import traceback
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.note_gen.dependencies import get_db_conn
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternResponse
from fastapi.encoders import jsonable_encoder

# Configure logging
logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/rhythm-patterns",
    tags=["rhythm-patterns"]
)

@router.get("")
@router.get("/")
async def get_rhythm_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[RhythmPatternResponse]:
    """Get all rhythm patterns."""
    try:
        cursor = db.rhythm_patterns.find({})
        patterns = await cursor.to_list(length=None)
        return [RhythmPatternResponse(**pattern) for pattern in patterns]
    except Exception as e:
        logger.error(f"Error retrieving rhythm patterns: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{pattern_id}")
@router.get("/{pattern_id}/")
async def get_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """Get a specific rhythm pattern by ID."""
    try:
        pattern = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if pattern:
            return RhythmPatternResponse(**pattern)
        raise HTTPException(status_code=404, detail=f"Rhythm pattern {pattern_id} not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid pattern ID format")
    except Exception as e:
        logger.error(f"Error retrieving rhythm pattern {pattern_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("")
@router.post("/")
async def create_rhythm_pattern(
    rhythm_pattern: RhythmPattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """Create a new rhythm pattern."""
    try:
        # Generate a new ID
        rhythm_pattern.id = str(uuid.uuid4())
        
        # Convert to dict for MongoDB
        pattern_data = jsonable_encoder(rhythm_pattern)
        
        # Insert into database
        result = await db.rhythm_patterns.insert_one(pattern_data)
        
        # Return the created pattern
        created_pattern = await db.rhythm_patterns.find_one({"_id": result.inserted_id})
        return RhythmPatternResponse(**created_pattern)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail=f"Rhythm pattern with name '{rhythm_pattern.name}' already exists"
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{pattern_id}")
@router.put("/{pattern_id}/")
async def update_rhythm_pattern(
    pattern_id: str,
    rhythm_pattern: RhythmPattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """Update an existing rhythm pattern."""
    try:
        existing = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        
        update_data = jsonable_encoder(rhythm_pattern)
        update_data["_id"] = pattern_id
        
        result = await db.rhythm_patterns.replace_one(
            {"_id": pattern_id},
            update_data
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=304, detail="No changes made to rhythm pattern")
        
        updated = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if updated:
            return RhythmPatternResponse(**updated)
        raise HTTPException(status_code=404, detail="Updated pattern not found")
    except Exception as e:
        logger.error(f"Error updating rhythm pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{pattern_id}")
@router.delete("/{pattern_id}/")
async def delete_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> Response:
    """Delete a rhythm pattern."""
    try:
        result = await db.rhythm_patterns.delete_one({"_id": pattern_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting rhythm pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/simple/")
@router.get("/simple")
@router.get("/simple/")
async def get_rhythm_patterns_simple_route(db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Get all rhythm patterns."""
    cursor = db.rhythm_patterns.find({})
    rhythm_patterns = await cursor.to_list(length=100)
    pattern_responses = [
        RhythmPatternResponse(**{**pattern, "id": str(pattern["_id"])}) 
        for pattern in rhythm_patterns
    ]
    return pattern_responses

@router.get("/simple/{pattern_id}")
@router.get("/simple/{pattern_id}/")
async def get_rhythm_pattern_simple_route(pattern_id: str, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Get a specific rhythm pattern by ID."""
    pattern = await db.rhythm_patterns.find_one({"_id": pattern_id})
    if pattern is None:
        raise HTTPException(status_code=404, detail="Rhythm pattern not found")
    pattern_response = RhythmPatternResponse(**{**pattern, "id": str(pattern["_id"])})
    return pattern_response

@router.post("/simple/")
@router.post("/simple")
@router.post("/simple/")
async def create_rhythm_pattern_simple_route(rhythm_pattern: RhythmPattern, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Create a new rhythm pattern."""
    try:
        logger.info("Creating new rhythm pattern")
        logger.debug(f"Received rhythm pattern with ID: {rhythm_pattern.id}")
        
        # Check for duplicate name
        existing_pattern = await db.rhythm_patterns.find_one({"name": rhythm_pattern.name})
        if existing_pattern:
            logger.warning(f"Rhythm pattern with name '{rhythm_pattern.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Rhythm pattern with name '{rhythm_pattern.name}' already exists"
            )
        
        # Convert rhythm pattern to dict for MongoDB
        pattern_dict = rhythm_pattern.model_dump()
        
        # Always use the provided UUID as _id
        if not rhythm_pattern.id:
            pattern_dict["_id"] = str(uuid.uuid4())
        else:
            pattern_dict["_id"] = rhythm_pattern.id
        del pattern_dict["id"]
        logger.debug(f"Using ID as _id: {pattern_dict['_id']}")
        
        # Insert the pattern
        try:
            result = await db.rhythm_patterns.insert_one(pattern_dict)
            # Convert _id back to id for response
            pattern_dict["id"] = pattern_dict["_id"]
            del pattern_dict["_id"]
            logger.info(f"Successfully created rhythm pattern with ID: {pattern_dict['id']}")
            return RhythmPatternResponse(**pattern_dict)
            
        except Exception as e:
            logger.error(f"Database error while creating rhythm pattern: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
            
    except ValidationError as ve:
        logger.warning(f"Validation error while creating rhythm pattern: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating rhythm pattern: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.put("/simple/{pattern_id}")
@router.put("/simple/{pattern_id}/")
async def update_rhythm_pattern_simple_route(pattern_id: str, rhythm_pattern: RhythmPattern, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Update an existing rhythm pattern."""
    try:
        logger.info(f"Attempting to update rhythm pattern: {pattern_id}")
        
        # Validate pattern
        RhythmPattern.validate_pattern_with_time_signature(rhythm_pattern)
        
        # Prepare update data
        update_data = rhythm_pattern.model_dump(by_alias=True, exclude_unset=True)
        
        # Update the pattern
        result = await db.rhythm_patterns.update_one(
            {"_id": pattern_id}, 
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No rhythm pattern found to update with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Rhythm pattern with ID {pattern_id} not found"
            )
        
        # Fetch updated pattern
        updated_pattern = await db.rhythm_patterns.find_one({"_id": pattern_id})
        updated_pattern_response = RhythmPatternResponse(**{**updated_pattern, "id": str(updated_pattern["_id"])})
        
        logger.info(f"Successfully updated rhythm pattern: {pattern_id}")
        return updated_pattern_response
    
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Validation error during rhythm pattern update: {ve}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        logger.error(f"Rhythm Pattern Object: {rhythm_pattern}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error updating rhythm pattern {pattern_id}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during rhythm pattern update"
        )

@router.delete("/simple/{pattern_id}")
@router.delete("/simple/{pattern_id}/")
async def delete_rhythm_pattern_simple_route(pattern_id: str, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Delete a rhythm pattern."""
    try:
        logger.debug(f"Attempting to delete rhythm pattern with ID: {pattern_id}")
        
        # We're using UUIDs as _id, so just use the pattern_id directly
        delete_result = await db.rhythm_patterns.delete_one({"_id": pattern_id})
                
        if delete_result.deleted_count == 0:
            logger.warning(f"No pattern found with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rhythm pattern with ID {pattern_id} not found"
            )
        
        logger.info(f"Successfully deleted rhythm pattern with ID: {pattern_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        logger.error(f"Error deleting rhythm pattern: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during rhythm pattern deletion"
        )

async def create_rhythm_pattern(
    rhythm_pattern: RhythmPattern, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    try:
        logger.info("Creating new rhythm pattern")
        logger.debug(f"Received rhythm pattern with ID: {rhythm_pattern.id}")
        
        # Check for duplicate name
        existing_pattern = await db.rhythm_patterns.find_one({"name": rhythm_pattern.name})
        if existing_pattern:
            logger.warning(f"Rhythm pattern with name '{rhythm_pattern.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Rhythm pattern with name '{rhythm_pattern.name}' already exists"
            )
        
        # Convert rhythm pattern to dict for MongoDB
        pattern_dict = rhythm_pattern.model_dump()
        
        # Always use the provided UUID as _id
        if not rhythm_pattern.id:
            pattern_dict["_id"] = str(uuid.uuid4())
        else:
            pattern_dict["_id"] = rhythm_pattern.id
        del pattern_dict["id"]
        logger.debug(f"Using ID as _id: {pattern_dict['_id']}")
        
        # Insert the pattern
        try:
            await db.rhythm_patterns.insert_one(pattern_dict)
            # Convert _id back to id for response
            pattern_dict["id"] = pattern_dict["_id"]
            del pattern_dict["_id"]
            logger.info(f"Successfully created rhythm pattern with ID: {pattern_dict['id']}")
            return RhythmPatternResponse(**pattern_dict)
            
        except Exception as e:
            logger.error(f"Database error while creating rhythm pattern: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
            
    except ValidationError as ve:
        logger.warning(f"Validation error while creating rhythm pattern: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating rhythm pattern: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def get_rhythm_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[RhythmPatternResponse]:
    """
    Retrieve all rhythm patterns from the database.
    
    Args:
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        List[RhythmPatternResponse]: List of all rhythm patterns
    """
    try:
        logger.info("Fetching all rhythm patterns")
        
        # Fetch all rhythm patterns
        cursor = db.rhythm_patterns.find()
        rhythm_patterns = await cursor.to_list(length=None)
        
        # Convert to response models
        pattern_responses = [
            RhythmPatternResponse(**{**pattern, "id": str(pattern["_id"])}) 
            for pattern in rhythm_patterns
        ]
        
        logger.info(f"Retrieved {len(pattern_responses)} rhythm patterns")
        return pattern_responses
    
    except Exception as e:
        logger.error(f"Error retrieving rhythm patterns: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unable to retrieve rhythm patterns"
        )

async def get_rhythm_pattern(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """
    Retrieve a specific rhythm pattern by its ID.
    
    Args:
        pattern_id (str): The unique identifier of the rhythm pattern
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        RhythmPatternResponse: The requested rhythm pattern
    
    Raises:
        HTTPException: If the rhythm pattern is not found
    """
    try:
        logger.info(f"Fetching rhythm pattern with ID: {pattern_id}")
        
        # Find the pattern
        pattern = await db.rhythm_patterns.find_one({"_id": pattern_id})
        
        if not pattern:
            logger.warning(f"Rhythm pattern not found with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Rhythm pattern with ID {pattern_id} not found"
            )
        
        # Convert to response model
        pattern_response = RhythmPatternResponse(**{**pattern, "id": str(pattern["_id"])})
        
        logger.info(f"Successfully retrieved rhythm pattern: {pattern_id}")
        return pattern_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rhythm pattern {pattern_id}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error while fetching rhythm pattern"
        )

async def update_rhythm_pattern(
    pattern_id: str, 
    rhythm_pattern: RhythmPattern, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """
    Update an existing rhythm pattern.
    
    Args:
        pattern_id (str): The unique identifier of the rhythm pattern to update
        rhythm_pattern (RhythmPattern): Updated rhythm pattern data
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        RhythmPatternResponse: The updated rhythm pattern
    
    Raises:
        HTTPException: For various validation and database-related errors
    """
    try:
        logger.info(f"Attempting to update rhythm pattern: {pattern_id}")
        
        # Validate pattern
        RhythmPattern.validate_pattern_with_time_signature(rhythm_pattern)
        
        # Prepare update data
        update_data = rhythm_pattern.model_dump(by_alias=True, exclude_unset=True)
        
        # Update the pattern
        result = await db.rhythm_patterns.update_one(
            {"_id": pattern_id}, 
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No rhythm pattern found to update with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Rhythm pattern with ID {pattern_id} not found"
            )
        
        # Fetch updated pattern
        updated_pattern = await db.rhythm_patterns.find_one({"_id": pattern_id})
        updated_pattern_response = RhythmPatternResponse(**{**updated_pattern, "id": str(updated_pattern["_id"])})
        
        logger.info(f"Successfully updated rhythm pattern: {pattern_id}")
        return updated_pattern_response
    
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Validation error during rhythm pattern update: {ve}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        logger.error(f"Rhythm Pattern Object: {rhythm_pattern}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error updating rhythm pattern {pattern_id}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during rhythm pattern update"
        )

async def delete_rhythm_pattern(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> None:
    """
    Delete a rhythm pattern by its ID.
    
    Args:
        pattern_id (str): The unique identifier of the rhythm pattern to delete
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        None: Returns 204 No Content status on successful deletion
    
    Raises:
        HTTPException: If the rhythm pattern cannot be deleted
    """
    try:
        logger.debug(f"Attempting to delete rhythm pattern with ID: {pattern_id}")
        
        # We're using UUIDs as _id, so just use the pattern_id directly
        delete_result = await db.rhythm_patterns.delete_one({"_id": pattern_id})
                
        if delete_result.deleted_count == 0:
            logger.warning(f"No pattern found with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rhythm pattern with ID {pattern_id} not found"
            )
        
        logger.info(f"Successfully deleted rhythm pattern with ID: {pattern_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        logger.error(f"Error deleting rhythm pattern: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during rhythm pattern deletion"
        )

async def create_rhythm_pattern_simple(
    rhythm_pattern: RhythmPattern, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """
    Create a new rhythm pattern using the simple route.
    
    Args:
        rhythm_pattern (RhythmPattern): The rhythm pattern to create
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        RhythmPatternResponse: Created rhythm pattern with assigned ID
    """
    # Debug print to see the exact data being sent
    import json
    import bson
    import uuid
    
    try:
        # Log the full input object details
        logger.info("Full RhythmPattern Input:")
        logger.info(f"ID: {rhythm_pattern.id}")
        logger.info(f"Name: {rhythm_pattern.name}")
        logger.info(f"Description: {rhythm_pattern.description}")
        logger.info(f"Tags: {rhythm_pattern.tags}")
        logger.info(f"Complexity: {rhythm_pattern.complexity}")
        logger.info(f"Style: {rhythm_pattern.style}")
        
        # Log the data object details
        logger.info("RhythmPatternData Details:")
        logger.info(f"Time Signature: {rhythm_pattern.data.time_signature}")
        logger.info(f"Notes: {len(rhythm_pattern.data.notes)} notes")
        for i, note in enumerate(rhythm_pattern.data.notes):
            logger.info(f"Note {i}: position={note.position}, duration={note.duration}, velocity={note.velocity}, is_rest={note.is_rest}")
        
        # Validate pattern with time signature
        try:
            RhythmPattern.validate_pattern_with_time_signature(rhythm_pattern)
        except Exception as ve:
            logger.error(f"Time signature validation error: {ve}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid time signature: {str(ve)}"
            )
        
        # Generate a unique ID if not provided
        if not rhythm_pattern.id:
            rhythm_pattern.id = str(uuid.uuid4())
        
        # Prepare the document for insertion
        try:
            # Use a custom serialization method to handle BSON-friendly conversion
            rhythm_pattern_dict = rhythm_pattern.model_dump(by_alias=True)
            
            # Convert any nested objects to BSON-friendly format
            def convert_to_bson_friendly(obj):
                if isinstance(obj, dict):
                    return {k: convert_to_bson_friendly(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_bson_friendly(item) for item in obj]
                elif isinstance(obj, float):
                    # Convert float to a BSON-friendly representation
                    return float(obj)
                return obj
            
            rhythm_pattern_dict = convert_to_bson_friendly(rhythm_pattern_dict)
            
            # Rename '_id' to 'id' if it exists
            if 'id' in rhythm_pattern_dict:
                rhythm_pattern_dict['_id'] = rhythm_pattern_dict.pop('id')
            
            logger.info(f"Converted rhythm pattern dict: {json.dumps(rhythm_pattern_dict, indent=2)}")
        except Exception as de:
            logger.error(f"Model dump error: {de}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error(f"Rhythm Pattern Object: {rhythm_pattern}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid rhythm pattern data: {str(de)}"
            )
        
        # Check for existing rhythm pattern with the same name
        existing_pattern = await db.rhythm_patterns.find_one({"name": rhythm_pattern.name})
        if existing_pattern:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Rhythm pattern with name '{rhythm_pattern.name}' already exists"
            )
        
        # Insert the rhythm pattern into the database
        try:
            result = await db.rhythm_patterns.insert_one(rhythm_pattern_dict)
            logger.info(f"Insertion result: {result}")
            logger.info(f"Inserted ID: {result.inserted_id}")
        except pymongo.errors.PyMongoError as e:
            logger.error(f"Database insertion error: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error(f"Rhythm Pattern Dict: {rhythm_pattern_dict}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to insert rhythm pattern: {str(e)}"
            )
        
        # Verify the insertion
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create rhythm pattern"
            )
        
        # Retrieve the inserted document to return
        try:
            # Use find_one with the correct _id field
            inserted_pattern = await db.rhythm_patterns.find_one({"_id": result.inserted_id})
            logger.info(f"Inserted pattern: {inserted_pattern}")
        except pymongo.errors.PyMongoError as e:
            logger.error(f"Find inserted pattern error: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not retrieve inserted pattern: {str(e)}"
            )
        
        if not inserted_pattern:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Created rhythm pattern could not be retrieved"
            )
        
        # Convert to RhythmPatternResponse
        try:
            # Rename _id to id for response
            inserted_pattern['id'] = str(inserted_pattern.pop('_id'))
            response = RhythmPatternResponse(**inserted_pattern)
            logger.info(f"Response object: {response}")
            return response
        except Exception as re:
            logger.error(f"Response creation error: {re}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error(f"Inserted Pattern: {inserted_pattern}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not create response: {str(re)}"
            )
    
    except ValidationError as ve:
        logger.error(f"Validation error creating rhythm pattern: {ve}")
        # Log the full validation error details
        for error in ve.errors():
            logger.error(f"Validation Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except HTTPException as he:
        # Re-raise HTTPException to preserve status code and details
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating rhythm pattern: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def get_rhythm_patterns_simple(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[RhythmPatternResponse]:
    """
    Retrieve all rhythm patterns from the database using the simple route.
    
    Args:
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        List[RhythmPatternResponse]: List of all rhythm patterns
    """
    try:
        logger.info("Retrieving all rhythm patterns via simple route")
        
        # Fetch all rhythm patterns from the database
        cursor = db.rhythm_patterns.find()
        rhythm_patterns = await cursor.to_list(length=None)
        
        # Convert to RhythmPatternResponse
        response = [RhythmPatternResponse(**pattern) for pattern in rhythm_patterns]
        
        logger.info(f"Retrieved {len(response)} rhythm patterns")
        return response
    
    except Exception as e:
        logger.error(f"Error retrieving rhythm patterns: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def get_rhythm_pattern_simple(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """
    Retrieve a specific rhythm pattern by its ID.
    
    Args:
        pattern_id (str): The unique identifier of the rhythm pattern
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        RhythmPatternResponse: The requested rhythm pattern
    
    Raises:
        HTTPException: If the rhythm pattern is not found or an error occurs
    """
    try:
        logger.info(f"Fetching rhythm pattern with ID: {pattern_id}")
        
        # Find the pattern - try both ObjectId and string formats
        pattern = None
        try:
            pattern = await db.rhythm_patterns.find_one({"_id": ObjectId(pattern_id)})
        except:
            pattern = await db.rhythm_patterns.find_one({"_id": pattern_id})
        
        if not pattern:
            logger.warning(f"Rhythm pattern not found with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Rhythm pattern with ID {pattern_id} not found"
            )
        
        # Convert to response model
        pattern_response = RhythmPatternResponse(**{**pattern, "id": str(pattern["_id"])})
        
        logger.info(f"Successfully retrieved rhythm pattern: {pattern_id}")
        return pattern_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rhythm pattern {pattern_id}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error while fetching rhythm pattern"
        )

async def update_rhythm_pattern_simple(
    pattern_id: str, 
    rhythm_pattern: RhythmPattern, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """
    Update an existing rhythm pattern using the simple route.
    
    Args:
        pattern_id (str): The unique identifier of the rhythm pattern to update
        rhythm_pattern (RhythmPattern): Updated rhythm pattern data
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        RhythmPatternResponse: The updated rhythm pattern
    
    Raises:
        HTTPException: For various validation and database-related errors
    """
    try:
        logger.info(f"Attempting to update rhythm pattern with ID: {pattern_id}")
        
        # Validate pattern with time signature
        RhythmPattern.validate_pattern_with_time_signature(rhythm_pattern)
        
        # Validate the pattern ID format
        if not pattern_id or not isinstance(pattern_id, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid ID format"
            )
        
        # Check if the rhythm pattern exists
        existing_pattern = await db.rhythm_patterns.find_one({"id": pattern_id})
        
        if not existing_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rhythm pattern with ID {pattern_id} not found"
            )
        
        # Prepare the update document
        update_data = rhythm_pattern.model_dump(by_alias=True)
        update_data['id'] = pattern_id  # Ensure ID remains the same
        
        # Update the rhythm pattern
        result = await db.rhythm_patterns.replace_one({"id": pattern_id}, update_data)
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update rhythm pattern"
            )
        
        # Retrieve the updated document
        updated_pattern = await db.rhythm_patterns.find_one({"id": pattern_id})
        
        # Convert to RhythmPatternResponse
        response = RhythmPatternResponse(**updated_pattern)
        
        logger.info(f"Successfully updated rhythm pattern: {response}")
        return response
    
    except ValidationError as ve:
        logger.error(f"Validation error updating rhythm pattern: {ve}")
        # Log the full validation error details
        for error in ve.errors():
            logger.error(f"Validation Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating rhythm pattern: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def delete_rhythm_pattern_simple(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> None:
    """
    Delete a specific rhythm pattern by its ID using the simple route.
    
    Args:
        pattern_id (str): The unique identifier of the rhythm pattern
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        None: Returns 204 No Content status on successful deletion
    
    Raises:
        HTTPException: If the pattern cannot be deleted
    """
    try:
        logger.info(f"Attempting to delete rhythm pattern: {pattern_id}")
        
        # Delete the pattern using the string ID directly
        delete_result = await db.rhythm_patterns.delete_one({"_id": pattern_id})
        
        if delete_result.deleted_count == 0:
            logger.warning(f"No rhythm pattern found to delete with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Rhythm pattern with ID {pattern_id} not found"
            )
        
        logger.info(f"Successfully deleted rhythm pattern: {pattern_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rhythm pattern {pattern_id}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during rhythm pattern deletion"
        )
