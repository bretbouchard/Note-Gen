from typing import Any, Dict
from pydantic import BaseModel, ConfigDict

class BaseModelWithConfig(BaseModel):
    """Base model with common configuration for all music models"""
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra='forbid',
        from_attributes=True,  # replaces orm_mode
        populate_by_name=True
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.model_dump()