"""Configuration settings for the application."""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    # Database settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_test_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "note_gen"
    mongodb_test_db: str = "note_gen_test"
    
    # Additional MongoDB settings
    mongodb_uri: Optional[str] = None
    mongodb_test_uri: Optional[str] = None
    database_name: Optional[str] = None

    # Test settings
    testing: Optional[str] = None
    clear_db_after_tests: Optional[str] = "0"
    pythonpath: Optional[str] = "src"

    class Config:
        """Pydantic config."""
        env_file = ".env"
        extra = "allow"  # Allow extra fields from environment variables

@lru_cache()
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

# Export the settings instance
settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
