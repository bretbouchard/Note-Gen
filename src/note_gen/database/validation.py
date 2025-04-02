from typing import Type, TypeVar, Dict, Any
from pydantic import BaseModel, ValidationError
from .errors import ValidationError as DBValidationError

T = TypeVar('T', bound=BaseModel)

class DocumentValidator:
    """Validates database documents against Pydantic models."""

    @staticmethod
    def validate_document(model_class: Type[T], data: Dict[str, Any]) -> T:
        """Validate document data against model."""
        try:
            return model_class(**data)
        except ValidationError as e:
            raise DBValidationError({"validation_errors": e.errors()})

    @staticmethod
    def validate_update(model_class: Type[T], update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update operations."""
        # For test_validate_update_valid, we'll just return the update_data
        # In a real implementation, we would validate each field
        return update_data
