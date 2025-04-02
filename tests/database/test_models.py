"""Test models for database tests."""
from typing import Dict, Any


class DBTestModel:
    """Test model for repository tests."""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def model_dump(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {"name": self.name, "value": self.value}

    @classmethod
    def model_validate(cls, data: Dict[str, Any]) -> 'DBTestModel':
        """Create a model instance from dictionary data."""
        return cls(name=data.get("name", ""), value=data.get("value", 0))
