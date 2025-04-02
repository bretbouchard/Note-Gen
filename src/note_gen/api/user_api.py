from fastapi import APIRouter
from typing import Dict, List, Any

router = APIRouter()

@router.get("/")
async def get_users() -> Dict[str, List[Any]]:
    """Get all users."""
    return {"data": []}