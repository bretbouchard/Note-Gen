from typing import List, Type
from motor.motor_asyncio import AsyncIOMotorDatabase
from .base import Migration
import logging

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.migrations: List[Type[Migration]] = []
    
    def register_migration(self, migration_class: Type[Migration]) -> None:
        """Register a new migration."""
        self.migrations.append(migration_class)
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        cursor = self.db.migrations.find().sort("executed_at", 1)
        return [doc["version"] for doc in await cursor.to_list(length=None)]
    
    async def migrate(self) -> None:
        """Apply all pending migrations."""
        applied = await self.get_applied_migrations()
        
        for migration_class in sorted(self.migrations, key=lambda x: x.__name__):
            if migration_class.__name__ not in applied:
                migration = migration_class(self.db)
                logger.info(f"Applying migration: {migration.version}")
                await migration.up()
                await migration.record_migration("up")
    
    async def rollback(self, steps: int = 1) -> None:
        """Rollback the last n migrations."""
        applied = await self.get_applied_migrations()
        
        for migration_class in sorted(self.migrations, key=lambda x: x.__name__, reverse=True)[:steps]:
            if migration_class.__name__ in applied:
                migration = migration_class(self.db)
                logger.info(f"Rolling back migration: {migration.version}")
                await migration.down()
                await self.db.migrations.delete_one({"version": migration.version})