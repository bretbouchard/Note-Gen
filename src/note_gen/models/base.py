"""Base models for the application."""
from pydantic import BaseModel, ConfigDict

class BaseModelWithConfig(BaseModel):
    """Base model with standard configuration."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='forbid'
    )
