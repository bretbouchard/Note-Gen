"""
Dependencies for FastAPI.

This module provides dependency injection functions for FastAPI.
"""

from note_gen.controllers.validation_controller import ValidationController
from note_gen.controllers.import_export_controller import ImportExportController
from note_gen.controllers.utility_controller import UtilityController


async def get_validation_controller():
    """
    Get a validation controller instance.
    
    Returns:
        ValidationController: A validation controller instance
    """
    return await ValidationController.create()


async def get_import_export_controller():
    """
    Get an import/export controller instance.
    
    Returns:
        ImportExportController: An import/export controller instance
    """
    return await ImportExportController.create()


async def get_utility_controller():
    """
    Get a utility controller instance.
    
    Returns:
        UtilityController: A utility controller instance
    """
    return await UtilityController.create()
