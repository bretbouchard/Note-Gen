"""
src/note_gen/routers/user_routes.py

User-related route handlers.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from src.note_gen.models.user import User
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.dependencies import get_db_conn
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/me")
async def get_current_user():
    """Get the current user."""
    return {"username": "testuser"}

@router.get("/", response_model=List[User])
async def get_users(db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Get all users."""
    cursor = db.users.find({})
    return await cursor.to_list(length=100)

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Get a specific user by ID."""
    user = await db.users.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=User, status_code=201)
async def create_user(user: User, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Create a new user."""
    result = await db.users.insert_one(user.dict())
    user.id = str(result.inserted_id)
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Delete a user."""
    result = await db.users.delete_one({"_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")