from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any


async def get_db_conn() -> AsyncIOMotorDatabase[Dict[str, Any]]: ...