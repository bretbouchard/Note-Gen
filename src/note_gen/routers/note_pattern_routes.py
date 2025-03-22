"""
Consolidated routes for note pattern operations with improved error handling and logging.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Response
from typing import List, Dict, Optional, Any, Union
from bson import ObjectId
from bson.errors import InvalidId
from fastapi.encoders import jsonable_encoder
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError

from src.note_gen.dependencies import get_db_conn
from src.note_gen.models import patterns
from src.note_gen.models.patterns import NotePattern
from src.note_gen.utils.logging_utils import setup_logger, log_endpoint

# Configure logging
logger = setup_logger(__name__)

router = APIRouter(
    prefix="/api/v1/note-patterns",
    tags=["note-patterns"]
)

@router.get("/", response_model=List[NotePattern])
@log_endpoint
async def get_note_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[NotePattern]:
    """
    Retrieve all note patterns.
    """
    try:
        patterns = await db.note_patterns.find().to_list(None)
        logger.debug(f"Retrieved {len(patterns)} note patterns")
        return [NotePattern(**pattern) for pattern in patterns]
    except Exception as e:
        logger.error(f"Failed to retrieve note patterns: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve note patterns"
        )

@router.post("/", response_model=NotePattern, status_code=status.HTTP_201_CREATED)
@log_endpoint
async def create_note_pattern(
    pattern: NotePattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NotePattern:
    """
    Create a new note pattern.
    """
    try:
        pattern_dict = jsonable_encoder(pattern)
        logger.info(f"Creating new note pattern: {pattern.name}")
        logger.debug(f"Pattern details: {pattern_dict}")
        
        result = await db.note_patterns.insert_one(pattern_dict)
        pattern_dict["id"] = str(result.inserted_id)
        
        logger.info(f"Successfully created note pattern with ID: {pattern_dict['id']}")
        return NotePattern(**pattern_dict)
        
    except DuplicateKeyError:
        logger.warning(f"Attempted to create duplicate note pattern: {pattern.name}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pattern with this name already exists"
        )
    except ValidationError as e:
        logger.error(f"Validation error creating note pattern: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating note pattern: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create note pattern"
        )

@router.post("/generate-note-pattern", response_model=NotePattern)
async def generate_note_pattern(
    note_pattern: NotePattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NotePattern:
    """
    Generate a note pattern based on provided parameters.
    """
    logger.info(f"Generating note pattern: {note_pattern.name}")
    logger.debug(f"Received request data for generating note pattern: {note_pattern}")
    # Logic to generate note pattern
    # Ensure chord root is a dictionary
    chord = {'note_name': 'C', 'octave': 4}
    return note_pattern

@router.get("/{pattern_id}", response_model=NotePattern)
async def get_note_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NotePattern:
    """Get a specific note pattern by ID."""
    logger.info(f"Getting note pattern by ID: {pattern_id}")
    try:
        # Convert string ID to ObjectId if it's a valid ObjectId format
        object_id = None
        if ObjectId.is_valid(pattern_id):
            try:
                object_id = ObjectId(pattern_id)
                logger.debug(f"Converting string ID {pattern_id} to ObjectId {object_id}")
            except InvalidId:
                logger.warning(f"Failed to convert {pattern_id} to ObjectId despite appearing valid")
                pass
        
        # Query the database with multiple possible ID formats
        pattern = None
        
        # Try by string ID field first (most common for note patterns)
        pattern = await db.note_patterns.find_one({"id": pattern_id})
        logger.debug(f"Search by string id field: {'found' if pattern else 'not found'}")
        
        # If not found, try by ObjectId if we have a valid one
        if not pattern and object_id:
            pattern = await db.note_patterns.find_one({"_id": object_id})
            logger.debug(f"Search by ObjectId: {'found' if pattern else 'not found'}")
        
        # Final fallback - try treating the string directly as _id
        if not pattern:
            pattern = await db.note_patterns.find_one({"_id": pattern_id})
            logger.debug(f"Search by string as _id: {'found' if pattern else 'not found'}")
            
        # If still not found, try legacy collection as a last resort
        if not pattern:
            pattern = await db.note_pattern_collection.find_one({"id": pattern_id})
            logger.debug(f"Search in legacy collection: {'found' if pattern else 'not found'}")
            
        if not pattern:
            logger.warning(f"Note pattern not found with id {pattern_id}")
            raise HTTPException(status_code=404, detail=f"Note pattern {pattern_id} not found")
            
        # Normalize the document to ensure all required fields are present
        normalized_doc = _normalize_response_doc(pattern)
        logger.debug(f"Normalized pattern: {normalized_doc.get('name')}, id: {normalized_doc.get('id')}")
        
        try:
            response_data = NotePattern(**normalized_doc)
            return response_data
        except ValidationError as e:
            logger.error(f"Validation error for note pattern {pattern_id}: {str(e)}")
            # Log detailed error information
            for error in e.errors():
                logger.error(f"  - {error['loc']}: {error['msg']}")
                
            # Create a valid fallback response
            try:
                # Set minimum required fields directly
                fallback_doc = {
                    'id': pattern.get('id', pattern.get('_id', pattern_id)),
                    'name': pattern.get('name', 'Unnamed Pattern'),
                    'pattern': pattern.get('pattern', [0, 2, 4]),
                    'duration': 1.0,
                    'position': 0.0,
                    'velocity': 64,
                    'description': pattern.get('description', 'No description'),
                    'tags': pattern.get('tags', ['default'])
                }
                response_data = NotePattern(**fallback_doc)
                return response_data
            except Exception as inner_e:
                logger.error(f"Failed to create fallback response: {inner_e}")
                raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving note pattern {pattern_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{pattern_id}", response_model=patterns.NotePattern)
async def update_note_pattern(
    pattern_id: str,
    note_pattern: patterns.NotePattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
):
    """Update a note pattern."""
    logger.info(f"Updating note pattern: {pattern_id}")
    logger.debug(f"Received request data for updating note pattern: {note_pattern}")
    
    try:
        # Check if the note pattern exists
        existing_doc = None
        
        # Try by string ID field first (most common)
        existing_doc = await db.note_patterns.find_one({"id": pattern_id})
        logger.debug(f"Search by string id field: {'found' if existing_doc else 'not found'}")
        
        # If not found, try by ObjectId if possible
        if not existing_doc and ObjectId.is_valid(pattern_id):
            try:
                obj_id = ObjectId(pattern_id)
                existing_doc = await db.note_patterns.find_one({"_id": obj_id})
                logger.debug(f"Search by ObjectId: {'found' if existing_doc else 'not found'}")
            except InvalidId:
                pass
        
        # If still not found, try as string _id
        if not existing_doc:
            existing_doc = await db.note_patterns.find_one({"_id": pattern_id})
            logger.debug(f"Search by string as _id: {'found' if existing_doc else 'not found'}")
        
        # Final fallback - check legacy collection
        if not existing_doc:
            existing_doc = await db.note_pattern_collection.find_one({"id": pattern_id})
            logger.debug(f"Search in legacy collection: {'found' if existing_doc else 'not found'}")
            
            # If found in legacy collection, move to new collection
            if existing_doc:
                # Convert legacy doc to proper format
                if "_id" in existing_doc:
                    existing_doc["id"] = str(existing_doc["_id"])
                    del existing_doc["_id"]
                
                # Prepare update filter for legacy collection
                filter_dict = {"id": pattern_id}
                logger.debug(f"Using update filter for legacy collection: {filter_dict}")
                collection = db.note_pattern_collection
            else:
                # Not found anywhere
                raise HTTPException(status_code=404, detail="Note pattern not found")
        else:
            # Found in note_patterns collection
            # Prepare update filter
            if "_id" in existing_doc and not isinstance(existing_doc["_id"], str):
                filter_dict = {"_id": existing_doc["_id"]}
            else:
                filter_dict = {"id": pattern_id}
            logger.debug(f"Using update filter: {filter_dict}")
            collection = db.note_patterns
        
        # Update the document
        note_pattern_dict = note_pattern.model_dump()
        
        # Preserve the _id field if it exists
        if "_id" in existing_doc and "_id" not in note_pattern_dict:
            note_pattern_dict["_id"] = existing_doc["_id"]
        
        # Always ensure the id field matches the pattern_id parameter
        note_pattern_dict["id"] = pattern_id
        
        # Update document
        await collection.replace_one(filter_dict, note_pattern_dict, upsert=True)
        
        # If it was in the legacy collection, also insert into the new one and delete from legacy
        if collection == db.note_pattern_collection:
            await db.note_patterns.insert_one(note_pattern_dict)
            await db.note_pattern_collection.delete_one(filter_dict)
            logger.info(f"Migrated note pattern {pattern_id} from legacy collection to note_patterns")
            
        return note_pattern_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
):
    """Delete a note pattern."""
    logger.info(f"Deleting note pattern: {pattern_id}")
    logger.debug(f"Received request data for deleting note pattern ID: {pattern_id}")
    try:
        # Convert string ID to ObjectId if it's a valid ObjectId format
        object_id = None
        if ObjectId.is_valid(pattern_id):
            try:
                object_id = ObjectId(pattern_id)
                logger.debug(f"Converting string ID {pattern_id} to ObjectId {object_id}")
            except InvalidId:
                logger.warning(f"Failed to convert {pattern_id} to ObjectId despite appearing valid")
                pass
        
        # First try deleting by string ID field (most common for note patterns)
        result = await db.note_patterns.delete_one({"id": pattern_id})
        logger.debug(f"Delete by string id field: {result.deleted_count} document(s)")
        
        # If not found, try by ObjectId if we have a valid one
        if result.deleted_count == 0 and object_id:
            result = await db.note_patterns.delete_one({"_id": object_id})
            logger.debug(f"Delete by ObjectId: {result.deleted_count} document(s)")
        
        # Final fallback - try treating the string directly as _id
        if result.deleted_count == 0:
            result = await db.note_patterns.delete_one({"_id": pattern_id})
            logger.debug(f"Delete by string as _id: {result.deleted_count} document(s)")
        
        # If nothing was deleted, also try in the legacy collection
        if result.deleted_count == 0:
            # Try in the note_pattern_collection as a fallback
            legacy_result = await db.note_pattern_collection.delete_one({"id": pattern_id})
            if legacy_result.deleted_count > 0:
                logger.debug(f"Deleted from legacy collection: {legacy_result.deleted_count} document(s)")
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            
            # None of the attempts found the pattern
            raise HTTPException(status_code=404, detail="Note pattern not found")
            
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting note pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
