"""Database configuration."""

from typing import Optional
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 27017
    database: str = "note_gen_db_dev"  # Changed from "test_db"
    username: Optional[str] = None
    password: Optional[str] = None

    def get_connection_url(self) -> str:
        """Get the MongoDB connection URL."""
        if self.username and self.password:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"mongodb://{self.host}:{self.port}"
