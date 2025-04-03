"""
Database configuration settings.
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Original uppercase fields
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "test_note_gen" if os.getenv("TESTING", "0") == "1" else "note_gen"

    # Additional fields from .env
    TESTING: str = "0"
    MONGODB_TEST_URI: str = "mongodb://localhost:27017/test_note_gen"
    MONGODB_URI: str = "mongodb://localhost:27017/note_gen"
    DATABASE_NAME: str = "note_gen"
    CLEAR_DB_AFTER_TESTS: str = "0"
    PYTHONPATH: str = "src"

    # Lowercase aliases for test compatibility
    @property
    def mongodb_url(self) -> str:
        return self.MONGODB_URI

    @property
    def mongodb_test_uri(self) -> str:
        return self.MONGODB_TEST_URI

    @property
    def mongodb_uri(self) -> str:
        return self.MONGODB_URI

    @property
    def database_name(self) -> str:
        return self.DATABASE_NAME

    @property
    def test_mongodb_database(self) -> str:
        return "test_note_gen"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from environment variables

settings = Settings()
