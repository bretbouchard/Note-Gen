from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class Migration(ABC):
    """Base class for database migrations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.version: str = self.__class__.__name__
    
    @abstractmethod
    async def up(self) -> None:
        """Upgrade database to this version."""
        pass
    
    @abstractmethod
    async def down(self) -> None:
        """Downgrade database from this version."""
        pass
    
    async def record_migration(self, direction: str) -> None:
        """Record migration execution."""
        migration_doc = {
            "version": self.version,
            "direction": direction,
            "executed_at": datetime.utcnow()
        }
        await self.db.migrations.insert_one(migration_doc)