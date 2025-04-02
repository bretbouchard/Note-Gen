from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str

router = APIRouter()

@router.get("/")
async def get_users():
    """Get all users."""
    try:
        return {"users": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_user(user: User):
    """Create a new user."""
    try:
        return {"user_id": "new_user"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))