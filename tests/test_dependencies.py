"""Tests for the dependencies module."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from note_gen.dependencies import (
    get_validation_controller,
    get_import_export_controller,
    get_utility_controller
)


@pytest.mark.asyncio
async def test_get_validation_controller():
    """Test get_validation_controller dependency."""
    with patch('note_gen.dependencies.ValidationController') as mock_controller_class:
        # Setup mock
        mock_controller = MagicMock()
        mock_controller_class.create = AsyncMock(return_value=mock_controller)

        # Call the dependency
        result = await get_validation_controller()

        # Verify
        assert result == mock_controller
        mock_controller_class.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_import_export_controller():
    """Test get_import_export_controller dependency."""
    with patch('note_gen.dependencies.ImportExportController') as mock_controller_class:
        # Setup mock
        mock_controller = MagicMock()
        mock_controller_class.create = AsyncMock(return_value=mock_controller)

        # Call the dependency
        result = await get_import_export_controller()

        # Verify
        assert result == mock_controller
        mock_controller_class.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_utility_controller():
    """Test get_utility_controller dependency."""
    with patch('note_gen.dependencies.UtilityController') as mock_controller_class:
        # Setup mock
        mock_controller = MagicMock()
        mock_controller_class.create = AsyncMock(return_value=mock_controller)

        # Call the dependency
        result = await get_utility_controller()

        # Verify
        assert result == mock_controller
        mock_controller_class.create.assert_called_once()
