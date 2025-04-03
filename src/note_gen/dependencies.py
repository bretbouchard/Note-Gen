"""
Dependencies for FastAPI.

This module provides dependency injection functions for FastAPI.
"""

from note_gen.controllers.validation_controller import ValidationController
from note_gen.controllers.import_export_controller import ImportExportController
from note_gen.controllers.utility_controller import UtilityController
from note_gen.controllers.pattern_controller import PatternController
from note_gen.database.repositories.note_pattern_repository import NotePatternRepository
from note_gen.database.repositories.rhythm_pattern_repository import RhythmPatternRepository
from note_gen.database.db import get_db_conn


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


async def get_pattern_controller():
    """
    Get a pattern controller instance.

    Returns:
        PatternController: A pattern controller instance
    """
    # Get database connection
    db = await get_db_conn()

    # Create repositories
    note_pattern_repository = NotePatternRepository(db.note_patterns)
    rhythm_pattern_repository = RhythmPatternRepository(db.rhythm_patterns)

    # Create controller
    return PatternController(
        note_pattern_repository=note_pattern_repository,
        rhythm_pattern_repository=rhythm_pattern_repository
    )
