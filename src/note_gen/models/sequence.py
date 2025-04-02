"""Models for sequences."""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from bson import ObjectId

class Sequence(BaseModel):
    """Base model for sequences."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
        validate_assignment=True
    )

    id: str = Field(default="", description="Unique identifier")
    name: str = Field(default="", description="Name of the sequence")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def to_dict(self) -> Dict[str, Any]:
        """Convert sequence to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "metadata": self.metadata
        }

    def clone(self) -> 'Sequence':
        """Create a deep copy of the sequence."""
        return self.__class__(**self.model_dump())
