from typing import Any
import pytest
from typeguard import TypeCheckError, typechecked
from src.note_gen.database.db import AsyncDBConnection, get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

@typechecked
def test_db_connection_types() -> None:
    """Test type safety of database connection objects."""
    async def check_db_types() -> None:
        async with AsyncDBConnection() as db:
            assert isinstance(db, AsyncIOMotorDatabase)
            # This should raise a TypeCheckError
            with pytest.raises(TypeCheckError):
                # @ts-ignore
                wrong_type: str = db  # type: ignore

    pytest.mark.asyncio(check_db_types)()

@typechecked
class TestTypeSafety:
    """Test suite for type safety checks."""
    
    @pytest.mark.asyncio
    async def test_db_connection_return_type(self) -> None:
        """Test that database connections return correct types."""
        async with get_db() as db:
            assert isinstance(db, AsyncIOMotorDatabase)
    
    def test_type_annotations_present(self) -> None:
        """Test that critical functions have type annotations."""
        import inspect
        from src.note_gen.database import db
        
        # Check all functions in the db module
        for name, obj in inspect.getmembers(db):
            if inspect.isfunction(obj):
                sig = inspect.signature(obj)
                # Check return annotation
                assert sig.return_annotation != inspect.Parameter.empty, \
                    f"Function {name} is missing return type annotation"
                # Check parameter annotations
                for param in sig.parameters.values():
                    assert param.annotation != inspect.Parameter.empty, \
                        f"Parameter {param.name} in function {name} is missing type annotation"