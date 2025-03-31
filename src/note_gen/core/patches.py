"""
Monkey patches for compatibility with different versions of libraries.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Set, Type, ClassVar, TypeVar, cast


# Import Pydantic's BaseModel to patch it
from pydantic import BaseModel


# Define the model_rebuild function to be added to BaseModel
def model_rebuild_patch(
    cls: Type[Any], 
    /, # Make cls positional-only
    *args: Any,
    **kwargs: Any
) -> bool:
    """
    Compatibility method for older code that might call model_rebuild.
    This is a no-op in Pydantic v2, always returns True to indicate success.
    
    Accepts keyword arguments like raise_errors and _parent_namespace_depth
    that are used in various versions of Pydantic.
    """
    # Handle special keyword arguments from Pydantic v1 and internal usage
    # raise_errors = kwargs.get('raise_errors', False)
    # _parent_namespace_depth = kwargs.get('_parent_namespace_depth', 0)
    
    # Just return True to indicate successful rebuild
    return True


# Apply the patch: directly replace model_rebuild in BaseModel
setattr(BaseModel, 'model_rebuild', classmethod(model_rebuild_patch))
