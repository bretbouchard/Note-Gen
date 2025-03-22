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
            raise DBValidationError(f"Document validation failed: {str(e)}")
    
    @staticmethod
    def validate_update(model_class: Type[T], update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update operations."""
        # Validate each field in update operations
        for operator, fields in update_data.items():
            if operator.startswith('$'):
                for field, value in fields.items():
                    try:
                        # Create a partial model with just this field
                        model_class(**{field: value})
                    except ValidationError as e:
                        raise DBValidationError(
                            f"Invalid update operation {operator} for field {field}: {str(e)}"
                        )
        return update_data