"""
Consolidated routes for rhythm pattern operations with improved error handling and logging.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
import uuid
from pydantic import ValidationError
import traceback
import sys
from datetime import datetime
import pymongo.errors
from bson import ObjectId, json_util
import pymongo

from src.note_gen.dependencies import get_db
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternResponse
from fastapi.encoders import jsonable_encoder

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all log levels

# Create console handler and set level to DEBUG
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add console handler to logger if not already added
if not logger.handlers:
    logger.addHandler(console_handler)

# Create a router with a specific prefix and tags
router = APIRouter(
    prefix="/api/v1/rhythm-patterns",
    tags=["rhythm-patterns"]
)

# Create a router with no prefix for backwards compatibility
simple_router = APIRouter(
    tags=["rhythm-patterns"],
    redirect_slashes=False
)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_rhythm_pattern(
    rhythm_pattern: RhythmPattern, 
    db: AsyncIOMotorDatabase = Depends(get_db)
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

@router.get("/", response_model=List[RhythmPatternResponse])
async def get_rhythm_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db)
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

@router.get("/{pattern_id}", response_model=RhythmPatternResponse)
async def get_rhythm_pattern(
    pattern_id: str, 
    db: AsyncIOMotorDatabase[str] = Depends(get_db)
) -> RhythmPatternResponse:
    """
    Retrieve a specific rhythm pattern by its ID.
    
    Args:
        pattern_id (str): The unique identifier of the rhythm pattern
        db (AsyncIOMotorDatabase[str]): Database connection
    
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

@router.put("/{pattern_id}", response_model=RhythmPatternResponse)
async def update_rhythm_pattern(
    pattern_id: str, 
    rhythm_pattern: RhythmPattern, 
    db: AsyncIOMotorDatabase = Depends(get_db)
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

@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rhythm_pattern(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
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

@simple_router.post("/rhythm-patterns", response_model=RhythmPatternResponse, status_code=status.HTTP_201_CREATED)
async def create_rhythm_pattern_simple(
    rhythm_pattern: RhythmPattern, 
    db: AsyncIOMotorDatabase = Depends(get_db)
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

@simple_router.get("/rhythm-patterns", response_model=List[RhythmPatternResponse])
async def get_rhythm_patterns_simple(
    db: AsyncIOMotorDatabase = Depends(get_db)
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

@simple_router.get("/rhythm-patterns/{pattern_id}", response_model=RhythmPatternResponse)
async def get_rhythm_pattern_simple(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
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

@simple_router.put("/rhythm-patterns/{pattern_id}", response_model=RhythmPatternResponse)
async def update_rhythm_pattern_simple(
    pattern_id: str, 
    rhythm_pattern: RhythmPattern, 
    db: AsyncIOMotorDatabase = Depends(get_db)
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

@simple_router.delete("/rhythm-patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rhythm_pattern_simple(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
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

# Register routes
router.post("", response_model=RhythmPatternResponse, status_code=status.HTTP_201_CREATED)(create_rhythm_pattern)
router.get("/", response_model=List[RhythmPatternResponse])(get_rhythm_patterns)
router.get("/{pattern_id}", response_model=RhythmPatternResponse)(get_rhythm_pattern)
router.put("/{pattern_id}", response_model=RhythmPatternResponse)(update_rhythm_pattern)
router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)(delete_rhythm_pattern)

# Register simple routes
simple_router.post("/rhythm-patterns", response_model=RhythmPatternResponse, status_code=status.HTTP_201_CREATED)(create_rhythm_pattern_simple)
simple_router.get("/rhythm-patterns", response_model=List[RhythmPatternResponse])(get_rhythm_patterns_simple)
simple_router.get("/rhythm-patterns/{pattern_id}", response_model=RhythmPatternResponse)(get_rhythm_pattern_simple)
simple_router.put("/rhythm-patterns/{pattern_id}", response_model=RhythmPatternResponse)(update_rhythm_pattern_simple)
simple_router.delete("/rhythm-patterns/{pattern_id}")(delete_rhythm_pattern_simple)
